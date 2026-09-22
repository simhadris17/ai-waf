import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.database import SessionLocal
from app.models import RequestLog
from app.ml.detector import detector
from app.websocket_manager import manager

logger = logging.getLogger("ai-waf.middleware")

# Paths the WAF itself should never inspect/block (health checks, docs, the
# dashboard's own API/websocket plumbing) to avoid self-inflicted lockouts.
EXCLUDED_PREFIXES = ("/health", "/docs", "/openapi.json", "/ws", "/api/auth", "/api/logs", "/api/simulate", "/favicon")


class WAFMiddleware(BaseHTTPMiddleware):
    """Inspects every inbound request, classifies it, logs it, and blocks
    high-confidence attacks with a 403 before they reach the route handler."""

    async def dispatch(self, request, call_next):
        path = request.url.path

        # The root endpoint is a health/status response, not user-controlled
        # application traffic. Match it exactly so other routes remain
        # protected.
        if path == "/" or any(path.startswith(p) for p in EXCLUDED_PREFIXES):
            return await call_next(request)

        payload = f"{path}?{request.url.query}" if request.url.query else path
        label, confidence, attack_type = detector.predict(payload)
        blocked = label == "ATTACK"

        client_ip = request.client.host if request.client else None
        method = request.method

        self._persist(client_ip, method, payload, label, confidence, blocked)
        self._broadcast(client_ip, method, payload, label, confidence, blocked, attack_type)

        if blocked:
            logger.warning("Blocked request: %s (confidence=%.2f)", payload, confidence)
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Request blocked by AI-WAF",
                    "label": label,
                    "confidence": confidence,
                    "attack_type": attack_type,
                },
            )

        return await call_next(request)

    def _persist(self, client_ip, method, payload, label, confidence, blocked):
        db = SessionLocal()
        try:
            entry = RequestLog(
                client_ip=client_ip,
                method=method,
                path=payload,
                label=label,
                confidence=confidence,
                blocked=int(blocked),
            )
            db.add(entry)
            db.commit()
        except Exception:
            logger.exception("Failed to persist request log")
            db.rollback()
        finally:
            db.close()

    def _broadcast(self, client_ip, method, payload, label, confidence, blocked, attack_type):
        """Fire-and-forget WebSocket broadcast. Uses get_event_loop() which is
        safe inside an ASGI app running under Uvicorn's event loop."""
        import asyncio

        data = {
            "path": payload,
            "label": label,
            "confidence": confidence,
            "blocked": blocked,
            "client_ip": client_ip,
            "method": method,
            "attack_type": attack_type,
        }

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast(data))
        except RuntimeError:
            pass

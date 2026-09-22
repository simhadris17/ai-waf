from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query

from app.config import get_settings
from app.websocket_manager import manager

router = APIRouter()

settings = get_settings()


@router.websocket("/ws/live")
async def live_feed(websocket: WebSocket, token: str | None = Query(default=None)):
    """Live event stream. Requires a valid JWT passed as ?token=<access_token>."""
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    from jose import JWTError, jwt

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("sub") is None:
            raise ValueError("No subject in token")
    except (JWTError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        while True:
            # We don't expect inbound messages, but reading keeps the
            # connection alive and lets us detect disconnects promptly.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

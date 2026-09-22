import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_logs, routes_simulate, routes_ws
from app.config import get_settings
from app.database import Base, engine
from app.middleware.waf_middleware import WAFMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ai-waf")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="AI-powered Web Application Firewall with real-time threat dashboard.",
    version="1.0.0",
)

# Create all tables on startup.
# For production migrations, replace with Alembic.
Base.metadata.create_all(bind=engine)

# CORS — allow configured frontend origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WAF middleware inspects every request.
app.add_middleware(WAFMiddleware)

# Routers
app.include_router(routes_auth.router)
app.include_router(routes_logs.router)
app.include_router(routes_simulate.router)
app.include_router(routes_ws.router)


@app.get("/health", tags=["health"])
def health():
    """Simple liveness probe for Render / Docker health checks."""
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/", tags=["health"])
def root():
    return {"status": "AI-WAF running", "env": settings.ENV}


# ---- Demo routes — simulates a real app sitting behind the WAF ----
@app.get("/login", tags=["demo"])
def demo_login(user: str = "guest"):
    return {"user": user}


@app.get("/search", tags=["demo"])
def demo_search(q: str = ""):
    return {"results_for": q}

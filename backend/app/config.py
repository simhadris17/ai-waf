"""
Centralized application configuration.
All values are read from environment variables (see .env.example),
so nothing environment-specific is hardcoded in source.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "AI-WAF"
    ENV: str = "development"
    DEBUG: bool = False

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me"

    # Database — defaults to SQLite for local dev; override via DATABASE_URL env var.
    # Render/Heroku: set DATABASE_URL to your Postgres connection string.
    DATABASE_URL: str = "sqlite:///./ai_waf.db"

    # ML model — set to path of trained model dir; falls back to keyword detection
    MODEL_DIR: str = "./model/final"
    ATTACK_CONFIDENCE_THRESHOLD: float = 0.75
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""

    # CORS — comma-separated list of allowed frontend origins
    # Include your Vercel URL here once deployed, e.g.:
    #   ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
    ALLOWED_ORIGINS: str = "http://localhost:5174,http://localhost:5174,http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

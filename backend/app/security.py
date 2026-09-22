"""
Security helpers — JWT creation/validation and password hashing.
The auth flow is:
  1. POST /api/auth/register  → creates user row with hashed password
  2. POST /api/auth/login     → verifies password, returns JWT
  3. Every protected route    → FastAPI's Depends(get_current_user) validates JWT
"""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.config import get_settings

settings = get_settings()

# OAuth2 scheme — tells FastAPI/Swagger where to get the token from.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Use the recommended (Argon2) algorithm for password hashing.
password_hash = PasswordHash.recommended()


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return an Argon2-hashed version of the plain-text password."""
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    return password_hash.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(subject: str) -> str:
    """Create a signed JWT for *subject* (username) valid for the configured duration."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """FastAPI dependency — decode JWT and return the username.

    Raises HTTP 401 if the token is missing, expired, or tampered with.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            raise credentials_exc
        return username
    except JWTError:
        raise credentials_exc

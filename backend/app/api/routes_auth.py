from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginIn, RegisterIn, Token, UserOut
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    """Create a new user account. Returns 409 if username or email already taken."""
    username = payload.username.strip()
    email = payload.email.strip().lower()

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    """Verify credentials and return a JWT bearer token."""
    user = (
        db.query(User)
        .filter(User.username == payload.username.strip())
        .first()
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return Token(access_token=create_access_token(subject=user.username))


@router.get("/me", response_model=UserOut)
def me(
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the profile of the currently authenticated user."""
    user = (
        db.query(User)
        .filter(User.username == current_username)
        .first()
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user

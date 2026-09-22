from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LogOut(BaseModel):
    id: int
    created_at: datetime
    client_ip: str | None
    method: str | None
    path: str
    label: str
    confidence: float
    blocked: int

    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    total: int
    safe: int
    attack: int
    blocked: int
    avg_confidence: float


class SimulateIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class SimulateOut(BaseModel):
    text: str
    label: str
    confidence: float
    attack_type: str | None = None  # 'keyword' | 'ml' | None


class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginIn(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

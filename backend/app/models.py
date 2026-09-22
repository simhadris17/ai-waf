from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func

from app.database import Base


class RequestLog(Base):
    """One row per HTTP request inspected by the WAF middleware."""

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    client_ip = Column(String(64), nullable=True)
    method = Column(String(10), nullable=True)
    path = Column(Text, nullable=False)
    label = Column(String(16), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    blocked = Column(Integer, default=0)


class User(Base):
    """Application user account."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

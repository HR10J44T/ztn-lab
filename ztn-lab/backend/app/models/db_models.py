from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)


class AccessEvent(Base):
    __tablename__ = "access_events"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    role = Column(String(30), nullable=False)
    resource = Column(String(120), nullable=False)
    action = Column(String(30), nullable=False)
    resource_segment = Column(String(50), nullable=False)
    device_trust = Column(String(30), nullable=False)
    location = Column(String(30), nullable=False)
    ip_address = Column(String(64), nullable=False)
    decision = Column(String(10), nullable=False)
    reason = Column(Text, nullable=False)
    policy_name = Column(String(80), nullable=False)
    risk_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

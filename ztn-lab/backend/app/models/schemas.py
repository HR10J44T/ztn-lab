from datetime import datetime
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class AccessRequest(BaseModel):
    resource: str = Field(..., examples=["/zones/admin"])
    action: str = Field(default="read", examples=["read"])
    device_trust: str = Field(default="managed", examples=["trusted", "unknown"])
    location: str = Field(default="remote", examples=["corporate", "remote", "foreign"])
    ip_address: str = Field(default="127.0.0.1")


class AccessDecision(BaseModel):
    decision: str
    resource_segment: str
    risk_score: int
    reason: str
    policy: str
    explanation: str


class EventOut(BaseModel):
    id: int
    username: str
    role: str
    resource: str
    action: str
    resource_segment: str
    device_trust: str
    location: str
    ip_address: str
    decision: str
    reason: str
    policy_name: str
    risk_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsOut(BaseModel):
    total_events: int
    allowed: int
    denied: int
    average_risk: float
    high_risk_events: int

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine, get_db
from app.models.db_models import AccessEvent, User
from app.models.schemas import AccessDecision, AccessRequest, EventOut, LoginRequest, MetricsOut, TokenResponse
from app.services.auth import authenticate_user, create_access_token
from app.services.bootstrap import seed_users
from app.services.policy_engine import evaluate_access

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": settings.app_name, "status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user.username)
    return TokenResponse(access_token=token)


@app.post("/access/evaluate", response_model=AccessDecision)
def evaluate(payload: AccessRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    decision = evaluate_access(
        role=current_user.role,
        resource=payload.resource,
        action=payload.action,
        device_trust=payload.device_trust,
        location=payload.location,
    )

    event = AccessEvent(
        username=current_user.username,
        role=current_user.role,
        resource=payload.resource,
        action=payload.action,
        resource_segment=decision.resource_segment,
        device_trust=payload.device_trust,
        location=payload.location,
        ip_address=payload.ip_address,
        decision=decision.decision,
        reason=decision.reason,
        policy_name=decision.policy,
        risk_score=decision.risk_score,
    )
    db.add(event)
    db.commit()

    return AccessDecision(
        decision=decision.decision,
        resource_segment=decision.resource_segment,
        risk_score=decision.risk_score,
        reason=decision.reason,
        policy=decision.policy,
        explanation=decision.explanation,
    )


@app.get("/events", response_model=list[EventOut])
def list_events(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AccessEvent).order_by(AccessEvent.created_at.desc()).limit(limit).all()


@app.get("/metrics", response_model=MetricsOut)
def metrics(db: Session = Depends(get_db)):
    total_events = db.query(func.count(AccessEvent.id)).scalar() or 0
    allowed = db.query(func.count(AccessEvent.id)).filter(AccessEvent.decision == "allow").scalar() or 0
    denied = db.query(func.count(AccessEvent.id)).filter(AccessEvent.decision == "deny").scalar() or 0
    average_risk = db.query(func.avg(AccessEvent.risk_score)).scalar() or 0.0
    high_risk_events = db.query(func.count(AccessEvent.id)).filter(AccessEvent.risk_score >= 70).scalar() or 0
    return MetricsOut(
        total_events=total_events,
        allowed=allowed,
        denied=denied,
        average_risk=round(float(average_risk), 2),
        high_risk_events=high_risk_events,
    )


@app.get("/users/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

from sqlalchemy.orm import Session
from app.models.db_models import User
from app.services.auth import get_password_hash


SEED_USERS = [
    {"username": "admin_user", "full_name": "Admin User", "role": "admin", "password": "Admin@123"},
    {"username": "dev_user", "full_name": "Developer User", "role": "developer", "password": "Dev@123"},
    {"username": "analyst_user", "full_name": "Analyst User", "role": "analyst", "password": "Analyst@123"},
    {"username": "guest_user", "full_name": "Guest User", "role": "guest", "password": "Guest@123"},
]


def seed_users(db: Session) -> None:
    for item in SEED_USERS:
        exists = db.query(User).filter(User.username == item["username"]).first()
        if exists:
            continue
        db.add(User(
            username=item["username"],
            full_name=item["full_name"],
            role=item["role"],
            hashed_password=get_password_hash(item["password"]),
        ))
    db.commit()

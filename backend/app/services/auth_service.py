from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.core.security.password import (
    hash_password,
    verify_password,
)
from backend.app.core.security.token import create_access_token
from backend.app.schemas.auth import RegisterRequest


def register_user(db: Session, data: RegisterRequest) -> User:
    email = data.email.lower().strip()

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(db: Session, email: str, password: str) -> dict:
    normalized_email = email.lower().strip()

    user = db.query(User).filter(
        User.email == normalized_email
    ).first()

    if not user or not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError("Invalid email or password")

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
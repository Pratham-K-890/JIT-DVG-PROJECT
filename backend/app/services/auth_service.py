from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth import LoginRequest, SignupRequest
from app.core.security import create_access_token, hash_password, verify_password
from app.infrastructure.orm_models import User


def signup(db: Session, req: SignupRequest) -> User:
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(name=req.name, email=req.email, password_hash=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, req: LoginRequest) -> str:
    """Returns a signed JWT access token if credentials are valid."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    return create_access_token(subject=str(user.id))

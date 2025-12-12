# app/services/user_service.py

from sqlmodel import Session, select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.database.models import User

# Password Hashing Tool
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def create_user(session: Session, user_data: dict) -> User:
    email = user_data["email"]
    password = user_data["password"]
    role = user_data["role"]
    full_name = user_data["full_name"]

    # 1. Validate Email Domain
    if not email.endswith("@knagent.com"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: Only @knagent.com emails are allowed."
        )

    # 2. Check if user already exists
    if get_user_by_email(session, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # 3. Hash the password
    hashed_password = pwd_context.hash(password)

    # 4. Save to DB
    new_user = User(
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=hashed_password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user
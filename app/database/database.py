# app/database/database.py

from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from app.core.config import settings

# --- Database Setup ---
# The URL is loaded securely from app/core/config.py
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=True) # echo=True for dev logging

def create_db_and_tables():
    """Initializes the database schema based on SQLModel definitions."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency injector for database sessions.
    Provides a session and ensures it is closed after the request is complete.
    """
    with Session(engine) as session:
        yield session
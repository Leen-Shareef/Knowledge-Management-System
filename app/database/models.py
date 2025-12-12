# app/database/models.py

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ConversationHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    session_id: str
    message_content: str
    sender: str  # "user" or "agent"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- NEW USER MODEL ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True) # Username will be the email
    full_name: str
    hashed_password: str
    role: str # HR_Employee, IT_Tech, etc.
    disabled: bool = Field(default=False)


class UnansweredQuery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    user_role: str
    question: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LeaveRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    start_date: str
    end_date: str
    reason: str
    status: str = "Pending" # Default status
    timestamp: datetime = Field(default_factory=datetime.utcnow)
# app/services/memory_service.py

from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from datetime import datetime

# Import database components
from app.database.models import ConversationHistory
# Removed unused import of ConversationHistoryBase
# Removed unused import of get_session

# --- Helper function for session ID generation ---
def get_or_create_session_id(session_id: Optional[str] = None) -> str:
    """Returns a provided session ID or generates a new one."""
    # Note: Added 'Optional' to the function signature for clarity
    return session_id if session_id else str(uuid4())

# --- Core memory functions ---

def save_message(
    session: Session, 
    user_id: str, 
    session_id: str, 
    sender: str, 
    content: str
):
    """Saves a single message (user query or agent response) to the database."""
    message = ConversationHistory(
        user_id=user_id,
        session_id=session_id,
        sender=sender,
        message_content=content
    )
    session.add(message)
    session.commit()
    # No need for session.refresh here unless we needed the new message ID
    # print(f"[DB] Saved message from {sender} in session {session_id}")


def load_message_history(session: Session, session_id: str) -> List[dict]:
    """Retrieves all messages for a specific session ID, ordered by timestamp."""
    
    # Query the database for all history matching the session_id
    history_records = session.query(ConversationHistory).filter(
        ConversationHistory.session_id == session_id
    ).order_by(ConversationHistory.timestamp).all()
    
    # Format the messages into a list of dictionaries as required by LangChain's memory classes
    formatted_history = []
    for record in history_records:
        # LangChain memory usually expects messages in a 'role' (human/ai) and 'content' format
        role = "human" if record.sender == "user" else "ai"
        formatted_history.append({
            "role": role,
            "content": record.message_content
        })
        
    return formatted_history
# app/api/v1/agent_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime

# --- IMPORTS ---
# Replaced 'create_rag_chain' with 'create_agent_system' for Tool Usage
from rag_pipeline.agent_setup import create_agent_system 
from app.database.database import get_session
from app.services.memory_service import save_message, get_or_create_session_id, load_message_history
from app.core.security import get_current_user_role
from app.database.models import ConversationHistory, UnansweredQuery
from app.core.limiter import limiter

# --- SCHEMAS ---
class QueryRequest(BaseModel):
    """Schema for the incoming chat query request."""
    question: str = Field(..., description="The user's query.")
    session_id: Optional[str] = Field(None, description="Current chat session ID.")

class QueryResponse(BaseModel):
    answer: str
    session_id: str

class SessionInfo(BaseModel):
    """Schema for the sidebar session list."""
    session_id: str
    preview: str
    timestamp: datetime

# --- ROUTER INIT ---
router = APIRouter()

# --- HELPER: Detect & Log Gaps ---
def check_and_log_gap(db_session: Session, user_id: str, role: str, question: str, session_id: str, answer: str):
    """
    Checks if the agent's answer indicates missing knowledge.
    If so, logs it to the UnansweredQuery table.
    """
    fallback_phrases = [
        "I do not have access to this information",
        "This information appears to be restricted",
        "I cannot find this information",
        "I cannot find the answer"
    ]
    
    if any(phrase in answer for phrase in fallback_phrases):
        print(f"[GAP DETECTED] Logging unanswered query: {question}")
        gap_entry = UnansweredQuery(
            user_id=user_id,
            user_role=role,
            question=question,
            session_id=session_id
        )
        db_session.add(gap_entry)
        db_session.commit()

# --- ENDPOINT 1: CHAT (Protected + Rate Limited + Agentic) ---
@router.post("/query", response_model=QueryResponse)
@limiter.limit("10/second")  # Limit: 5 requests per minute per IP
def chat_with_agent(
    request: Request,  # Required by slowapi to check IP
    query_data: QueryRequest,  # Renamed to avoid name conflict
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user_role)
):
    """
    Secure Chat Endpoint.
    1. Checks Rate Limit & Auth.
    2. Spinning up the AGENT (Decides between Tools).
    3. Saves History & Logs Gaps.
    """
    
    # 1. Extract verified info from Token
    user_id = current_user["username"]
    user_role = current_user["role"]
    
    # 2. Get or Create Session ID
    session_id = get_or_create_session_id(query_data.session_id)
    
    # 3. Save User Message
    save_message(db_session, user_id, session_id, "user", query_data.question)

    try:
        # 4. Create Agent Executor (Reasoning Engine)
        agent_executor = create_agent_system(user_id, session_id, user_role)
        
        # 5. Invoke Agent
        # The agent uses "input" key standard for React agents
        result = agent_executor.invoke({"input": query_data.question})
        
        # Extract the final string answer from the agent's result dictionary
        agent_answer = result["output"]

        # 6. Check for Knowledge Gaps (Logging)
        check_and_log_gap(db_session, user_id, user_role, query_data.question, session_id, agent_answer)

    except Exception as e:
        print(f"[FATAL AGENT ERROR]: {e}")
        # Graceful fallback so the UI doesn't crash
        agent_answer = "I apologize, but I am currently unable to access my tools. Please try again later."

    # 7. Save Agent Response
    save_message(db_session, user_id, session_id, "agent", agent_answer)
    
    return QueryResponse(answer=agent_answer, session_id=session_id)


# --- ENDPOINT 2: GET SESSIONS (Sidebar History) ---
@router.get("/sessions", response_model=List[SessionInfo])
def get_user_sessions(
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user_role)
):
    """
    Returns a unique list of chat sessions for the logged-in user.
    Used to populate the sidebar.
    """
    user_id = current_user["username"]
    
    # Query all messages for this user, sorted by newest first
    statement = select(ConversationHistory).where(ConversationHistory.user_id == user_id).order_by(ConversationHistory.timestamp.desc())
    results = db_session.exec(statement).all()
    
    unique_sessions = []
    seen_ids = set()
    
    for msg in results:
        if msg.session_id not in seen_ids:
            seen_ids.add(msg.session_id)
            unique_sessions.append(SessionInfo(
                session_id=msg.session_id,
                preview=msg.message_content[:30] + "...",  # First 30 chars
                timestamp=msg.timestamp
            ))
    
    return unique_sessions


# --- ENDPOINT 3: GET HISTORY DETAIL (Load Old Chat) ---
@router.get("/history/{session_id}")
def get_session_messages(
    session_id: str,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user_role)
):
    """
    Loads specific messages when a user clicks a sidebar item.
    """
    return load_message_history(db_session, session_id)
# app/tools/agent_tools.py

from langchain.tools import tool
from sqlmodel import Session, select
from app.database.models import User
from passlib.context import CryptContext
from rag_pipeline.retrieval_chain import create_retriever
import json # <--- New import for cleaning JSON

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- TOOL 1: PASSWORD CHANGE (DEBUG VERSION) ---
def get_password_change_tool(current_user_email: str):
    
    @tool
    def change_my_password(input_str: str):
        """
        Changes the password for the current user. 
        Input should be JUST the new password string.
        """
        print(f"\n[DEBUG] 🛠️ Tool was called!")
        print(f"[DEBUG] Raw Input from AI: '{input_str}'")

        # 1. Clean the Input (Super Robust Mode)
        clean_password = input_str.strip()
        
        # Check if AI sent JSON like {"new_password": "secret"}
        if "{" in clean_password and "}" in clean_password:
            try:
                # Try to parse it as JSON and grab the value
                data = json.loads(clean_password)
                # Grab the first value found (usually the password)
                clean_password = list(data.values())[0]
                print(f"[DEBUG] JSON Detected. Extracted: '{clean_password}'")
            except:
                pass # If parse fails, keep original
        
        # Remove key phrases if AI said "password=secret"
        if "=" in clean_password:
            clean_password = clean_password.split("=")[-1]
            
        # Remove quotes
        clean_password = clean_password.strip().strip("'").strip('"')
        
        print(f"[DEBUG] Final Password to Save: '{clean_password}'")

        # 2. Database Update
        from app.database.database import engine
        
        with Session(engine) as session:
            statement = select(User).where(User.email == current_user_email)
            user = session.exec(statement).first()
            
            if not user:
                print(f"[DEBUG] ❌ User {current_user_email} not found.")
                return "Error: User account not found."
                
            # Update Password
            user.hashed_password = pwd_context.hash(clean_password)
            session.add(user)
            session.commit()
            print(f"[DEBUG] ✅ Database Updated Successfully for {current_user_email}")
            
        return f"Success: Password updated to '{clean_password}'"
    
    return change_my_password

# --- TOOL 2: KNOWLEDGE BASE (Unchanged) ---
def get_knowledge_tool(user_role: str):
    retriever = create_retriever(user_role)
    
    @tool
    def search_knowledge_base(query: str):
        """
        Search for company policies, HR rules, IT guidelines, or procedures.
        Input should be the search query (e.g., "leave policy").
        """
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found."
        return "\n\n".join([d.page_content for d in docs])
        
    return search_knowledge_base

# --- TOOL 3: LEAVE APPLICATION (Unchanged) ---
def get_leave_tool(current_user_email: str):
    # ... (Keep the exact code for leave tool from the previous step) ...
    # If you need it again, I can paste it, but you likely already have it working.
    @tool
    def apply_for_leave(leave_details: str):
        """
        Submits a leave request.
        INPUT MUST BE A SINGLE STRING: "Start, End, Reason"
        """
        from app.database.models import LeaveRequest
        from app.database.database import engine
        
        try:
            parts = leave_details.split(",")
            if len(parts) < 3: return "Error: Use 'Start, End, Reason'"
            start, end = parts[0].strip(), parts[1].strip()
            reason = ",".join(parts[2:]).strip()
        except: return "Error: Format error."

        with Session(engine) as session:
            new_leave = LeaveRequest(user_id=current_user_email, start_date=start, end_date=end, reason=reason)
            session.add(new_leave)
            session.commit()
            
        return f"Success: Leave requested."
    
    return apply_for_leave
# check_leaves.py
from sqlmodel import Session, select, create_engine
from app.database.models import LeaveRequest
from app.core.config import settings

# 1. Connect to Database
engine = create_engine(settings.DATABASE_URL)

def view_all_leaves():
    print("--- 📋 Checking Leave Request Table ---")
    
    with Session(engine) as session:
        # Select all rows from the LeaveRequest table
        statement = select(LeaveRequest)
        results = session.exec(statement).all()
        
        if not results:
            print("No leave requests found.")
        
        for leave in results:
            print(f"ID: {leave.id}")
            print(f"👤 User:   {leave.user_id}")
            print(f"📅 Dates:  {leave.start_date} -> {leave.end_date}")
            print(f"📝 Reason: {leave.reason}")
            print(f"⚡ Status: {leave.status}")
            print("-" * 30)

if __name__ == "__main__":
    view_all_leaves()
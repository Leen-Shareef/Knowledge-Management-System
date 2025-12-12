# reset_all_passwords.py
from sqlmodel import Session, select, create_engine
from app.database.models import User
from app.core.config import settings
from passlib.context import CryptContext

# 1. Setup
engine = create_engine(settings.DATABASE_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_all_to_default():
    print("--- 🔄 Starting Bulk Password Reset ---")
    
    with Session(engine) as session:
        # Get all users
        users = session.exec(select(User)).all()
        
        for user in users:
            # Force reset to 'secret'
            new_hash = pwd_context.hash("secret")
            user.hashed_password = new_hash
            session.add(user)
            print(f"✅ Reset password for: {user.email} -> 'secret'")
            
        session.commit()
        
    print("--- 🏁 All passwords are now 'secret' ---")

if __name__ == "__main__":
    reset_all_to_default()
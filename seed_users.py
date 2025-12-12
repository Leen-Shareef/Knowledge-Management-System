# seed_users.py

from sqlmodel import Session, SQLModel, create_engine, select
from app.database.models import User
from passlib.context import CryptContext
from app.core.config import settings

# 1. Setup Database Connection
engine = create_engine(settings.DATABASE_URL)

# 2. Setup Password Hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user_if_not_exists(session: Session, email: str, name: str, role: str, password: str):
    # Check if user already exists
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        print(f"[INFO] User {email} already exists. Skipping.")
        return

    # Hash the password
    hashed_pw = pwd_context.hash(password)
    
    # Create the User object
    new_user = User(
        email=email,
        full_name=name,
        role=role,
        hashed_password=hashed_pw
    )
    
    session.add(new_user)
    session.commit()
    print(f"[SUCCESS] Created User: {name} ({role}) - {email}")

def main():
    print("--- Starting Admin User Provisioning (Corrected Domain) ---")
    
    # Create the table if it doesn't exist yet
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # --- DEFINING YOUR COMPANY STAFF (Corrected to @kmagent.com) ---
        
        # 1. HR Manager
        create_user_if_not_exists(session, "lolo@kmagent.com", "Lolo Manager", "HR_Employee", "secret")
        
        # 2. IT Tech
        create_user_if_not_exists(session, "bob@kmagent.com", "Bob Tech", "IT_Tech", "secret")
        
        # 3. Sales Rep
        create_user_if_not_exists(session, "alice@kmagent.com", "Alice Sales", "Sales_Team", "secret")

        create_user_if_not_exists(session, "paula@kmagent.com", "paula Tech", "IT_Tech", "secret")
        
    print("--- Provisioning Complete. You may now login with @kmagent.com ---")

if __name__ == "__main__":
    main()
# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# --- Configuration ---
SECRET_KEY = "super_secret_key_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Mock Database of Valid Users ---
# In a real app, this comes from your PostgreSQL 'users' table.
FAKE_USERS_DB = {
    "lolo_hr": {
        "username": "lolo_hr",
        "full_name": "Lolo HR Manager",
        "email": "lolo@hr.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # password: "secret"
        "disabled": False,
        "role": "HR_Employee", # <--- The Real Role
    },
    "bob_it": {
        "username": "bob_it",
        "full_name": "Bob IT Tech",
        "email": "bob@it.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # password: "secret"
        "disabled": False,
        "role": "IT_Tech", # <--- The Real Role
    }
}

# --- Security Tools ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # We add the expiration time to the token
    to_encode.update({"exp": expire})
    
    # We sign the token with our Secret Key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_role(token: str = Depends(oauth2_scheme)):
    """
    Decodes the token to find the user's role. 
    This is the Dependency we will inject into the Agent Router.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role") # Extract the role we stamped
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Return a dictionary with the verified identity
    return {"username": username, "role": role}
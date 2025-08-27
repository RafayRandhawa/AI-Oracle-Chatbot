import json
from db_handler import get_connection
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi import Request,HTTPException,status
# Load environment variables from .env file
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify plain password against hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT token
def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

# Create access + refresh tokens
def create_tokens(user_id: int):
    access_token = create_token(
        {"sub": str(user_id)},
        timedelta(days=7)  # Increased token expiration to 7 days
    )
    refresh_token = create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=30)  # Increased refresh token expiration to 30 days
    )
    return access_token, refresh_token


def authenticate_user(username: str, password: str):
    conn = get_connection()
    user = conn.cursor().execute("SELECT id,username,password_hash FROM users WHERE username = :1", (username,)).fetchone()
    conn.close()

    if user and verify_password(password, user[2]):
        return {"id": user[0], "username": user[1]}
    return None

def login_service(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        return None
    print(f"User {user} authenticated successfully.")
    access_token, refresh_token = create_tokens(user["id"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("auth_token")
    
    if token:
        temp = token.replace("'", "\"")
        token = json.loads(temp).get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token,os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Token")
        
        return {"id": user_id}
    except jwt.JWTError:    
        print("JWT Error occurred during token decoding.")
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    

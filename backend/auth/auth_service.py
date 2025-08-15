from db_handler import get_connection
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

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
        timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    )
    refresh_token = create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))
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

    access_token, refresh_token = create_tokens(user["id"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

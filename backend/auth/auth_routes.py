# routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth.auth_service import authenticate_user

# Create an APIRouter for authentication-related endpoints
auth_router = APIRouter()

# Define a request body schema using Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login")
def login(request: LoginRequest):
    """
    Login endpoint:
    - Validates user credentials using the authentication service
    - Returns JWT token if credentials are correct
    """
    token = authenticate_user(request.username, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": token}

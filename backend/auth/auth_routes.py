# routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from auth.auth_service import login_service
from fastapi.responses import JSONResponse
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
    token = login_service(request.username, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
   
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,        # JS can't read it
        samesite="None",      # "None" if you want cross-site cookies
        secure=False          # True if HTTPS
    )
    return response

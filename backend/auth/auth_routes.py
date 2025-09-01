# routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from auth.auth_service import login_service, get_current_user_from_cookie, get_user_by_id
from fastapi.responses import JSONResponse
import os

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
   
    response = JSONResponse(content={"message": "Login successful", "token":token})
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,        # JS can't read it
        samesite="None" if os.getenv("ENV") == "production" else "Lax", # Adjust based on environment
        secure=os.getenv("ENV") == "production",  # True if HTTPS in production
        max_age=60 * 60,  # Set cookie to expire in 7 days
        expires=60 * 60   # Explicitly set expiration to 7 days
    )
    print(f"Response: {response.body}")  # Log the response body
    print(f"Cookies: {response.headers.get('set-cookie')}")  # Log the set-cookie header
    return response
@auth_router.post("/logout")
async def logout(response: Response):
    # Clear cookie by setting it with empty value and immediate expiry
    response = JSONResponse({"message": "Logout successful"})
    response.delete_cookie(
        key="auth_token",   
        path="/"
    )
    return response

@auth_router.get("/me")
def me(request: Request):
    """
    Returns details about the currently logged-in user.
    """
    try:
        user = get_user_by_id(request)  
        return JSONResponse(content={"logged_in": True})
    except Exception:
        return JSONResponse(content={"logged_in": False})
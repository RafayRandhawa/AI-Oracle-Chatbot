from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sessions.session_service import get_sessions,create_session,rename_session,delete_session,get_messages
from fastapi.responses import JSONResponse
from auth.auth_service import get_current_user_from_cookie
import traceback
session_router = APIRouter()


class SessionRequest(BaseModel):
    
    title: str | None = None

@session_router.post("/create-session")
def create_session(req: SessionRequest, current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Create a new session for the user.
    """
    try:
        # Placeholder logic for session creation
        session_id = create_session(current_user["id"], req.title) 
        return {"success": True, "session_id": session_id}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})
        
@session_router.get("/get-sessions")
def get_sessions_for_user(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Retrieve all sessions for a given user.
    """
    try:
        current_user = current_user["id"]
        sessions = get_sessions(user_id= current_user)
        return {"success": True, "sessions": sessions}
    except Exception as e:
        print(f"Error details: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})
            
        
@session_router.delete("/delete-session/{session_id}")
def delete_session(session_id: int):
    """
    Delete a specific session by its ID.
    """
    try:
        delete_session(session_id)
        return {"success": True, "message": f"Session {session_id} deleted"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})

@session_router.get("/rename-session/{session_id}")
def rename_session(session_id: int, new_title: str):
    """
    Rename a specific session by its ID.
    """
    try:
        rename_session(session_id, new_title)
        return {"success": True, "message": f"Session {session_id} renamed to {new_title}"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})
        
@session_router.get("/get-messages/{session_id}")
def get_messages_for_session(session_id: int):
    """
    Retrieve all messages for a given session.
    """
    try:
        messages = get_messages(session_id)
        return {"success": True, "messages": messages}
    except Exception as e:
        print(f"Error details: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})
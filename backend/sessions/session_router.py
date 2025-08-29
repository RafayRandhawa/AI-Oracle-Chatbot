from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sessions.session_service import get_sessions,create_session,rename_session,delete_session,get_messages,save_message
from fastapi.responses import JSONResponse
from auth.auth_service import get_current_user_from_cookie
import traceback
session_router = APIRouter()


class SessionRequest(BaseModel):
    
    title: str | None = None

@session_router.post("/create-session")
def create_session_endpoint(req: SessionRequest, current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Create a new session for the user.
    """
    try:
        print(f"Creating session for user: {current_user}")
        print(f"Session title: {req.title}")
        # Call the service function with correct parameters
        user_id = int(current_user["id"])  # Convert string to int
        session_result = create_session(user_id, req.title) 
        if isinstance(session_result, dict) and "error" in session_result:
            raise Exception(session_result["message"])
        print(f"Session created with ID: {session_result}")
        return {"success": True, "session_id": session_result}
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})
        
@session_router.get("/get-sessions")
def get_sessions_endpoint(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Retrieve all sessions for a given user.
    """
    try:
        user_id = int(current_user["id"])  # Convert string to int
        sessions = get_sessions(user_id=user_id)
        print({"success": True, "sessions": sessions})
        return {"success": True, "sessions": sessions}
    except Exception as e:
        print(f"Error details: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})
            
        
@session_router.delete("/delete-session/{session_id}")
def delete_session_endpoint(session_id: int):
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
def rename_session_endpoint(session_id: int, new_title: str):
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
def get_messages_endpoint(session_id: int):
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


from pydantic import BaseModel
from fastapi import Depends
from fastapi.responses import JSONResponse
import traceback


class MessageRequest(BaseModel):
    session_id: int
    role: str  # e.g. "user" or "assistant"
    content: str


@session_router.post("/set-messages")
def store_message_endpoint(
    req: MessageRequest, current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Store a new message for a given session.
    """
    try:
        user_id = int(current_user["id"])
        print(f"Storing message for user {user_id}, session {req.session_id}")

        # Call service layer
        message_id = save_message(
            session_id=req.session_id,
            role=req.role,
            content=req.content,
        )
        return {"success": True, "message_id": message_id}

    except Exception as e:
        print(f"Error storing message: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "failed",
                "error": str(e),
            },
        )
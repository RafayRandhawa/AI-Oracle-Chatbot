from db_handler import get_connection
import oracledb
import logging
import traceback

def create_session(user_id: int,title: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO CHAT_SESSIONS (user_id,title) VALUES (:1,:2) RETURNING id INTO :3", (user_id,title,cursor.var(int)))
        session_id = cursor.getvalue(2)
        conn.commit()
        return session_id
    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error in create_session:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }
        
        
def get_sessions(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute("SELECT id, title, started_at FROM CHAT_SESSIONS WHERE user_id = :1", (user_id,))
        sessions = [{"session_id": row[0], "title": row[1], "created_at": row[2]} for row in cursor.fetchall()]
        return sessions
    except oracledb.DatabaseError as db_err:
        print("Database error occurred in get_sessions.")
        error_obj, = db_err.args
        logging.error("Database error in get_sessions:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }
    finally:
        cursor.close()
        conn.close()
        
def delete_session(session_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM CHAT_SESSIONS WHERE id = :1", (session_id,))
        conn.commit()
        return {"success": True}
    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error in delete_session:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }
    finally:
        cursor.close()
        conn.close()

def rename_session(session_id: int, new_title: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE CHAT_SESSIONS SET title = :1 WHERE id = :2", (new_title, session_id))
        conn.commit()
        return {"success": True}
    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error in rename_session:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }
    finally:
        cursor.close()
        conn.close()
        
def get_messages(session_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("Select id, role, content, created_at FROM MESSAGES WHERE session_id = :1 ORDER BY created_at ASC", (session_id,))
        messages = [{"id": row[0], "role": row[1], "content": row[2], "created_at": row[3]} for row in cursor.fetchall()]
        return messages
    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error in get_messages:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }
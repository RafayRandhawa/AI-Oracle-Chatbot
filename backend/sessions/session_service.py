import logging
import traceback
from db_handler import get_connection
import oracledb


def create_session(user_id: str, title: str):
    """Create a new chat session."""
    print(f"create_session called with user_id: {user_id}, title: {title}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        session_id_var = cursor.var(str)

        cursor.execute(
            """
            INSERT INTO chat_sessions (user_id, title)
            VALUES (:1, :2)
            RETURNING session_id INTO :3
            """,
            (user_id, title, session_id_var)
        )

        session_id = session_id_var.getvalue()
        conn.commit()
        print(f"Session ID fetched: {session_id}")
        return session_id

    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error in create_session:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }

    finally:
        cursor.close()
        conn.close()


def get_sessions(user_id: str):
    """Retrieve all sessions for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT session_id, title, started_at, last_message_at, status
            FROM chat_sessions
            WHERE user_id = :1
            ORDER BY started_at DESC
            """,
            (user_id,)
        )
        sessions = [
            {
                "session_id": row[0],
                "title": row[1],
                "started_at": row[2],
                "last_message_at": row[3],
                "status": row[4]
            }
            for row in cursor.fetchall()
        ]
        return sessions

    except oracledb.DatabaseError as db_err:
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


def delete_session(session_id: str):
    """Delete a session by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM chat_sessions WHERE session_id = :1",
            (session_id,)
        )
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


def rename_session(session_id: str, new_title: str):
    """Update the title of a session."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE chat_sessions SET title = :1 WHERE session_id = :2",
            (new_title, session_id)
        )
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


def get_messages(session_id: str):
    """Retrieve all messages for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT message_id, role, content, created_at
            FROM chat_messages
            WHERE session_id = :1
            ORDER BY created_at ASC
            """,
            (session_id,)
        )

        messages = [
            {
                "message_id": row[0],
                "role": row[1],
                "content": row[2],
                "created_at": row[3],
            }
            for row in cursor.fetchall()
        ]
        return messages

    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error in get_messages:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code
        }

    finally:
        cursor.close()
        conn.close()


def save_message(session_id: str, role: str, content: str):
    """Save a message to a session."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        message_id_var = cursor.var(str)  # Use str for VARCHAR2

        cursor.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (:1, :2, :3, SYSTIMESTAMP)
            RETURNING message_id INTO :4
            """,
            (session_id, role, content, message_id_var)
        )

        message_id = message_id_var.getvalue()
        conn.commit()
        return message_id

    except Exception as e:
        conn.rollback()
        logging.error("Error in save_message:\n%s", traceback.format_exc())
        raise

    finally:
        cursor.close()
        conn.close()

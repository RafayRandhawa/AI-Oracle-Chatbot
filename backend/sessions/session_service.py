from db_handler import get_connection
import oracledb
import logging
import traceback

def create_session(user_id: int, title: str):
    print(f"create_session called with user_id: {user_id}, title: {title}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Create output variable for session_id
        session_id_var = cursor.var(int)

        cursor.execute(
            """
            INSERT INTO CHAT_SESSIONS (user_id, title)
            VALUES (:1, :2)
            RETURNING id INTO :3
            """,
            (user_id, title, session_id_var)
        )

        # Retrieve session_id from variable
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
        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM chat_messages
            WHERE session_id = :1
            ORDER BY created_at ASC
            """,
            (session_id,),
        )
        messages = [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "created_at": row[3],
            }
            for row in cursor.fetchall()
        ]
        return messages

    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error(
            "Database error in get_messages:\n%s", traceback.format_exc()
        )
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code,
        }

    finally:
        cursor.close()
        conn.close()


def save_message(session_id: int, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # create bind variable
        message_id_var = cursor.var(int)

        cursor.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (:1, :2, :3, SYSTIMESTAMP)
            RETURNING id INTO :4
            """,
            (session_id, role, content, message_id_var),
        )

        message_id = message_id_var.getvalue()
        conn.commit()
        return message_id

    except Exception as e:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# def get_messages(session_id: int):
#     conn = get_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             """
#             SELECT id, role, content, created_at,
#                    model, prompt_tokens, completion_tokens, latency_ms,
#                    sql_text, sql_blocked, error_text
#             FROM chat_messages
#             WHERE session_id = :1
#             ORDER BY created_at ASC
#             """,
#             (session_id,)
#         )

#         rows = cursor.fetchall()
#         messages = [
#             {
#                 "id": r[0],
#                 "role": r[1],
#                 "content": r[2],
#                 "created_at": str(r[3]),
#                 "model": r[4],
#                 "prompt_tokens": r[5],
#                 "completion_tokens": r[6],
#                 "latency_ms": r[7],
#                 "sql_text": r[8],
#                 "sql_blocked": r[9],
#                 "error_text": r[10]
#             }
#             for r in rows
#         ]
#         return messages
#     finally:
#         cursor.close()
#         conn.close()

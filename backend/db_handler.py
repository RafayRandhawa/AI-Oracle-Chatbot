import oracledb
from dotenv import load_dotenv
import os
import traceback
import logging

import time


logging.basicConfig(filename="db_errors.log", level=logging.ERROR)
# Initialize the Oracle Client in 'thick mode' by specifying the Instant Client path.
# This is REQUIRED for connecting to older versions of Oracle like 11g.
load_dotenv()
oracledb.init_oracle_client(lib_dir=os.getenv("INSTANT_CLIENT"))

# Database configuration: replace these with your actual credentials.
DB_USER = 'chatbot_user'
DB_PASSWORD = 'chatbotpass'
DB_DSN = 'localhost/XE'  # DSN format is 'hostname/SERVICE_NAME' for Oracle XE.

def get_connection():
    """
    Establishes a connection to the Oracle Database.
    
    Returns:
        connection (oracledb.Connection): Active connection object.
    """
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        mode=oracledb.AUTH_MODE_DEFAULT  # Explicitly using standard authentication.
    )


def connect_with_retry(max_retries=3, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_connection()
            return conn
        except oracledb.Error as e:
            if attempt < max_retries:
                print(f"Connection failed (attempt {attempt}), retrying...")
                time.sleep(delay)
            else:
                raise e  # re-raise the last error after final attempt


def execute_query(query: str):
    """
    Executes a SQL query (SELECT, DML, or DDL) and returns results or error details.

    Returns:
        list[dict]: For SELECT queries, returns list of rows as dictionaries.
        dict: For DML/DDL, returns a success message.
        dict: For errors, returns structured error with traceback.
    """
    conn = None
    cursor = None
    try:
        # Get connection
        conn = connect_with_retry()
        cursor = conn.cursor()

        # Clean up query and execute
        query = query.strip().rstrip(';')
        cursor.execute(query)

        # If SELECT query
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            conn.commit()
            return {"message": "Query executed successfully"}

    except oracledb.DatabaseError as db_err:
        # Database-specific errors
        error_obj, = db_err.args
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code,
            "query": query
        }

    except Exception as e:
        logging.error("Unexpected error:\n%s", traceback.format_exc())
        # General Python errors (e.g., type error in AI logic)
        return {
            "error": "Unexpected Error",
            "message": str(e),
            "query": query,
            "trace": traceback.format_exc()
        }

    finally:
        # Close resources
        if cursor:
            try: cursor.close()
            except: pass
        if conn:
            try: conn.close()
            except: pass





# Cache variable to store metadata after first retrieval
_cached_metadata = None


def extract_db_metadata(force_refresh=False):
    """
    Extracts comprehensive database metadata, with optional caching.

    Args:
        force_refresh (bool): If True, refreshes the cache even if already loaded.

    Returns:
        dict: Database metadata including tables, columns, data types, PKs, FKs, comments.
    """
    global _cached_metadata

    if _cached_metadata is not None and not force_refresh:
        print("Returning cached metadata")
        return _cached_metadata

    print("Extracting metadata from database...")
    conn = get_connection()
    cursor = conn.cursor()

    metadata = {}

    try:
        # Columns, data types, nullability, comments
        column_query = """
            SELECT
                c.table_name,
                c.column_name,
                c.data_type,
                c.nullable,
                tc.comments AS column_comment
            FROM
                user_tab_columns c
            LEFT JOIN
                user_col_comments tc
            ON
                c.table_name = tc.table_name AND c.column_name = tc.column_name
            ORDER BY
                c.table_name, c.column_id
        """
        cursor.execute(column_query)
        for table_name, column_name, data_type, nullable, col_comment in cursor.fetchall():
            table_name = table_name.upper()
            if table_name not in metadata:
                metadata[table_name] = {
                    "columns": [],
                    "primary_keys": [],
                    "foreign_keys": [],
                    "table_comment": ""
                }
            metadata[table_name]["columns"].append({
                "name": column_name,
                "type": data_type,
                "nullable": nullable,
                "comment": col_comment or ""
            })

        # Primary keys
        pk_query = """
            SELECT
                cols.table_name,
                cols.column_name
            FROM
                user_constraints cons
            JOIN
                user_cons_columns cols
            ON
                cons.constraint_name = cols.constraint_name
            WHERE
                cons.constraint_type = 'P'
        """
        cursor.execute(pk_query)
        for table_name, column_name in cursor.fetchall():
            if table_name in metadata:
                metadata[table_name]["primary_keys"].append(column_name)

        # Foreign keys
        fk_query = """
            SELECT
                a.table_name,
                a.column_name,
                c_pk.table_name AS referenced_table,
                b.column_name AS referenced_column
            FROM
                user_constraints c
            JOIN
                user_cons_columns a
            ON
                c.constraint_name = a.constraint_name
            JOIN
                user_constraints c_pk
            ON
                c.r_constraint_name = c_pk.constraint_name
            JOIN
                user_cons_columns b
            ON
                c_pk.constraint_name = b.constraint_name
            WHERE
                c.constraint_type = 'R'
        """
        cursor.execute(fk_query)
        for table_name, column_name, ref_table, ref_column in cursor.fetchall():
            if table_name in metadata:
                metadata[table_name]["foreign_keys"].append({
                    "column": column_name,
                    "references": {
                        "table": ref_table,
                        "column": ref_column
                    }
                })

        # Table comments
        table_comments_query = """
            SELECT
                table_name,
                comments
            FROM
                user_tab_comments
        """
        cursor.execute(table_comments_query)
        for table_name, comment in cursor.fetchall():
            if table_name in metadata:
                metadata[table_name]["table_comment"] = comment or ""

        _cached_metadata = metadata  # Cache for future calls
        return metadata

    finally:
        cursor.close()
        conn.close()

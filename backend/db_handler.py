import oracledb
from dotenv import load_dotenv
import os
import traceback
import logging
import re
import time

# Cache variable to store metadata after first retrieval
_cached_metadata = None

logging.basicConfig(filename="db_errors.log", level=logging.ERROR)
# Initialize the Oracle Client in 'thick mode' by specifying the Instant Client path.
# This is REQUIRED for connecting to older versions of Oracle like 11g.
load_dotenv()
oracledb.init_oracle_client(lib_dir=os.getenv("INSTANT_CLIENT"))

# Database configuration:

# DB_USER = 'CHATBOT_USER'
# DB_PASSWORD = 'chatbotpass'
# DB_DSN = 'localhost/XE'  

# DSN format is 'hostname/SERVICE_NAME' for Oracle XE.


#Test Server Credentials


DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DSN = os.getenv('DB_DSN')




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


def execute_query(query: str, params: dict = None):
    """
    Executes a SQL query with optional parameters and returns results or error details.

    Args:
        query (str): SQL query with placeholders (e.g., SELECT * FROM employees WHERE name = :emp_name)
        params (dict): Optional dictionary of bind parameters.

    Returns:
        list[dict] | dict: Query results or status/error message.
    """
    conn = None
    cursor = None
    try:
        conn = connect_with_retry()
        cursor = conn.cursor()

        query = query.strip().rstrip(';')
        logging.info("Executing query:\n%s\nParams: %s", query, params)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if cursor.description:  # SELECT
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:  # DML / DDL
            conn.commit()
            return {"message": "Query executed successfully"}

    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        logging.error("Database error:\n%s", traceback.format_exc())
        return {
            "error": "Database Error",
            "message": str(error_obj.message),
            "code": error_obj.code,
            "query": query
        }

    except Exception as e:
        logging.error("Unexpected error:\n%s", traceback.format_exc())
        return {
            "error": "Unexpected Error",
            "message": str(e),
            "query": query,
            "trace": traceback.format_exc()
        }

    finally:
        if cursor:
            try: cursor.close()
            except: pass
        if conn:
            try: conn.close()
            except: pass


def extract_db_metadata(owner: str = 'TIS', force_refresh=False):
    """
    Extracts comprehensive database metadata for a given owner/schema, with optional caching.

    Args:
        owner (str): The schema owner to extract metadata from (default is 'TIS').
        force_refresh (bool): If True, refreshes the cache even if already loaded.

    Returns:
        dict: Database metadata including tables, columns, data types, PKs, FKs, comments.
    """
    global _cached_metadata

    if _cached_metadata is not None and not force_refresh:
        print("Returning cached metadata")
        return _cached_metadata

    print(f"Extracting metadata from database for owner: {owner}")
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
                cc.comments AS column_comment
            FROM
                all_tab_columns c
            LEFT JOIN
                all_col_comments cc
            ON
                c.owner = cc.owner AND c.table_name = cc.table_name AND c.column_name = cc.column_name
            WHERE
                c.owner = :owner
            ORDER BY
                c.table_name, c.column_id
        """
        cursor.execute(column_query, {"owner": owner})
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
                all_constraints cons
            JOIN
                all_cons_columns cols
            ON
                cons.owner = cols.owner AND cons.constraint_name = cols.constraint_name
            WHERE
                cons.constraint_type = 'P' AND cons.owner = :owner
        """
        cursor.execute(pk_query, {"owner": owner})
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
                all_constraints c
            JOIN
                all_cons_columns a
            ON
                c.owner = a.owner AND c.constraint_name = a.constraint_name
            JOIN
                all_constraints c_pk
            ON
                c.r_constraint_name = c_pk.constraint_name AND c.r_owner = c_pk.owner
            JOIN
                all_cons_columns b
            ON
                c_pk.owner = b.owner AND c_pk.constraint_name = b.constraint_name
            WHERE
                c.constraint_type = 'R' AND c.owner = :owner
        """
        cursor.execute(fk_query, {"owner": owner})
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
                all_tab_comments
            WHERE
                owner = :owner
        """
        cursor.execute(table_comments_query, {"owner": owner})
        for table_name, comment in cursor.fetchall():
            if table_name in metadata:
                metadata[table_name]["table_comment"] = comment or ""

        _cached_metadata = metadata  # Cache for future calls
        return metadata

    finally:
        cursor.close()
        conn.close()



def parameterize_query(query: str):
    param_index = 1
    params = {}

    # 1️⃣ Handle TO_DATE('...', '...') → :paramX
    def replace_todate(match):
        nonlocal param_index
        date_val = match.group(1)
        fmt_val = match.group(2)
        key = f"param{param_index}"
        param_index += 1
        params[key] = (date_val, fmt_val)
        return f"TO_DATE(:{key}, '{fmt_val}')"

    query = re.sub(r"TO_DATE\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", replace_todate, query, flags=re.IGNORECASE)

    # 2️⃣ Handle ILIKE → LOWER(column) LIKE LOWER(:paramX)
    def replace_ilike(match):
        nonlocal param_index
        column = match.group(1)
        value = match.group(2)
        key = f"param{param_index}"
        param_index += 1
        params[key] = value
        return f"LOWER({column}) LIKE LOWER(:{key})"

    query = re.sub(
        r"(\w+(?:\.\w+)?)\s+ILIKE\s+'([^']*)'",
        replace_ilike,
        query,
        flags=re.IGNORECASE
    )


    # 3️⃣ Handle IN (...) with strings or numbers → IN (:param1, :param2, ...)
    def replace_in_clause(match):
        nonlocal param_index
        values = match.group(1)
        elements = [v.strip().strip("'") for v in values.split(',')]
        bind_keys = []
        for val in elements:
            key = f"param{param_index}"
            param_index += 1
            try:
                val_converted = float(val) if '.' in val else int(val)
            except ValueError:
                val_converted = val
            params[key] = val_converted
            bind_keys.append(f":{key}")
        return f"IN ({', '.join(bind_keys)})"

    query = re.sub(r"\bIN\s*\(\s*([^)]+?)\s*\)", replace_in_clause, query, flags=re.IGNORECASE)

    # 4️⃣ Replace string literals → :paramX
    def replace_string(match):
        nonlocal param_index
        key = f"param{param_index}"
        param_index += 1
        value = match.group(1)
        params[key] = value
        return f":{key}"

    query = re.sub(r"'([^']*)'", replace_string, query)

    # 5️⃣ Replace numbers (not part of idenCHATBOT_USERiers or TO_DATE) → :paramX
    def replace_number(match):
        nonlocal param_index
        key = f"param{param_index}"
        param_index += 1
        num_str = match.group(0)
        value = float(num_str) if '.' in num_str else int(num_str)
        params[key] = value
        return f":{key}"

    query = re.sub(r'(?<![\w.])(\d+(\.\d+)?)(?!\w)', replace_number, query)

    return query, params


def is_safe_query(sql: str) -> bool:
    forbidden_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "MERGE", "UPDATE", "INSERT","PURGE"]
    sql_upper = sql.upper()
    for kw in forbidden_keywords:
        # \b matches a word boundary, so UPDATE_ won't match UPDATE
        if re.search(rf"\b{kw}\b", sql_upper):
            return False
    return True

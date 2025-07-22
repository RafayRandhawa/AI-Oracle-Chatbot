import oracledb

# Initialize the Oracle Client in 'thick mode' by specifying the Instant Client path.
# This is REQUIRED for connecting to older versions of Oracle like 11g.
oracledb.init_oracle_client(lib_dir=r"D:\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8")

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

def execute_query(query: str):
    """
    Executes a SQL query (can be SELECT, INSERT, UPDATE, DELETE, DDL etc.)
    
    Args:
        query (str): The SQL query to be executed.
    
    Returns:
        list of dict: If query is a SELECT, returns a list of rows mapped as dictionaries.
        dict: If query is DDL/DML, returns a success message.
        dict: In case of error, returns an error message and debug context.
    """
    conn = None
    cursor = None
    try:
        # Establish database connection
        conn = get_connection()
        cursor = conn.cursor()

        # Execute the provided query
        # Clean up the query to remove trailing semicolon
        query = query.strip().rstrip(';')
        cursor.execute(query)

        # cursor.description is not None if the query returns rows (e.g., SELECT).
        if cursor.description:
            # Extract column names from cursor.description
            columns = [col[0] for col in cursor.description]
            
            # Map each row to a dictionary {column_name: value, ...}
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            return results
        else:
            # If query is DML/DDL, commit changes to database
            conn.commit()
            return {"message": "Query executed successfully"}

    except Exception as e:
        # Catch any errors that occur during connection or query execution
        return {
            "error": str(e),
            "context": locals()  # Include local variables for debugging
        }

    finally:
        # Ensure cursor and connection are always closed (even if errors occur)
        if cursor:
            cursor.close()
        if conn:
            conn.close()


import oracledb
from db_handler import get_connection

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

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

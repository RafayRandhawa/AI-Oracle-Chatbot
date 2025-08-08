import oracledb
from db_handler import get_connection  # reuse your existing logic

def get_metadata_rows():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name, column_name, data_type, nullable
        FROM all_tab_columns
        WHERE owner = 'TIF'
    """)
    return cursor.fetchall()

def format_metadata_rows(rows):
    return [
        f"Table: {table}, Column: {column}, Type: {dtype}, Nullable: {nullable}"
        for table, column, dtype, nullable in rows
    ]

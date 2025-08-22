import oracledb
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

# Initialize Oracle Client
try:
    oracledb.init_oracle_client(lib_dir=r"D:\instantclient_23_9")
    print("✅ Oracle Instant Client initialized")
except Exception as e:
    print(f"⚠️ Oracle Client init: {e}")

def get_connection():
    """Establish and return a database connection"""
    try:
        conn = oracledb.connect(
            user='CHATBOT_USER',
            password='chatbotpass',
            dsn='localhost/XE'
        )
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise

def test_metadata_extraction():
    """Test each step of metadata extraction"""
    print("🔍 Testing metadata extraction step by step...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Test 1: Check if user exists and has tables
        print("\n1. Checking if user CHATBOT_USER exists and has tables...")
        cursor.execute("SELECT COUNT(*) FROM all_tables WHERE owner = 'CHATBOT_USER'")
        table_count = cursor.fetchone()[0]
        print(f"   Tables found for CHATBOT_USER: {table_count}")
        
        if table_count == 0:
            print("   ❌ No tables found for CHATBOT_USER!")
            print("   Checking available schemas...")
            cursor.execute("SELECT DISTINCT owner FROM all_tables ORDER BY owner")
            schemas = cursor.fetchall()
            print("   Available schemas:")
            for schema in schemas:
                print(f"     - {schema[0]}")
            return False
        
        # Test 2: Check column extraction
        print("\n2. Testing column extraction...")
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
                c.owner = 'CHATBOT_USER'
            ORDER BY
                c.table_name, c.column_id
        """
        cursor.execute(column_query)
        columns = cursor.fetchall()
        print(f"   Columns found: {len(columns)}")
        
        if columns:
            for i, (table_name, column_name, data_type, nullable, col_comment) in enumerate(columns[:3]):
                print(f"     Sample {i+1}: {table_name}.{column_name} ({data_type})")
        
        # Test 3: Check table comments
        print("\n3. Testing table comments...")
        cursor.execute("SELECT table_name, comments FROM all_tab_comments WHERE owner = 'CHATBOT_USER'")
        table_comments = cursor.fetchall()
        print(f"   Table comments found: {len(table_comments)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_metadata_extraction()
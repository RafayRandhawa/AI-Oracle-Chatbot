import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

def check_connection():
    print("🔍 Testing Oracle Database Connection...")
    print("=" * 50)
    
    # Initialize Oracle Client
    try:
        oracledb.init_oracle_client(lib_dir=r"D:\instantclient_23_9")
        print("✅ Oracle Instant Client initialized")
    except Exception as e:
        print(f"⚠️ Oracle Client init: {e}")

    try:
        # Test connection
        conn = oracledb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=os.getenv('DB_DSN')
        )
        print("✅ Connection successful!")
        
        # Get database info
        cursor = conn.cursor()
        
        # 1. Check database version
        cursor.execute('SELECT * FROM v$version WHERE banner LIKE \'Oracle%\'')
        version = cursor.fetchone()
        print(f"📋 Database Version: {version[0]}")
        
        # 2. Check current user
        cursor.execute('SELECT USER FROM dual')
        current_user = cursor.fetchone()
        print(f"👤 Connected as: {current_user[0]}")
        
        # 3. Check available tables
        cursor.execute('SELECT COUNT(*) FROM user_tables')
        table_count = cursor.fetchone()
        print(f"📊 Tables in schema: {table_count[0]}")
        
        # 4. Show first 5 tables
        cursor.execute('SELECT table_name FROM user_tables WHERE rownum <= 5')
        tables = cursor.fetchall()
        print("🗂️ Sample tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # 5. Check connection details (removed connection_id for compatibility)
        print(f"🌐 Service name: {conn.dsn}")
        
        conn.close()
        print("\n🎉 Connection test completed successfully!")
        return True
        
    except oracledb.Error as e:
        error, = e.args
        print(f"❌ Connection failed!")
        print(f"   Error code: {error.code}")
        print(f"   Error message: {error.message}")
        print(f"   Context: {error.context}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    check_connection()
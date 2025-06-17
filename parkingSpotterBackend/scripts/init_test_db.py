import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from database.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def create_test_database():
    """Create the test database if it doesn't exist."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    try:
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='parking_spotter_test'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE parking_spotter_test')
            print("Test database created successfully!")
        else:
            print("Test database already exists.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_test_database() 
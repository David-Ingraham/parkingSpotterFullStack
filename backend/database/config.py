import os

# Check if Render provides a complete DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    print(f"DEBUG: Using provided DATABASE_URL")
else:
    # Fallback: Build from individual components for local development
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'parking_spotter')
    
    # Debug logging to see what we actually got
    print(f"DEBUG: Building DATABASE_URL from components:")
    print(f"DEBUG: DB_USER = '{DB_USER}'")
    print(f"DEBUG: DB_PASSWORD = '{'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}'")
    print(f"DEBUG: DB_HOST = '{DB_HOST}'")
    print(f"DEBUG: DB_PORT = '{DB_PORT}'")
    print(f"DEBUG: DB_NAME = '{DB_NAME}'")
    
    # Database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"DEBUG: Final DATABASE_URL = {DATABASE_URL[:20]}...{DATABASE_URL[-20:]}")

# Other configurations can be added here
WEBSOCKET_PORT = 8001
HTTP_PORT = 8000 
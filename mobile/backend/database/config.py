import os
from pathlib import Path

# Check if DATABASE_URL is provided (for production deployment)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    print(f"Using provided DATABASE_URL")
else:
    # Use SQLite for local development
    # Database file will be in backend/parking_spotter.db
    db_path = Path(__file__).parent.parent / 'parking_spotter.db'
    DATABASE_URL = f"sqlite:///{db_path}"
    print(f"Using SQLite database at: {db_path}")

# Other configurations can be added here
WEBSOCKET_PORT = 8001
HTTP_PORT = 8000 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_backend_url():
    # If we're running for the emulator, use 10.0.2.2
    if os.getenv("FLASK_ENV") == "emulator":
        return "http://10.0.2.2:8000"
    # Otherwise default to localhost
    return "http://localhost:8000"

backend_url = get_backend_url() 
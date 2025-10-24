"""
Parking Spotter Backend API

A Flask-based REST API for accessing NYC parking camera data.
Designed with privacy-first principles - no user data collection.

Author: Parking Spotter Team
License: MIT
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from routes import register_routes
from waitress import serve
from database.db import init_db

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for cross-origin requests from mobile app
CORS(app)

@app.after_request
def add_cache_headers(response):
    """
    Add cache control headers to all responses.
    Helps improve performance by allowing browsers to cache static content.
    """
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'public, max-age=60'  # Cache for 1 minute
    return response

# Load environment variables from .env file (development) or system (production)
load_dotenv()

# Initialize database connection and create tables if needed
print("Initializing database...")
init_db()

# Register all API route blueprints
register_routes(app)

if __name__ == "__main__":
    """
    Start the production WSGI server.
    
    Uses Waitress server which is production-ready and handles:
    - Multiple concurrent requests
    - Proper HTTP protocol implementation
    - Security features like request size limits
    """
    print("Starting HTTP server on http://0.0.0.0:8000")
    serve(app, host="0.0.0.0", port=8000)

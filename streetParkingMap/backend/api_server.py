"""
API Server - Flask API with Background Scanner
Main entry point for the backend
"""

from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread, Lock
import time
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner import CameraScanner

# Configuration
CAMERA_DATA_PATH = 'data/manhattan_cameras.json'
MODEL_PATH = 'models/weights.pt'
SCAN_INTERVAL = 600  # 10 minutes (in seconds)
MAX_WORKERS = 8  # Parallel scanning threads

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global in-memory storage
camera_status = {}
status_lock = Lock()
scanner = None
last_scan_time = None

def background_scanner():
    """
    Background thread that continuously scans cameras
    Runs every SCAN_INTERVAL seconds
    """
    global camera_status, last_scan_time, scanner
    
    print("\n" + "="*60)
    print("Background Scanner Thread Started")
    print(f"Scan interval: {SCAN_INTERVAL} seconds ({SCAN_INTERVAL/60:.1f} minutes)")
    print("="*60 + "\n")
    
    while True:
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting camera scan...")
            
            # Run scan
            results = scanner.scan_all_cameras()
            
            # Update global state (thread-safe)
            with status_lock:
                camera_status.clear()
                camera_status.update(results)
                last_scan_time = time.time()
            
            print(f"✓ Updated in-memory status with {len(results)} cameras")
            print(f"Next scan in {SCAN_INTERVAL/60:.1f} minutes...\n")
            
        except Exception as e:
            print(f"[ERROR] Scanner thread error: {e}")
            print("Continuing anyway...\n")
        
        # Sleep until next scan
        time.sleep(SCAN_INTERVAL)

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """
    Get all camera statuses
    
    Returns:
        JSON object with cameras and metadata:
        {
            "cameras": {...},
            "last_scan": timestamp,
            "camera_count": int
        }
    """
    with status_lock:
        return jsonify({
            'cameras': camera_status,
            'last_scan': last_scan_time,
            'camera_count': len(camera_status),
            'scan_interval': SCAN_INTERVAL
        })

@app.route('/api/camera/<address>', methods=['GET'])
def get_camera(address):
    """
    Get specific camera status
    
    Args:
        address: Camera address/name
        
    Returns:
        JSON object with camera data or 404
    """
    with status_lock:
        if address in camera_status:
            return jsonify(camera_status[address])
        else:
            return jsonify({'error': 'Camera not found'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON with server status
    """
    with status_lock:
        return jsonify({
            'status': 'online',
            'cameras_loaded': len(camera_status),
            'last_scan': last_scan_time,
            'scanner_active': scanner is not None
        })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Street Parking Map API',
        'version': '1.0.0',
        'endpoints': {
            '/api/cameras': 'Get all camera statuses',
            '/api/camera/<address>': 'Get specific camera status',
            '/api/health': 'Health check'
        }
    })

def initialize_scanner():
    """Initialize the scanner and start background thread"""
    global scanner
    
    print("\n" + "="*60)
    print("STREET PARKING MAP - Backend Server")
    print("="*60 + "\n")
    
    # Check if required files exist
    if not os.path.exists(CAMERA_DATA_PATH):
        print(f"[ERROR] Camera data file not found: {CAMERA_DATA_PATH}")
        print("Please ensure manhattan_cameras.json is in the data/ directory")
        sys.exit(1)
    
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found: {MODEL_PATH}")
        print("Please copy your weights.pt file to models/ directory")
        print("Expected location: streetParkingMap/backend/models/weights.pt")
        sys.exit(1)
    
    # Initialize scanner
    print("Initializing camera scanner...")
    scanner = CameraScanner(
        camera_data_path=CAMERA_DATA_PATH,
        model_path=MODEL_PATH,
        max_workers=MAX_WORKERS
    )
    
    # Run initial scan before starting API
    print("\nRunning initial scan...")
    global camera_status, last_scan_time
    results = scanner.scan_all_cameras()
    with status_lock:
        camera_status.update(results)
        last_scan_time = time.time()
    print(f"✓ Initial scan complete. {len(results)} cameras ready.\n")
    
    # Start background scanner thread
    scanner_thread = Thread(target=background_scanner, daemon=True)
    scanner_thread.start()
    
    print("="*60)
    print("Server ready!")
    print("API available at: http://localhost:5000")
    print("Try: http://localhost:5000/api/cameras")
    print("="*60 + "\n")

if __name__ == '__main__':
    # Initialize scanner and start background thread
    initialize_scanner()
    
    # Start Flask API server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False for production
        use_reloader=False  # Disable reloader to prevent double initialization
    )


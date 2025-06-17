import os
import time
import uuid
from flask import Blueprint, request, jsonify
from PIL import Image
from helpers.fetch_image import fetch_and_save_image
from helpers.get_nearby_cameras import find_nearby_cameras
import psutil
import os
import inspect 

bp = Blueprint('five_nearest', __name__)
BASE_URL = os.getenv("BACKEND_URL")

# NYC boundary coordinates
NYC_BOUNDS = {
    "lat_min": 40.4774,
    "lat_max": 40.9176,
    "lng_min": -74.2591,
    "lng_max": -73.7004
}

def is_within_nyc(lat: float, lng: float) -> bool:
    """Check if coordinates are within NYC boundaries"""
    return (NYC_BOUNDS["lat_min"] <= lat <= NYC_BOUNDS["lat_max"] and
            NYC_BOUNDS["lng_min"] <= lng <= NYC_BOUNDS["lng_max"])

def log_memory(label=""):
    proc = psutil.Process(os.getpid())
    mem = proc.memory_info().rss / 1024 / 1024  # in MB
    print(f"[{label}] Memory usage: {mem:.2f} MB")

def cleanup_old_dirs():
    """Clean up directories older than 5 minutes"""
    base_dir = os.path.join("static", "imgs")
    now = time.time()
    if os.path.exists(base_dir):
        for dir_name in os.listdir(base_dir):
            dir_path = os.path.join(base_dir, dir_name)
            if os.path.isdir(dir_path):
                # Check if directory is older than 5 minutes
                if now - os.path.getctime(dir_path) > 300:  # 300 seconds = 5 minutes
                    try:
                        for f in os.listdir(dir_path):
                            os.remove(os.path.join(dir_path, f))
                        os.rmdir(dir_path)
                    except Exception as e:
                        print(f"Failed to cleanup directory {dir_path}: {e}")

@bp.before_app_request
def log_headers():
    print("BASE_URL is:", BASE_URL)
    print(f"\n[{request.method}] {request.path}")
    for h, v in request.headers.items():
        print(f"{h}: {v}")

@bp.post("/fiveNearest")
def fiveNearest():
    print(f"Above is for the {inspect.stack()[1][3]} endpoint")
    
    log_memory("start /fiveNearest")
    start = time.time()
    data = request.get_json()
    
    # Validate input data
    if not data or "lat" not in data or "lng" not in data:
        return jsonify(error="Missing latitude or longitude"), 400
        
    try:
        lat = float(data["lat"])
        lng = float(data["lng"])
    except (ValueError, TypeError):
        return jsonify(error="Invalid latitude or longitude format"), 400
        
    # Check if coordinates are within NYC
    if not is_within_nyc(lat, lng):
        return jsonify(error="Location must be within NYC boundaries"), 400
    
    # Create a unique directory for this request
    request_id = str(uuid.uuid4())
    img_dir = os.path.join("static", "imgs", request_id)
    os.makedirs(img_dir, exist_ok=True)
    
    # Clean up old request directories in the background
    cleanup_old_dirs()

    cameras = find_nearby_cameras(lat, lng, "camera_id_lat_lng_wiped.json")
    if not cameras:
        return jsonify(error="no cameras nearby"), 404

    log_memory("after image fetch")

    stamp = int(time.time())
    output = []

    for addr, info in list(cameras.items())[:5]:
        try:
            img = fetch_and_save_image(info["camera_id"], stamp)
            if img.width > 640:
                h = img.height * 640 // img.width
                img = img.resize((640, h), Image.LANCZOS)

            filename = f"{stamp}_{addr.replace(' ', '_')}.jpg"
            path = os.path.join(img_dir, filename)
            with open(path, 'wb') as f:
                img.save(f, format="JPEG", quality=70, optimize=True)
                f.flush()
                os.fsync(f.fileno())

            output.append({
                "address": addr,
                "url": f"{BASE_URL}/static/imgs/{request_id}/{filename}"
            })
        except Exception as e:
            print(f"[ERROR] Failed for {addr}: {e}")

    log_memory("before return")
    print(f"Request took {time.time() - start:.2f} seconds")

    return jsonify(images=output)

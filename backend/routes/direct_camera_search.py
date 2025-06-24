import os
from dotenv import load_dotenv
import time
import json
import uuid
from flask import Blueprint, request, jsonify
from PIL import Image
import googlemaps
from helpers.fetch_image import fetch_and_save_image
from helpers.get_nearby_cameras import find_nearby_cameras
from routes.five_nearest import cleanup_old_dirs

# Load environment variables from .env file
load_dotenv()

bp = Blueprint('direct_camera_search', __name__)
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # Default to localhost if not set
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")



@bp.post("/search_cameras")
def search_cameras():
    data = request.get_json()
    
    if not data or "addresses" not in data:
        return jsonify(error="No addresses provided"), 400
        
    addresses = data["addresses"]
    
    # Get numCams parameter with default
    numCams = data.get("numCams", 5)
    
    # Input validation for numCams - convert string to int if possible
    try:
        numCams = int(numCams)
    except (ValueError, TypeError):
        return jsonify(error="numCams must be a valid integer"), 400
        
    if numCams < 1 or numCams > 8:
        return jsonify(error="numCams must be between 1 and 8"), 400
    
    # Basic input validation for addresses
    if not isinstance(addresses, list) or len(addresses) == 0:
        return jsonify(error="Must provide at least one address"), 400

    if not GOOGLE_MAPS_API_KEY:
        return jsonify(error="Google Maps API key not configured on server"), 500
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    # Load camera data
    with open("camera_id_lat_lng_wiped.json", "r") as f:
        camera_data = json.load(f)
    
    # Create a unique directory for this request
    request_id = str(uuid.uuid4())
    img_dir = os.path.join("static", "imgs", request_id)
    os.makedirs(img_dir, exist_ok=True)
    
    # Clean up old request directories
    cleanup_old_dirs()

    stamp = int(time.time())
    all_nearby_cameras = {}

    # For each searched address, find nearby cameras around its location
    for addr in addresses:
        try:
            # Geocode the address to get its latitude and longitude
            geocode_result = gmaps.geocode(addr)
            if not geocode_result:
                print(f"[WARNING] Could not geocode address: {addr}")
                continue

            search_lat = geocode_result[0]['geometry']['location']['lat']
            search_lng = geocode_result[0]['geometry']['location']['lng']

            # Find nearby cameras around this geocoded location
            nearby_cameras = find_nearby_cameras(search_lat, search_lng, "camera_id_lat_lng_wiped.json")
            if nearby_cameras:
                # Merge with existing cameras (avoid duplicates)
                for camera_addr, camera_info in nearby_cameras.items():
                    if camera_addr not in all_nearby_cameras:
                        all_nearby_cameras[camera_addr] = camera_info
            


            else:
                print(f"[INFO] No cameras found near geocoded location for {addr}")

        except Exception as e:
            print(f"[ERROR] Failed to process {addr}: {e}")

    if not all_nearby_cameras:
        return jsonify(error="No cameras found near the searched addresses"), 404

    output = []
    
    # Process up to numCams cameras from all nearby results
    for addr, info in list(all_nearby_cameras.items())[:numCams]:
        try:
            img = fetch_and_save_image(info["camera_id"], stamp)
            if img and img.width > 640:
                h = img.height * 640 // img.width
                img = img.resize((640, h), Image.LANCZOS)

            if img:
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
            else:
                print(f"[ERROR] No image returned for {addr}")
        except Exception as e:
            print(f"[ERROR] Failed to fetch/process image for {addr}: {e}")

    if not output:
        return jsonify(error="No valid camera images could be retrieved"), 404
    
    print(output)

    return jsonify(images=output) 
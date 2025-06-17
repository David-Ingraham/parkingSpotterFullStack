import os
from dotenv import load_dotenv
import time
import json
import uuid
from flask import Blueprint, request, jsonify
from PIL import Image
from helpers.fetch_image import fetch_and_save_image
from routes.five_nearest import cleanup_old_dirs

# Load environment variables from .env file
load_dotenv()

bp = Blueprint('direct_camera_search', __name__)
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # Default to localhost if not set



@bp.post("/search_cameras")
def search_cameras():
    data = request.get_json()
    
    if not data or "addresses" not in data:
        return jsonify(error="No addresses provided"), 400
        
    addresses = data["addresses"]
    
    # Basic input validation
    if not isinstance(addresses, list) or len(addresses) > 5:
        return jsonify(error="Must provide 1-5 addresses as a list"), 400

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
    output = []

    # Process each address (assuming frontend sends exact matches)
    for addr in addresses:
        try:
            if addr in camera_data:
                # Get the camera ID
                camera_id = camera_data[addr]["camera_id"]
                
                # Fetch and process image
                try:
                    img = fetch_and_save_image(camera_id, stamp)
                    if img and img.width > 640:
                        h = img.height * 640 // img.width
                        img = img.resize((640, h), Image.LANCZOS)

                    if img:
                        filename = f"{stamp}_{addr.replace(' ', '_')}.jpg"
                        path = os.path.join(img_dir, filename)
                        print(f"[DEBUG] About to save image for {addr}. Image mode: {img.mode}, Size: {img.size}, Format: {img.format}")
                        try:
                            with open(path, 'wb') as f:
                                img.save(f, format="JPEG", quality=70, optimize=True)
                                f.flush()
                                os.fsync(f.fileno())
                            print(f"[DEBUG] Successfully saved image to {path}")
                        except Exception as e:
                            print(f"[ERROR] Failed to save image for {addr}: {e}")
                            continue

                        output.append({
                            "address": addr,
                            "url": f"{BASE_URL}/static/imgs/{request_id}/{filename}"
                        })
                    else:
                        print(f"[ERROR] No image returned for {addr}")
                except Exception as e:
                    print(f"[ERROR] Failed to fetch/process image for {addr}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed for {addr}: {e}")

    if not output:
        return jsonify(error="No valid cameras found"), 404

    return jsonify(images=output) 
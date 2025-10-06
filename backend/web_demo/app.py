import os
import json
import io
import sys
import time # Added for timestamp
from flask import Flask, jsonify, request, render_template, send_file
from PIL import Image
import requests

# Add the parent directory to the path to allow imports from `helpers`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers.fetch_image import fetch_and_save_image

from ultralytics import YOLO

# --- Model Loading (Robust Path) ---
# Get the absolute path to the directory containing this script (web_demo)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute path to the model file
model_path = os.path.join(script_dir, '..', 'model', 'weights.pt')
# Load the model using the absolute path, which is more reliable
model = YOLO(model_path)

app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Helper Functions ---

def get_camera_data():
    """Loads camera data from the JSON file."""
    try:
        # Corrected path to be relative to the backend/ directory
        with open('../camera_id_lat_lng_wiped.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: camera_id_lat_lng_wiped.json not found in backend/ directory.")
        return {}

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML page for the demo."""
    return render_template('index.html')

@app.route('/get_camera_names', methods=['GET'])
def get_camera_names():
    """Provides a list of camera names for autocomplete."""
    query = request.args.get('query', '').lower()
    camera_data = get_camera_data()
    
    if not query:
        return jsonify([])

    matches = []
    # Correctly iterate over the dictionary items
    for camera_name, info in camera_data.items():
        # The camera name is the KEY, not a value in the info dict.
        # We also need to replace underscores for user-friendly searching.
        searchable_name = camera_name.replace('_', ' ').lower()
        if query in searchable_name:
            matches.append({'id': info['camera_id'], 'name': camera_name.replace('_', ' ')})
            if len(matches) >= 15:  # Limit results for performance
                break
    
    return jsonify(matches)

@app.route('/detect_parking', methods=['GET'])
def detect_parking():
    """
    Fetches a live camera image, runs parking detection, 
    and returns the image with bounding boxes.
    """
    camera_id = request.args.get('camera_id')
    if not camera_id:
        return "Camera ID is required", 400

    # 1. Fetch the live image
    # Note: The base URL for camera images might need to be configured
    try:
        # Use the correct function name and add a timestamp
        timestamp = int(time.time())
        img = fetch_and_save_image(camera_id, timestamp)
        if not img:
            return "Failed to fetch image from camera.", 404
    except Exception as e:
        return f"Error fetching image: {e}", 500

    # 2. Run the model on the image
    results = model(img, verbose=False) # verbose=False for cleaner console
    processed_img = results[0].plot() # plot() draws the bounding boxes
    # Convert color format from BGR (used by OpenCV) to RGB (used by PIL)
    processed_img = Image.fromarray(processed_img[..., ::-1]) 

    # 3. Serve the image back to the frontend
    img_io = io.BytesIO()
    processed_img.save(img_io, 'JPEG', quality=85)
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
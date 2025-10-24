import json
import random
import time
from pathlib import Path
import sys
import os

# Add backend to Python path so we can import the helper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from helpers.fetch_image import fetch_and_save_image

def load_camera_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def download_test_images(num_images_per_batch=5, num_batches=6):
    # Load camera data
    camera_data = load_camera_data('../backend/camera_id_lat_lng_wiped.json')
    
    # Get all camera IDs
    cameras = [(location, data['camera_id']) 
              for location, data in camera_data.items()]
    
    # Create test_images directory if it doesn't exist
    base_dir = Path('test_images')
    base_dir.mkdir(exist_ok=True)
    
    for batch in range(num_batches):
        batch_dir = base_dir / f'batch_{batch + 1}'
        batch_dir.mkdir(exist_ok=True)
        
        # Select random cameras for this batch
        selected_cameras = random.sample(cameras, num_images_per_batch)
        
        print(f"\nDownloading batch {batch + 1}...")
        for i, (location, camera_id) in enumerate(selected_cameras, 1):
            print(f"  [{i}/{num_images_per_batch}] Downloading from {location}...")
            
            # Get current timestamp
            timestamp = int(time.time() * 1000)
            
            # Fetch image
            img = fetch_and_save_image(camera_id, timestamp)
            if img:
                # Save image
                save_path = batch_dir / f"{location}_{timestamp}.jpg"
                img.save(save_path, 'JPEG')
                print(f"    Saved to {save_path}")
            else:
                print(f"    Failed to download image from {location}")
            
            # Wait a bit between downloads to be nice to the API
            time.sleep(1)

if __name__ == "__main__":
    print("Starting to download test images...")
    download_test_images() 
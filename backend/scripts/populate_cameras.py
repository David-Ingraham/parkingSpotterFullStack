import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Camera

def populate_cameras():
    """Populate all cameras from JSON file into the database"""
    
    # Load camera data
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'camera_id_lat_lng_wiped.json')
    
    print(f"Loading camera data from: {json_path}")
    with open(json_path, 'r') as f:
        camera_data = json.load(f)
    
    print(f"Found {len(camera_data)} cameras in JSON file")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        added = 0
        updated = 0
        
        for address, info in camera_data.items():
            # Check if camera already exists
            existing = db.query(Camera).filter_by(address=address).first()
            
            if existing:
                # Update existing camera
                existing.camera_id = info['camera_id']
                existing.latitude = info['latitude']
                existing.longitude = info['longitude']
                updated += 1
            else:
                # Create new camera
                camera = Camera(
                    address=address,
                    camera_id=info['camera_id'],
                    latitude=info['latitude'],
                    longitude=info['longitude'],
                    last_status=None,
                    parked_cars_confidence=None,
                    open_parking_confidence=None
                )
                db.add(camera)
                added += 1
        
        db.commit()
        print(f"Successfully populated cameras: {added} added, {updated} updated")
        
    except Exception as e:
        db.rollback()
        print(f"Error populating cameras: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_cameras()

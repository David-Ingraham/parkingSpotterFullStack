import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List
from PIL import Image
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal
from database.models import Camera, Watcher, cleanup_expired_watchers, get_watched_cameras
from helpers.fetch_image import fetch_and_save_image
from helpers.push_notification import init_firebase, send_push_notification

# Import YOLO for vision model
from ultralytics import YOLO

# Configuration
POLL_INTERVAL = 15  # 5 minutes in seconds
MODEL_PATH = "model/weights.pt"
CONFIDENCE_CHANGE_THRESHOLD = 0.20  # 20% change threshold

class CameraWatcherService:
    def __init__(self):
        self.model = None
        print("Initializing Camera Watcher Service...")
        print("Initializing Firebase for push notifications...")
        init_firebase()
        
    def load_model(self):
        """Load the vision model"""
        print(f"Loading vision model from {MODEL_PATH}...")
        self.model = YOLO(MODEL_PATH)
        print("Vision model loaded successfully")
        
    def run_inference(self, image: Image.Image) -> Dict:
        """
        Run vision model on image and return predictions
        Returns dict with average confidences for each class
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Run inference with very low confidence threshold
        results = self.model(image, conf=0.01)
        
        # Parse predictions
        parked_cars_detections = []
        open_parking_detections = []
        
        for box in results[0].boxes:
            class_name = results[0].names[int(box.cls.item())]
            confidence = box.conf.item()
            
            if class_name == "parkedCars":
                parked_cars_detections.append(confidence)
            elif class_name == "openParking":
                open_parking_detections.append(confidence)
        
        # Calculate average confidences
        avg_parked_cars = sum(parked_cars_detections) / len(parked_cars_detections) if parked_cars_detections else 0.0
        avg_open_parking = sum(open_parking_detections) / len(open_parking_detections) if open_parking_detections else 0.0
        
        return {
            'parked_cars_confidence': avg_parked_cars,
            'open_parking_confidence': avg_open_parking,
            'parked_cars_count': len(parked_cars_detections),
            'open_parking_count': len(open_parking_detections)
        }
    
    def determine_status(self, parked_cars_conf: float, open_parking_conf: float) -> str:
        """
        Determine camera status based on detections
        Returns: "none", "parked_cars", "open_parking", or "both"
        """
        has_parked_cars = parked_cars_conf > 0
        has_open_parking = open_parking_conf > 0
        
        if has_parked_cars and has_open_parking:
            return "both"
        elif has_parked_cars:
            return "parked_cars"
        elif has_open_parking:
            return "open_parking"
        else:
            return "none"
    
    def should_notify(self, camera: Camera, new_status: str) -> bool:
        """
        Determine if we should notify watchers based on status change
        """
        # If camera was never scanned (last_status is None), notify on first scan
        if camera.last_status is None:
            return True
        
        # If status changed, notify
        if camera.last_status != new_status:
            return True
        
        return False
    
    def notify_watchers(self, camera_address: str, new_status: str):
        """
        Send push notifications to all watchers of this camera
        """
        db = SessionLocal()
        
        try:
            # Get all watchers for this camera with push tokens
            watchers = db.query(Watcher).filter_by(
                camera_address=camera_address
            ).filter(
                Watcher.expires_at > datetime.now(timezone.utc),
                Watcher.push_token.isnot(None)
            ).all()
            
            if not watchers:
                print(f"  No watchers with push tokens for {camera_address}")
                return
            
            # Format status for user-friendly notification
            status_messages = {
                'none': 'No parking detected',
                'parked_cars': 'Only parked cars visible',
                'open_parking': 'Open parking spots available!',
                'both': 'Mixed - some spots available'
            }
            
            title = 'Parking Update'
            body = f'{camera_address}: {status_messages.get(new_status, new_status)}'
            
            success_count = 0
            failed_watcher_ids = []
            
            for watcher in watchers:
                data = {
                    'camera_address': camera_address,
                    'status': new_status,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                success = send_push_notification(
                    watcher.push_token,
                    title,
                    body,
                    data
                )
                
                if success:
                    success_count += 1
                else:
                    # Mark token as invalid
                    failed_watcher_ids.append(watcher.id)
            
            # Clean up invalid tokens
            if failed_watcher_ids:
                db.query(Watcher).filter(Watcher.id.in_(failed_watcher_ids)).update(
                    {Watcher.push_token: None},
                    synchronize_session=False
                )
                db.commit()
                print(f"  Removed {len(failed_watcher_ids)} invalid push tokens")
            
            print(f"  Sent {success_count} push notifications for {camera_address}")
            
        except Exception as e:
            print(f"  Error notifying watchers: {e}")
        finally:
            db.close()
    
    def process_camera(self, camera: Camera, db):
        """Process a single camera: fetch image, run model, update status"""
        try:
            print(f"Processing camera: {camera.address}")
            
            # Fetch image
            timestamp = int(time.time() * 1000)
            image = fetch_and_save_image(camera.camera_id, timestamp)
            
            if image is None:
                print(f"Failed to fetch image for {camera.address}")
                return
            
            # Run inference
            predictions = self.run_inference(image)
            
            parked_cars_conf = predictions['parked_cars_confidence']
            open_parking_conf = predictions['open_parking_confidence']
            
            print(f"  Parked cars: {predictions['parked_cars_count']} detections, avg conf: {parked_cars_conf:.3f}")
            print(f"  Open parking: {predictions['open_parking_count']} detections, avg conf: {open_parking_conf:.3f}")
            
            # Determine new status
            new_status = self.determine_status(parked_cars_conf, open_parking_conf)
            print(f"  Status: {camera.last_status} -> {new_status}")
            
            # Check if we should notify
            if self.should_notify(camera, new_status):
                print(f"  STATUS CHANGED - Sending push notifications")
                self.notify_watchers(camera.address, new_status)
            else:
                print(f"  No change - No notification")
            
            # Update camera in database
            camera.last_status = new_status
            camera.parked_cars_confidence = parked_cars_conf
            camera.open_parking_confidence = open_parking_conf
            db.commit()
            
        except Exception as e:
            print(f"Error processing camera {camera.address}: {e}")
            db.rollback()
    
    def poll_cameras(self):
        """Main polling loop - checks all watched cameras"""
        db = SessionLocal()
        
        try:
            # Clean up expired watchers
            cleanup_expired_watchers(db)
            
            # Get all cameras with active watchers
            watched_cameras = get_watched_cameras(db)
            
            if not watched_cameras:
                print("No cameras being watched")
                return
            
            print(f"Found {len(watched_cameras)} cameras being watched")
            
            # Process each camera
            for camera in watched_cameras:
                self.process_camera(camera, db)
                
        except Exception as e:
            print(f"Error in poll_cameras: {e}")
        finally:
            db.close()
    
    def run(self):
        """Main service loop"""
        print("Camera Watcher Service starting...")
        self.load_model()
        
        print(f"Starting polling loop (every {POLL_INTERVAL} seconds)")
        
        while True:
            try:
                print(f"\n[{datetime.now(timezone.utc).isoformat()}] Starting camera poll")
                self.poll_cameras()
                print(f"Poll complete. Sleeping for {POLL_INTERVAL} seconds...\n")
                time.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nShutting down Camera Watcher Service...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                print("Continuing...")
                time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    service = CameraWatcherService()
    service.run()

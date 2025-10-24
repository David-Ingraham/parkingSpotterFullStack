"""
Camera Scanner Module
Handles parallel scanning of multiple cameras
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional
from datetime import datetime
from utils.fetch_image import fetch_and_save_image
from model_inference import ParkingDetector

class CameraScanner:
    """Manages parallel scanning of traffic cameras"""
    
    def __init__(self, camera_data_path: str, model_path: str, max_workers: int = 8):
        """
        Initialize the camera scanner
        
        Args:
            camera_data_path: Path to manhattan_cameras.json
            model_path: Path to YOLO model weights
            max_workers: Number of parallel scanning threads
        """
        self.camera_data_path = camera_data_path
        self.max_workers = max_workers
        
        # Load camera data
        print(f"Loading camera data from {camera_data_path}...")
        with open(camera_data_path, 'r') as f:
            self.cameras = json.load(f)
        print(f"Loaded {len(self.cameras)} cameras")
        
        # Initialize model
        self.detector = ParkingDetector(model_path)
        
    def scan_single_camera(self, address: str, camera_data: Dict) -> Optional[Dict]:
        """
        Scan a single camera
        
        Args:
            address: Camera address/name
            camera_data: Dict with camera_id, latitude, longitude
            
        Returns:
            Dict with scan results or None if failed
        """
        try:
            camera_id = camera_data['camera_id']
            timestamp = int(time.time() * 1000)
            
            # Fetch image
            image = fetch_and_save_image(camera_id, timestamp)
            
            if image is None:
                print(f"[WARN] Failed to fetch image for {address}")
                return None
            
            # Run model inference
            predictions = self.detector.run_inference(image)
            status = self.detector.determine_status(predictions)
            
            # Build result
            result = {
                'address': address,
                'camera_id': camera_id,
                'latitude': camera_data['latitude'],
                'longitude': camera_data['longitude'],
                'status': status,
                'parked_cars_confidence': round(predictions['parked_cars_confidence'], 3),
                'open_parking_confidence': round(predictions['open_parking_confidence'], 3),
                'parked_cars_count': predictions['parked_cars_count'],
                'open_parking_count': predictions['open_parking_count'],
                'last_scanned': datetime.utcnow().isoformat() + 'Z'
            }
            
            print(f"[OK] {address}: {status} (parked: {predictions['parked_cars_count']}, open: {predictions['open_parking_count']})")
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to scan {address}: {e}")
            return None
    
    def scan_all_cameras(self) -> Dict[str, Dict]:
        """
        Scan all cameras in parallel
        
        Returns:
            Dict mapping camera address to scan results
        """
        print(f"\n{'='*60}")
        print(f"Starting scan of {len(self.cameras)} cameras with {self.max_workers} workers")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        results = {}
        successful = 0
        failed = 0
        
        # Scan cameras in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_address = {
                executor.submit(self.scan_single_camera, address, data): address
                for address, data in self.cameras.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_address):
                address = future_to_address[future]
                try:
                    result = future.result()
                    if result:
                        results[address] = result
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"[ERROR] Exception scanning {address}: {e}")
                    failed += 1
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"Scan complete!")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print(f"Successful: {successful}/{len(self.cameras)}")
        print(f"Failed: {failed}/{len(self.cameras)}")
        print(f"Average: {elapsed/len(self.cameras):.2f} sec/camera")
        print(f"{'='*60}\n")
        
        return results


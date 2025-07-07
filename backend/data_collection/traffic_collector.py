import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule
from tqdm import tqdm
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_setup import create_database, insert_car_count, insert_batch_status
from email_notifications import send_failure_alert, send_startup_notification
from helpers.fetch_image import fetch_and_save_image

# Configuration
CAMERA_DATA_FILE = "../camera_id_lat_lng_wiped.json"
PROCESSING_INTERVAL = 15  # minutes
MAX_CONCURRENT_CAMERAS = 8
ERROR_THRESHOLD = 0.10
MODEL_PATH = "yolov8l.pt"

class TrafficDataCollector:
    def __init__(self):
        self.model = None
        self.camera_data = {}
        self.setup_logging()
        self.load_camera_data()
        
    def setup_logging(self):
        """Setup logging"""
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def load_camera_data(self):
        """Load camera data from JSON file"""
        try:
            camera_file = os.path.join(os.path.dirname(__file__), CAMERA_DATA_FILE)
            with open(camera_file, 'r') as f:
                self.camera_data = json.load(f)
            self.logger.info(f"Loaded {len(self.camera_data)} cameras")
        except Exception as e:
            self.logger.error(f"Failed to load camera data: {str(e)}")
            raise
    
    def initialize_model(self):
        """Initialize YOLOv8 model"""
        try:
            self.logger.info("Initializing YOLOv8 model...")
            self.model = YOLO(MODEL_PATH)
            self.logger.info("YOLOv8 model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize YOLOv8 model: {str(e)}")
            raise
    
    def fetch_camera_image(self, camera_id):
        """Fetch image from camera using existing function"""
        try:
            timestamp = int(time.time())
            image = fetch_and_save_image(camera_id, timestamp)
            return image
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch camera {camera_id}: {str(e)}")
            return None
    
    def count_cars_in_image(self, image):
        """Count cars in image using YOLOv8"""
        try:
            # Convert RGBA to RGB if needed
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            img_array = np.array(image)
            results = self.model(img_array, verbose=False)
            
            # Count vehicles (cars, trucks, buses, motorcycles)
            vehicle_classes = [2, 3, 5, 7]  # COCO dataset class IDs
            car_count = 0
            max_confidence = 0
            
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    
                    if class_id in vehicle_classes and confidence > 0.5:
                        car_count += 1
                        max_confidence = max(max_confidence, confidence)
            
            return car_count, max_confidence
            
        except Exception as e:
            self.logger.error(f"Error counting cars: {str(e)}")
            return 0, 0.0
    
    def process_single_camera(self, camera_address, camera_info):
        """Process a single camera"""
        start_time = time.time()
        
        try:
            # Skip cameras without coordinates
            if not camera_info.get('latitude') or not camera_info.get('longitude'):
                return None
            
            # Fetch image
            image = self.fetch_camera_image(camera_info['camera_id'])
            if image is None:
                return {'camera_address': camera_address, 'success': False, 'error': 'Failed to fetch image'}
            
            # Count cars
            car_count, confidence = self.count_cars_in_image(image)
            processing_time = time.time() - start_time
            
            # Save to database
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_car_count(camera_address, timestamp, car_count, confidence, processing_time)
            
            return {
                'camera_address': camera_address,
                'success': True,
                'car_count': car_count,
                'confidence': confidence,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Error processing {camera_address}: {str(e)}")
            return {
                'camera_address': camera_address,
                'success': False,
                'error': str(e),
                'processing_time': processing_time
            }
    
    def process_camera_batch(self):
        """Process all cameras in parallel"""
        batch_start_time = time.time()
        batch_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.logger.info(f"Starting batch processing at {batch_timestamp}")
        
        cameras_to_process = list(self.camera_data.items())
        successful_cameras = []
        failed_cameras = []
        
        # Process cameras in parallel
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CAMERAS) as executor:
            future_to_camera = {
                executor.submit(self.process_single_camera, addr, info): addr
                for addr, info in cameras_to_process
            }
            
            for future in tqdm(as_completed(future_to_camera), 
                             total=len(cameras_to_process), 
                             desc="Processing cameras"):
                camera_address = future_to_camera[future]
                try:
                    result = future.result()
                    if result is None:
                        continue
                        
                    if result['success']:
                        successful_cameras.append(result)
                        self.logger.debug(f"SUCCESS {camera_address}: {result['car_count']} cars")
                    else:
                        failed_cameras.append(camera_address)
                        self.logger.warning(f"FAILED {camera_address}: {result['error']}")
                        
                except Exception as e:
                    failed_cameras.append(camera_address)
                    self.logger.error(f"ERROR {camera_address}: {str(e)}")
        
        # Statistics
        total_cameras = len(cameras_to_process)
        cameras_processed = len(successful_cameras)
        cameras_failed = len(failed_cameras)
        batch_processing_time = time.time() - batch_start_time
        
        # Save batch status
        status = "completed" if cameras_failed == 0 else "partial"
        insert_batch_status(batch_timestamp, cameras_processed, cameras_failed, 
                          total_cameras, batch_processing_time, status)
        
        # Check failure rate
        failure_rate = cameras_failed / total_cameras if total_cameras > 0 else 0
        if failure_rate > ERROR_THRESHOLD:
            error_details = f"Failed cameras: {failed_cameras[:10]}"
            send_failure_alert(cameras_failed, total_cameras, error_details)
        
        self.logger.info(f"Batch complete: {cameras_processed}/{total_cameras} cameras processed "
                        f"({failure_rate:.1%} failure rate) in {batch_processing_time:.1f}s")
        
        return cameras_processed, cameras_failed
    
    def run_continuous_collection(self):
        """Run continuous data collection"""
        self.logger.info("Starting continuous traffic data collection...")
        
        # Initialize model
        self.initialize_model()
        
        # Send startup notification
        send_startup_notification()
        
        # Schedule batch processing
        schedule.every(PROCESSING_INTERVAL).minutes.do(self.process_camera_batch)
        
        # Run initial batch
        self.logger.info("Running initial batch...")
        self.process_camera_batch()
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                self.logger.info("Stopping data collection...")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                time.sleep(300)

def main():
    """Main function"""
    print("Parking Spotter - Traffic Data Collection System")
    print("=" * 50)
    
    # Create database
    create_database()
    
    # Create collector instance
    collector = TrafficDataCollector()
    
    # Start continuous collection
    collector.run_continuous_collection()

if __name__ == "__main__":
    main() 
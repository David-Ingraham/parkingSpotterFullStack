#!/usr/bin/env python3
"""
Camera Health Check Tool
Tests the health and reliability of NYC traffic cameras with rate limiting.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
import io

# Add backend directory to path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from helpers.fetch_image import fetch_and_save_image

# Configuration
RESULTS_DIR = Path(__file__).parent / "results"
CAMERA_DATA_FILE = Path(__file__).parent.parent.parent / "camera_id_lat_lng_wiped.json"
REQUEST_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # exponential backoff multiplier

class CameraHealthCheck:
    def __init__(self):
        self.setup_logging()
        self.load_camera_data()
        self.setup_results_dir()
        
    def setup_logging(self):
        """Configure logging"""
        log_dir = RESULTS_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"health_check_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_results_dir(self):
        """Create results directory structure"""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_camera_data(self):
        """Load camera data from JSON file"""
        try:
            with open(CAMERA_DATA_FILE, 'r') as f:
                self.camera_data = json.load(f)
            self.logger.info(f"Loaded {len(self.camera_data)} cameras")
        except Exception as e:
            self.logger.error(f"Failed to load camera data: {str(e)}")
            raise

    def validate_image(self, image_data):
        """
        Validate that the response is actually an image and meets minimum requirements
        Returns: (is_valid, details)
        """
        try:
            # Try to open the image data
            img = Image.open(io.BytesIO(image_data))
            
            # Check image size (traffic cam images should be reasonably large)
            width, height = img.size
            if width < 300 or height < 200:
                return False, "Image too small"
                
            # Check file size (real images usually > 50KB)
            if len(image_data) < 50000:
                return False, "File too small"
                
            return True, f"Valid image: {width}x{height}, {len(image_data)/1024:.1f}KB"
            
        except Exception as e:
            return False, f"Invalid image: {str(e)}"

    def test_single_camera(self, camera_id, camera_info):
        """Test a single camera with retries and backoff"""
        delay = REQUEST_DELAY
        
        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                
                # Fetch image using existing function
                image = fetch_and_save_image(camera_id, int(time.time()))
                
                if image is None:
                    raise Exception("Failed to fetch image")
                    
                # Convert PIL Image to bytes for validation
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format or 'JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Validate image
                is_valid, details = self.validate_image(img_byte_arr)
                if not is_valid:
                    raise Exception(f"Image validation failed: {details}")
                
                response_time = time.time() - start_time
                
                return {
                    'success': True,
                    'response_time': response_time,
                    'details': details
                }
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for camera {camera_id}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay)
                    delay *= BACKOFF_FACTOR
                else:
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            finally:
                # Always wait between requests, even after failures
                time.sleep(REQUEST_DELAY)
                
        return {'success': False, 'error': 'Max retries exceeded'}

    def phase1_quick_check(self):
        """
        Phase 1: Quick status check of all cameras
        Returns: dict of camera results
        """
        self.logger.info("Starting Phase 1: Quick Status Check")
        results = {}
        
        for camera_address, camera_info in self.camera_data.items():
            self.logger.info(f"Testing camera: {camera_address}")
            result = self.test_single_camera(camera_info['camera_id'], camera_info)
            results[camera_address] = result
            
        return results

    def phase2_reliability_check(self, working_cameras):
        """
        Phase 2: Detailed reliability check of working cameras
        """
        self.logger.info("Starting Phase 2: Reliability Check")
        results = {}
        
        for camera_address, camera_info in working_cameras.items():
            self.logger.info(f"Running reliability test for: {camera_address}")
            camera_results = []
            
            for i in range(5):  # 5 tests per camera
                result = self.test_single_camera(camera_info['camera_id'], camera_info)
                camera_results.append(result)
                
            # Calculate reliability stats
            successes = sum(1 for r in camera_results if r['success'])
            success_rate = successes / len(camera_results)
            
            if successes > 0:
                avg_response_time = sum(r['response_time'] for r in camera_results if r['success']) / successes
            else:
                avg_response_time = None
                
            results[camera_address] = {
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'test_results': camera_results
            }
            
        return results

    def run_health_check(self):
        """Run the complete two-phase health check"""
        start_time = time.time()
        
        # Phase 1: Quick Check
        phase1_results = self.phase1_quick_check()
        
        # Filter working cameras for Phase 2
        working_cameras = {
            addr: info for addr, info in self.camera_data.items()
            if phase1_results.get(addr, {}).get('success', False)
        }
        
        self.logger.info(f"Phase 1 complete. {len(working_cameras)} working cameras found.")
        
        # Phase 2: Reliability Check
        phase2_results = self.phase2_reliability_check(working_cameras)
        
        # Compile final report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_cameras': len(self.camera_data),
            'working_cameras': len(working_cameras),
            'dead_cameras': len(self.camera_data) - len(working_cameras),
            'runtime': time.time() - start_time,
            'phase1_results': phase1_results,
            'phase2_results': phase2_results
        }
        
        # Save report
        report_file = RESULTS_DIR / f"report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        latest_file = RESULTS_DIR / "latest_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Health check complete. Report saved to {report_file}")
        return report

def main():
    try:
        checker = CameraHealthCheck()
        report = checker.run_health_check()
        
        # Print summary
        print("\nHealth Check Summary:")
        print(f"Total Cameras: {report['total_cameras']}")
        print(f"Working Cameras: {report['working_cameras']}")
        print(f"Dead Cameras: {report['dead_cameras']}")
        print(f"Runtime: {report['runtime']:.1f} seconds")
        print(f"\nFull report saved to: {RESULTS_DIR}/latest_report.json")
        
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
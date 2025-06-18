#!/usr/bin/env python3
"""
Comprehensive test script for configurable camera count feature.
Tests both /fiveNearest and /search_cameras endpoints with various numCams values.
Logs all responses and saves photos for validation.
"""

import requests
import json
import os
import time
from datetime import datetime
import urllib.parse
from PIL import Image
import io

# Configuration
BASE_URL = "http://localhost:8000"
PHOTOS_DIR = "test_photos/configurable_cameras"
LOG_FILE = "test_photos/configurable_cameras_test.log"

class TestLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

def setup_test_environment():
    """Create test directories and clean up old files"""
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    
    # Clean up old test photos
    for file in os.listdir(PHOTOS_DIR):
        if file.endswith(('.jpg', '.jpeg', '.png')):
            os.remove(os.path.join(PHOTOS_DIR, file))
    
    # Initialize log file
    with open(LOG_FILE, "w") as f:
        f.write(f"=== Configurable Cameras Test Started at {datetime.now()} ===\n\n")

def download_and_save_image(url, filename):
    """Download image from URL and save to test folder"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(PHOTOS_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Validate image
            try:
                with Image.open(filepath) as img:
                    return True, f"Saved {filename} ({img.size[0]}x{img.size[1]}, {img.format})"
            except Exception as e:
                return False, f"Invalid image {filename}: {e}"
        else:
            return False, f"Failed to download {filename}: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error downloading {filename}: {e}"

def test_five_nearest_endpoint(logger):
    """Test /fiveNearest endpoint with various numCams values"""
    logger.log("=" * 60)
    logger.log("TESTING /fiveNearest ENDPOINT")
    logger.log("=" * 60)
    
    # Test coordinates (Times Square area)
    test_lat, test_lng = 40.7589, -73.9851
    
    test_cases = [
        {"numCams": 1, "description": "Single camera"},
        {"numCams": 3, "description": "Three cameras"},
        {"numCams": 5, "description": "Default five cameras"},
        {"numCams": 8, "description": "Maximum eight cameras"},
        {"numCams": "6", "description": "String input (should convert)"},
        {"description": "No numCams (should default to 5)"},
        {"numCams": 10, "description": "Over limit (should fail)", "should_fail": True},
        {"numCams": "abc", "description": "Invalid string (should fail)", "should_fail": True},
        {"numCams": 0, "description": "Zero cameras (should fail)", "should_fail": True},
    ]
    
    for i, test_case in enumerate(test_cases):
        logger.log(f"\nTest {i+1}: {test_case['description']}")
        
        payload = {"lat": test_lat, "lng": test_lng}
        if "numCams" in test_case:
            payload["numCams"] = test_case["numCams"]
        
        try:
            response = requests.post(
                f"{BASE_URL}/fiveNearest",
                json=payload,
                timeout=30
            )
            
            should_fail = test_case.get("should_fail", False)
            
            if should_fail:
                if response.status_code != 200:
                    logger.log(f"✅ Expected failure: {response.status_code} - {response.json().get('error', 'Unknown error')}")
                else:
                    logger.log(f"❌ Should have failed but got: {response.status_code}")
            else:
                if response.status_code == 200:
                    data = response.json()
                    images = data.get("images", [])
                    logger.log(f"✅ Success: Got {len(images)} images")
                    
                    # Download and save images
                    for j, image_data in enumerate(images):
                        address = image_data.get("address", f"unknown_{j}")
                        filename = f"five_nearest_test{i+1}_{j+1}_{address.replace(' ', '_')}.jpg"
                        
                        success, message = download_and_save_image(image_data["url"], filename)
                        if success:
                            logger.log(f"  📷 {message}")
                        else:
                            logger.log(f"  ❌ {message}", "ERROR")
                else:
                    logger.log(f"❌ Failed: {response.status_code} - {response.text[:200]}", "ERROR")
                    
        except Exception as e:
            logger.log(f"❌ Exception: {e}", "ERROR")
        
        time.sleep(1)  # Be nice to the server

def test_search_cameras_endpoint(logger):
    """Test /search_cameras endpoint with various numCams values"""
    logger.log("\n" + "=" * 60)
    logger.log("TESTING /search_cameras ENDPOINT")
    logger.log("=" * 60)
    
    test_cases = [
        {
            "addresses": ["1_Ave_57_st"],
            "numCams": 1,
            "description": "Single camera from single address"
        },
        {
            "addresses": ["1_Ave_57_st"],
            "numCams": 4,
            "description": "Four cameras from single address"
        },
        {
            "addresses": ["1_Ave_57_st", "Broadway_46_St-_Quad_North"],
            "numCams": 6,
            "description": "Six cameras from two addresses"
        },
        {
            "addresses": ["5_Ave_46_St"],
            "numCams": 8,
            "description": "Maximum eight cameras"
        },
        {
            "addresses": ["10_Ave_42_St"],
            "numCams": "5",
            "description": "String input (should convert)"
        },
        {
            "addresses": ["2_Ave_42_St"],
            "description": "No numCams (should default to 5)"
        },
        {
            "addresses": ["3_Ave_42_St"],
            "numCams": 15,
            "description": "Over limit (should fail)",
            "should_fail": True
        },
        {
            "addresses": ["FAKE_ADDRESS_THAT_DOESNT_EXIST"],
            "numCams": 5,
            "description": "Invalid address (should fail gracefully)",
            "should_fail": True
        },
    ]
    
    for i, test_case in enumerate(test_cases):
        logger.log(f"\nTest {i+1}: {test_case['description']}")
        
        payload = {"addresses": test_case["addresses"]}
        if "numCams" in test_case:
            payload["numCams"] = test_case["numCams"]
        
        try:
            response = requests.post(
                f"{BASE_URL}/search_cameras",
                json=payload,
                timeout=30
            )
            
            should_fail = test_case.get("should_fail", False)
            
            if should_fail:
                if response.status_code != 200:
                    logger.log(f"✅ Expected failure: {response.status_code} - {response.json().get('error', 'Unknown error')}")
                else:
                    data = response.json()
                    images = data.get("images", [])
                    if len(images) == 0:
                        logger.log(f"✅ Expected failure: Got empty results")
                    else:
                        logger.log(f"❓ Unexpected success: Got {len(images)} images")
            else:
                if response.status_code == 200:
                    data = response.json()
                    images = data.get("images", [])
                    logger.log(f"✅ Success: Got {len(images)} images")
                    
                    # Download and save images
                    for j, image_data in enumerate(images):
                        address = image_data.get("address", f"unknown_{j}")
                        filename = f"search_cameras_test{i+1}_{j+1}_{address.replace(' ', '_')}.jpg"
                        
                        success, message = download_and_save_image(image_data["url"], filename)
                        if success:
                            logger.log(f"  📷 {message}")
                        else:
                            logger.log(f"  ❌ {message}", "ERROR")
                else:
                    logger.log(f"❌ Failed: {response.status_code} - {response.text[:200]}", "ERROR")
                    
        except Exception as e:
            logger.log(f"❌ Exception: {e}", "ERROR")
        
        time.sleep(1)  # Be nice to the server

def test_performance(logger):
    """Test performance with different camera counts"""
    logger.log("\n" + "=" * 60)
    logger.log("PERFORMANCE TESTING")
    logger.log("=" * 60)
    
    test_cases = [1, 3, 5, 8]
    
    for num_cams in test_cases:
        logger.log(f"\nTesting performance with {num_cams} cameras...")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/fiveNearest",
                json={"lat": 40.7589, "lng": -73.9851, "numCams": num_cams},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                data = response.json()
                images = data.get("images", [])
                logger.log(f"✅ {num_cams} cameras: {duration:.2f}s, got {len(images)} images")
            else:
                logger.log(f"❌ {num_cams} cameras: Failed with {response.status_code}")
                
        except Exception as e:
            logger.log(f"❌ {num_cams} cameras: Exception - {e}")

def main():
    """Run all tests"""
    print("🦕 Starting Configurable Cameras Test Suite...")
    
    setup_test_environment()
    logger = TestLogger(LOG_FILE)
    
    logger.log("Starting comprehensive test of configurable camera endpoints")
    logger.log(f"Base URL: {BASE_URL}")
    logger.log(f"Photos will be saved to: {PHOTOS_DIR}")
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        logger.log("✅ Server connectivity confirmed")
    except Exception as e:
        logger.log(f"❌ Cannot connect to server: {e}", "ERROR")
        logger.log("Make sure your backend is running with: python main.py")
        return
    
    # Run all tests
    test_five_nearest_endpoint(logger)
    test_search_cameras_endpoint(logger)
    test_performance(logger)
    
    # Summary
    logger.log("\n" + "=" * 60)
    logger.log("TEST SUMMARY")
    logger.log("=" * 60)
    
    # Count saved photos
    photo_count = len([f for f in os.listdir(PHOTOS_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))])
    logger.log(f"📷 Total photos saved: {photo_count}")
    logger.log(f"📁 Photos location: {os.path.abspath(PHOTOS_DIR)}")
    logger.log(f"📄 Full log: {os.path.abspath(LOG_FILE)}")
    
    print(f"\n🦖 Test completed! Check {photo_count} photos in {PHOTOS_DIR}")
    print(f"🦕 Full log available in {LOG_FILE}")

if __name__ == "__main__":
    main() 
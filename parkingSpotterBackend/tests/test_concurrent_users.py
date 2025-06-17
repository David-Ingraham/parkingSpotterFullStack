import asyncio
import aiohttp
import json
import time
import shutil
from urllib.parse import urlparse
from pathlib import Path

# Create a constant for the test photos directory
TEST_PHOTOS_DIR = Path(__file__).parent / "test_photos"

# Server configuration
SERVER_URL = "http://localhost:8000"  # Use localhost for local testing

async def download_image(session, url, save_path):
    """Download an image from URL and save it to path"""
    # Replace 10.0.2.2 with localhost for local testing
    url = url.replace("10.0.2.2", "localhost")
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to download image {url}: Status {response.status}")
            return False
        
        with open(save_path, "wb") as f:
            f.write(await response.read())
        return True

async def simulate_user_request(session, user_id, lat, lng):
    """Simulate a single user making a request"""
    print(f"User {user_id} starting request...")
    
    try:
        async with session.post(
            f"{SERVER_URL}/fiveNearest",
            json={"lat": lat, "lng": lng},
            timeout=aiohttp.ClientTimeout(total=10)  # Add 10 second timeout
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"User {user_id} got error {response.status}")
                print(f"Error details: {error_text}")
                return None
                
            data = await response.json()
            
            if "images" not in data:
                print(f"User {user_id} got no images in response")
                return None
                
            # Extract request_id from first URL
            first_url = data["images"][0]["url"]
            url_path = urlparse(first_url).path
            request_id = Path(url_path).parts[-2]  # Get the UUID directory name
            
            # Create user's test directory
            user_dir = TEST_PHOTOS_DIR / f"user_{user_id}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Download all images
            download_tasks = []
            for idx, img in enumerate(data["images"]):
                save_path = user_dir / f"photo_{idx}.jpg"
                download_tasks.append(download_image(session, img["url"], save_path))
            
            # Wait for all downloads to complete
            download_results = await asyncio.gather(*download_tasks)
            successful_downloads = sum(1 for r in download_results if r)
            
            print(f"User {user_id} got {len(data['images'])} images with request_id: {request_id}")
            print(f"User {user_id} successfully downloaded {successful_downloads} images")
            
            return {
                "request_id": request_id,
                "total_images": len(data["images"]),
                "downloaded": successful_downloads
            }
    except Exception as e:
        print(f"User {user_id} encountered error: {str(e)}")
        return None

async def main():
    # Clear and create test photos directory
    if TEST_PHOTOS_DIR.exists():
        shutil.rmtree(TEST_PHOTOS_DIR)
    TEST_PHOTOS_DIR.mkdir(parents=True)
    
    # Test locations (slightly different for each user to simulate real usage)
    locations = [
        {"lat": 40.7128, "lng": -74.0060},  # New York
        {"lat": 40.7129, "lng": -74.0061},  # Slightly offset
        {"lat": 40.7127, "lng": -74.0059},  # Slightly offset
        {"lat": 40.7130, "lng": -74.0062},  # Slightly offset
    ]
    
    print("\nStarting concurrent user test...")
    print("================================")
    print(f"Test photos will be saved to: {TEST_PHOTOS_DIR}")
    
    async with aiohttp.ClientSession() as session:
        # Make requests concurrently
        tasks = [
            simulate_user_request(session, i, loc["lat"], loc["lng"])
            for i, loc in enumerate(locations)
        ]
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks)
        
        # Filter out failed requests
        valid_results = [r for r in results if r is not None]
        
        print("\nTest Results:")
        print("============")
        print(f"Total requests: {len(locations)}")
        print(f"Successful requests: {len(valid_results)}")
        
        # Detailed results
        print("\nDetailed Results:")
        print("================")
        for i, result in enumerate(results):
            if result:
                print(f"User {i}: Got {result['total_images']} images, "
                      f"Downloaded {result['downloaded']} successfully")
            else:
                print(f"User {i}: Failed")
        
        # Check server-side directories
        print("\nServer-side directories:")
        print("=======================")
        for result in valid_results:
            img_dir = Path("static/imgs") / result["request_id"]
            if img_dir.exists():
                images = list(img_dir.glob("*.jpg"))
                print(f"Directory {result['request_id']}: {len(images)} images")
            else:
                print(f"Directory {result['request_id']}: Not found!")
        
        # Summary of downloaded files
        print("\nDownloaded files:")
        print("================")
        for user_dir in TEST_PHOTOS_DIR.glob("user_*"):
            photos = list(user_dir.glob("*.jpg"))
            print(f"{user_dir.name}: {len(photos)} photos downloaded")

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"\nTotal test time: {time.time() - start_time:.2f} seconds") 
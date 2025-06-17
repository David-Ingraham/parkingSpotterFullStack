import asyncio
import aiohttp
import json
import time
from pathlib import Path

# Create a constant for the test photos directory
TEST_PHOTOS_DIR = Path(__file__).parent / "test_photos"

async def simulate_user_request(session, user_id, addresses):
    """Simulate a single user making a request"""
    print(f"User {user_id} starting request...")
    
    try:
        async with session.post(
            "http://localhost:8000/search_cameras",
            json={"addresses": addresses},
            timeout=aiohttp.ClientTimeout(total=10)
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
            
            # Create user's test directory
            user_dir = TEST_PHOTOS_DIR / f"user_{user_id}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Download all images
            for idx, img in enumerate(data["images"]):
                try:
                    url = img["url"].replace("10.0.2.2", "localhost")
                    async with session.get(url) as img_response:
                        if img_response.status == 200:
                            save_path = user_dir / f"photo_{idx}.jpg"
                            with open(save_path, "wb") as f:
                                f.write(await img_response.read())
                except Exception as e:
                    print(f"User {user_id} failed to download image {idx}: {e}")
            
            print(f"User {user_id} got {len(data['images'])} images")
            return {
                "requested": len(addresses),
                "received": len(data["images"])
            }
            
    except Exception as e:
        print(f"User {user_id} encountered error: {str(e)}")
        return None

async def main():
    # Test data - each user requests different addresses
    test_cases = [
        ["10 Ave W 34 St", "2 Ave 42 St"],
        ["11 Ave W 42 St", "12 Ave 34 St"],
        ["5 Ave 42 St", "7 Ave 34 St"],
        ["8 Ave 42 St", "9 Ave 34 St"]
    ]
    
    print("\nStarting concurrent camera search test...")
    print("=====================================")
    
    # Clear and create test directory
    if TEST_PHOTOS_DIR.exists():
        for file in TEST_PHOTOS_DIR.glob("**/*"):
            if file.is_file():
                file.unlink()
        for dir in TEST_PHOTOS_DIR.glob("user_*"):
            if dir.is_dir():
                dir.rmdir()
    TEST_PHOTOS_DIR.mkdir(exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            simulate_user_request(session, i, addresses)
            for i, addresses in enumerate(test_cases)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        print("\nTest Results:")
        print("============")
        print(f"Total users: {len(test_cases)}")
        print(f"Successful requests: {len([r for r in results if r is not None])}")
        
        print("\nDetailed Results:")
        print("================")
        for i, result in enumerate(results):
            if result:
                print(f"User {i}: Requested {result['requested']} cameras, "
                      f"received {result['received']} images")
            else:
                print(f"User {i}: Failed")
        
        # Check downloaded files
        print("\nDownloaded Files:")
        print("================")
        for user_dir in TEST_PHOTOS_DIR.glob("user_*"):
            photos = list(user_dir.glob("*.jpg"))
            print(f"{user_dir.name}: {len(photos)} photos downloaded")

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"\nTotal test time: {time.time() - start_time:.2f} seconds") 
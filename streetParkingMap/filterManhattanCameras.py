import json
from pathlib import Path

# Manhattan boundaries (approximate)
MANHATTAN_BOUNDS = {
    'north': 40.88,
    'south': 40.70,
    'west': -74.02,
    'east': -73.91
}

def is_in_manhattan(lat, lng):
    """Check if coordinates fall within Manhattan boundaries"""
    return (
        MANHATTAN_BOUNDS['south'] <= lat <= MANHATTAN_BOUNDS['north'] and
        MANHATTAN_BOUNDS['west'] <= lng <= MANHATTAN_BOUNDS['east']
    )

def filter_manhattan_cameras():
    # Read the full camera data
    input_file = Path('camera_id_lat_lng_wiped.json')
    
    with open(input_file, 'r') as f:
        all_cameras = json.load(f)
    
    # Filter to only Manhattan cameras
    manhattan_cameras = {}
    
    for address, camera_data in all_cameras.items():
        lat = camera_data.get('latitude')
        lng = camera_data.get('longitude')
        
        if lat and lng and is_in_manhattan(lat, lng):
            manhattan_cameras[address] = camera_data
    
    # Create streetParkingMap directory if it doesn't exist
    output_dir = Path('streetParkingMap')
    output_dir.mkdir(exist_ok=True)
    
    # Save filtered results
    output_file = output_dir / 'manhattan_cameras.json'
    
    with open(output_file, 'w') as f:
        json.dump(manhattan_cameras, f, indent=4)
    
    print(f"✓ Found {len(manhattan_cameras)} cameras in Manhattan")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Reduced from {len(all_cameras)} total cameras to {len(manhattan_cameras)}")
    print(f"✓ That's {len(manhattan_cameras)/len(all_cameras)*100:.1f}% of all cameras")

if __name__ == "__main__":
    filter_manhattan_cameras()
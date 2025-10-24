import json

def main():
    # Load both JSON files
    with open("camera_id_lat_lng_wiped.json", "r") as f:
        original_data = json.load(f)
    
    with open("camera_id_lat_lng_updated.json", "r") as f:
        updated_data = json.load(f)
    
    # Keep track of changes
    fixed_count = 0
    
    # Update null coordinates in original data
    for address, data in original_data.items():
        if data['latitude'] is None or data['longitude'] is None:
            if address in updated_data and updated_data[address]['latitude'] is not None:
                # Copy just the coordinates
                data['latitude'] = updated_data[address]['latitude']
                data['longitude'] = updated_data[address]['longitude']
                fixed_count += 1
                print(f"Fixed coordinates for: {address}")
    
    # Save the patched original file
    with open("camera_id_lat_lng_wiped.json", "w") as f:
        json.dump(original_data, f, indent=4)
    
    print(f"\nDone! Fixed {fixed_count} null coordinates in the original file.") 
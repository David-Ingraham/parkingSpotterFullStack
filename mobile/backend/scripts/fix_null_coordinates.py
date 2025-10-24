import json
import os
from dotenv import load_dotenv
import googlemaps
import time
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("Please set GOOGLE_MAPS_API_KEY in .env file")

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def format_address(address: str) -> str:
    """Convert address from JSON key format to Google Maps friendly format."""
    # Replace underscores with spaces
    address = address.replace('_', ' ')
    
    # Common replacements
    replacements = {
        ' Ave ': ' Avenue & ',
        ' St ': ' Street & ',
        ' Bet ': ' Between ',
        ' E ': ' East ',
        ' W ': ' West ',
        ' N ': ' North ',
        ' S ': ' South ',
    }
    
    for old, new in replacements.items():
        address = address.replace(old, new)
    
    # Remove trailing '&' if exists
    address = address.strip('& ')
    
    # Add New York context
    address = f"{address}, Manhattan, New York, NY"
    
    return address

def get_coordinates(formatted_address: str) -> tuple[float | None, float | None]:
    """Get coordinates from Google Maps Geocoding API."""
    try:
        # Add a small delay to respect API rate limits
        time.sleep(0.1)
        
        # Make the geocoding request
        result = gmaps.geocode(formatted_address)
        
        if result and len(result) > 0:
            location = result[0]['geometry']['location']
            return location['lat'], location['lng']
        
        return None, None
    
    except Exception as e:
        print(f"Error geocoding {formatted_address}: {e}")
        return None, None

def main():
    # Load the JSON file
    with open("camera_id_lat_lng_wiped.json", "r") as f:
        camera_data = json.load(f)
    
    # Keep track of changes
    addresses_fixed = 0
    addresses_failed = 0
    null_addresses = []
    
    # Find and process null coordinates
    for address, data in camera_data.items():
        if data['latitude'] is None or data['longitude'] is None:
            null_addresses.append(address)
            
            # Format the address for geocoding
            formatted_address = format_address(address)
            data['formatted_address'] = formatted_address
            
            print(f"\nProcessing: {address}")
            print(f"Formatted as: {formatted_address}")
            
            # Get coordinates
            lat, lng = get_coordinates(formatted_address)
            
            if lat is not None and lng is not None:
                data['latitude'] = lat
                data['longitude'] = lng
                addresses_fixed += 1
                print(f"✓ Fixed! New coordinates: {lat}, {lng}")
            else:
                addresses_failed += 1
                print(f"✗ Failed to get coordinates")
    
    # Save the updated data
    with open("camera_id_lat_lng_updated.json", "w") as f:
        json.dump(camera_data, f, indent=4)
    
    # Print summary
    print("\nSummary:")
    print(f"Total addresses with null coordinates: {len(null_addresses)}")
    print(f"Successfully fixed: {addresses_fixed}")
    print(f"Failed to fix: {addresses_failed}")
    
    if addresses_failed > 0:
        print("\nAddresses that still need fixing:")
        for address in null_addresses:
            if camera_data[address]['latitude'] is None:
                print(f"- {address}")

if __name__ == "__main__":
    main() 
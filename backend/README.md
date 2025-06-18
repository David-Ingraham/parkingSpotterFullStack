# ParkingSpotter Backend

This is the backend service for the ParkingSpotter mobile app, designed to help users find nearby parking in NYC by retrieving and serving traffic camera images near a given location. It is built using Flask and deployed to Render.

## Overview

This Flask API exposes a `/photo` endpoint that takes a set of latitude and longitude coordinates and returns publicly viewable image URLs from nearby NYC traffic cameras.

These images are temporarily cached on the server and served via static URLs. Images are resized and compressed to optimize network performance.

## Folder Structure

```
backend/
├── main.py                     # Flask app
├── fetch_image.py             # Fetches single camera image
├── get_nearby_cameras.py      # Finds nearby cameras
├── camera_id_lat_lng_wiped.json  # All camera metadata
├── static/
│   └── imgs/                  # Where fetched images are saved
├── requirements.txt           # Python dependencies
```


## API Reference

### POST /photo

Description:  
Returns an array of traffic camera images near the specified coordinates.

Request Body:
```json
{
  "lat": 40.7570,
  "lng": -73.9903
}
```

Response:
```json
{
  "images": [
    {
      "address": "10_Ave_42_St",
      "url": "https://your-app.onrender.com/static/imgs/1684863025_10_Ave_42_St.jpg"
    }
  ]
}
```

## Core Code Breakdown

### main.py

The main server entry point.

```python
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)
```

Initializes Flask with a static folder where images are saved, and enables CORS so your frontend can make cross-origin requests.

```python
@app.post("/photo")
def photo():
```

Defines a POST endpoint `/photo` that expects a JSON payload with latitude and longitude.

```python
data = request.get_json()
lat, lng = data["lat"], data["lng"]
```

Parses the coordinates from the request body.

```python
img_dir = os.path.join("static", "imgs")
os.makedirs(img_dir, exist_ok=True)
for f in os.listdir(img_dir):
    os.remove(os.path.join(img_dir, f))
```

Ensures the image folder exists and is emptied before saving new images.

```python
cameras = find_nearby_cameras(lat, lng, "camera_id_lat_lng_wiped.json")
```

Calls the helper function to find all nearby cameras based on coordinates.

```python
img = fetch_and_save_image(info["camera_id"], stamp)
```

Fetches and decodes the live traffic image for each nearby camera.

```python
img = img.resize((640, h), Image.LANCZOS)
```

Optionally resizes large images to improve frontend performance.

```python
url = f"https://your-backend.onrender.com/static/imgs/{filename}"
```

Generates a public URL pointing to the saved image.

### fetch_image.py

```python
img = Image.open(BytesIO(response.content))
```

Opens the image directly from HTTP response bytes.

### get_nearby_cameras.py

```python
distance = haversine(user_lat_lng, camera_lat_lng)
```

Uses the Haversine formula to calculate distance in miles.

## Dependencies

See `requirements.txt`. Key libraries:
- Flask – Web framework
- flask-cors – Handles CORS headers
- Pillow – Image processing
- requests – HTTP camera API fetch
- python-dotenv – API key management
- haversine – Geolocation distance math
- psutil – Logs memory usage

## Deployment

This app is deployed to Render (free tier). On push to GitHub, it auto-rebuilds.

Static files are served from `/static/imgs/`.


## License

This project is licensed under a custom license:

You are free to use, modify, and distribute this code for personal or non-commercial use.  
Commercial use, redistribution, or integration into paid products or services requires prior written permission and a commercial license from the author.

Contact: David Ingraham — https://www.linkedin.com/in/david-ingraham-730066203

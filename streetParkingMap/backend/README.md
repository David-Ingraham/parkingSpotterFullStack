# Street Parking Map - Backend

Simple in-memory backend that scans Manhattan traffic cameras to detect parking availability.

## Architecture

- **Flask API** serves camera status data
- **Background scanner** runs every 10 minutes
- **In-memory storage** (no database needed)
- **Parallel processing** with 8 worker threads
- **YOLOv8 model** detects parked cars and open parking spots

## Setup

### 1. Prerequisites

- Python 3.8+
- Your trained YOLOv8 model weights

### 2. Install Dependencies

```bash
cd streetParkingMap/backend
pip install -r requirements.txt
```

### 3. Add Your Model

Copy your trained model to the `models/` directory:

```bash
# Copy from your main backend
copy ..\backend\model\weights.pt models\weights.pt
```

Or on Mac/Linux:
```bash
cp ../../backend/model/weights.pt models/weights.pt
```

### 4. Verify Data Files

Make sure you have:
- `data/manhattan_cameras.json` ✓ (125 Manhattan cameras)
- `models/weights.pt` (Your YOLO model)

## Running the Server

```bash
python api_server.py
```

**What happens on startup:**
1. Loads camera data (125 cameras)
2. Loads YOLO model
3. Runs initial scan (~2-3 minutes with 8 workers)
4. Starts Flask API on port 5000
5. Starts background scanner (rescans every 10 minutes)

## API Endpoints

### Get All Cameras
```bash
GET http://localhost:5000/api/cameras
```

**Response:**
```json
{
  "cameras": {
    "10_Ave_42_St": {
      "address": "10_Ave_42_St",
      "camera_id": "b55781b8-827c-40e3-b094-27c289d22f7a",
      "latitude": 40.7596359,
      "longitude": -73.9954730,
      "status": "open_parking",
      "parked_cars_confidence": 0.145,
      "open_parking_confidence": 0.823,
      "parked_cars_count": 3,
      "open_parking_count": 12,
      "last_scanned": "2025-10-24T14:32:15Z"
    },
    ...
  },
  "last_scan": 1729781535.123,
  "camera_count": 125,
  "scan_interval": 600
}
```

### Get Specific Camera
```bash
GET http://localhost:5000/api/camera/10_Ave_42_St
```

### Health Check
```bash
GET http://localhost:5000/api/health
```

## Status Values

- `"open_parking"` - 🟢 Parking spots available
- `"parked_cars"` - 🔴 Only parked cars (no open spots)
- `"both"` - 🟡 Mix of parked cars and open spots
- `"none"` - ⚪ No parking detected (or camera offline)

## Configuration

Edit these constants in `api_server.py`:

```python
SCAN_INTERVAL = 600  # 10 minutes (in seconds)
MAX_WORKERS = 8      # Parallel scanning threads
```

## Performance

**With 8 parallel workers:**
- Full scan: ~20-30 seconds (125 cameras)
- Per camera: ~1-2 seconds (fetch + inference)
- Memory usage: ~600-800MB (model + images)

## Troubleshooting

### Model Not Found
```
[ERROR] Model file not found: models/weights.pt
```
**Fix:** Copy your weights.pt file to `models/` directory

### Camera Data Not Found
```
[ERROR] Camera data file not found: data/manhattan_cameras.json
```
**Fix:** Make sure manhattan_cameras.json is in `data/` directory

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Fix:** Change port in `api_server.py` or kill existing process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <pid> /F

# Mac/Linux
lsof -ti:5000 | xargs kill
```

## Testing

```bash
# Test API is running
curl http://localhost:5000/api/health

# Get all cameras
curl http://localhost:5000/api/cameras

# Get specific camera
curl http://localhost:5000/api/camera/10_Ave_42_St
```

## Next Steps

1. Build the frontend React app
2. Display cameras on a Leaflet map
3. Color-code markers by status
4. Deploy to Hetzner/Oracle Cloud

## Notes

- Data is stored **in-memory only** (lost on restart)
- Scans run in background thread
- CORS enabled for frontend development
- No authentication (add if needed for production)


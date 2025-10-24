# Street Parking Map

A simple web-based parking availability map for Manhattan using NYC traffic cameras and computer vision.

## Overview

This project scans 125 Manhattan traffic cameras every 10 minutes using a YOLOv8 model to detect parking availability. The data is served via a simple API and displayed on an interactive map.

**Key Features:**
- 🚗 Real-time parking detection using computer vision
- 🗺️ Color-coded map markers (green = open, red = full, yellow = mixed)
- ⚡ Fast parallel scanning (8 workers, ~20 seconds per scan)
- 💾 In-memory storage (no database needed)
- 🌐 Simple REST API

## Project Structure

```
streetParkingMap/
├── backend/                      # Flask API + Scanner
│   ├── api_server.py            # Main server (Flask + background thread)
│   ├── scanner.py               # Parallel camera scanner
│   ├── model_inference.py       # YOLO model wrapper
│   ├── utils/
│   │   └── fetch_image.py       # Fetch images from NYC DOT
│   ├── models/
│   │   └── weights.pt           # Your YOLO model (add this)
│   ├── data/
│   │   └── manhattan_cameras.json  # 125 camera locations
│   ├── requirements.txt
│   └── README.md
│
└── frontend/                     # React app (to be built)
    └── (coming next)
```

## Quick Start

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd streetParkingMap/backend
   pip install -r requirements.txt
   ```

2. **Add your model:**
   ```bash
   # Copy your trained weights from main project
   copy ..\..\backend\model\weights.pt models\weights.pt
   ```

3. **Run the server:**
   ```bash
   python api_server.py
   ```

4. **Test the API:**
   ```bash
   # In another terminal
   curl http://localhost:5000/api/cameras
   ```

### What Happens on Startup

1. ✓ Loads 125 Manhattan camera locations
2. ✓ Loads YOLOv8 model (~100-300MB)
3. ✓ Runs initial scan (takes 2-3 minutes)
4. ✓ Starts Flask API on port 5000
5. ✓ Background scanner rescans every 10 minutes

## API Endpoints

### `GET /api/cameras`
Returns all cameras with current parking status

### `GET /api/camera/<address>`
Returns specific camera details

### `GET /api/health`
Health check and status

See `backend/README.md` for detailed API documentation.

## Parking Status Values

| Status | Marker Color | Meaning |
|--------|-------------|---------|
| `open_parking` | 🟢 Green | Parking spots available! |
| `parked_cars` | 🔴 Red | No open spots detected |
| `both` | 🟡 Yellow | Mix of parked + open |
| `none` | ⚪ Gray | No data / camera offline |

## Performance

**System Requirements:**
- 2 vCPU, 4GB RAM recommended
- ~600-800MB memory usage
- CPU-only inference (no GPU needed)

**Scan Performance:**
- 125 cameras scanned in ~20-30 seconds
- 8 parallel workers
- ~1-2 seconds per camera (fetch + inference)

## Architecture

```
┌─────────────────┐
│  Flask API      │  Port 5000
│  (api_server.py)│  Serves camera status
└────────┬────────┘
         │
         ├─→ Global in-memory dict: camera_status{}
         │
┌────────▼────────┐
│ Background      │  Every 10 minutes
│ Scanner Thread  │  Updates camera_status
└────────┬────────┘
         │
         ├─→ scanner.py (parallel workers)
         ├─→ model_inference.py (YOLO)
         └─→ fetch_image.py (NYC DOT API)
```

## Next Steps

1. **Build Frontend** - React app with Leaflet map
2. **Deploy** - Hetzner VPS (~$6/month) or Oracle Free Tier
3. **Add Features:**
   - Historical data (if needed)
   - User notifications
   - Camera health monitoring

## Technology Stack

**Backend:**
- Flask (API framework)
- Ultralytics YOLOv8 (computer vision)
- Python threading (parallel processing)

**Frontend (coming):**
- React (UI framework)
- Leaflet.js (map library)
- Axios (API calls)

## Cost Estimate

**For 24/7 operation:**
- Hetzner CX21: $6.40/month (recommended)
- DigitalOcean: $12/month
- Oracle Free Tier: $0/month (if approved)

**For 6am-10pm operation (16 hrs/day):**
- ~60% of above costs

## License

Same as parent project (MIT)

## Credits

- NYC DOT for public traffic camera data
- Ultralytics for YOLOv8 framework


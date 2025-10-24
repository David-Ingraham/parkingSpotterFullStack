# Quick Start Guide

Get the Manhattan Parking Map running locally in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+
- Your trained YOLOv8 model (`weights.pt`)

## Step 1: Backend Setup

### Install Dependencies

```bash
cd streetParkingMap/backend
pip install -r requirements.txt
```

### Add Your Model

```bash
# Copy your trained model to the models folder
# Windows:
copy ..\..\backend\model\weights.pt models\weights.pt

# Mac/Linux:
cp ../../backend/model/weights.pt models/weights.pt
```

### Start Backend Server

```bash
python api_server.py
```

**Wait for initial scan to complete** (~2-3 minutes). You'll see:
```
✓ Initial scan complete. 124 cameras ready.
Server ready!
API available at: http://localhost:5000
```

Keep this terminal running!

## Step 2: Frontend Setup

**Open a new terminal**

### Install Dependencies

```bash
cd streetParkingMap/frontend
npm install
```

### Create Environment File

```bash
# Copy the example file
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

The `.env` file should contain:
```
VITE_API_URL=http://localhost:5000
```

### Start Frontend

```bash
npm run dev
```

The app will open at **http://localhost:3000**

## Step 3: Open in Browser

Navigate to **http://localhost:3000**

You should see:
- 🗺️ Interactive map of Manhattan
- 🔴 Red markers (parked cars)
- 🟢 Green markers (open parking) - if any!
- 🟡 Yellow markers (mixed)
- ⚪ Gray markers (no data)

Click any marker to see details!

## What You Should See

### Backend Terminal
```
============================================================
Starting camera poll
Found 125 cameras being watched
[OK] 10_Ave_42_St: parked_cars (parked: 4, open: 0)
[OK] 10_Ave_57_St: none (parked: 0, open: 0)
...
Poll complete. Sleeping for 600 seconds...
```

### Frontend Browser
- Map centered on Manhattan
- Colored markers for each camera
- Sidebar with legend and stats
- Clickable markers with popup details

## Troubleshooting

### Backend Issues

**Error: Model file not found**
```bash
# Make sure weights.pt is in the right place:
ls models/weights.pt  # Should exist
```

**Error: Camera data not found**
```bash
# Make sure manhattan_cameras.json exists:
ls data/manhattan_cameras.json  # Should exist
```

**Port 5000 already in use**
```bash
# Windows - find and kill process:
netstat -ano | findstr :5000
taskkill /PID <pid> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill
```

### Frontend Issues

**White screen / Loading forever**
- Check backend is running on port 5000
- Open browser console (F12) for errors
- Try visiting http://localhost:5000/api/cameras directly

**Map tiles not loading**
- Check internet connection (tiles load from OpenStreetMap)
- Try a different browser

**No markers showing**
- Wait for initial backend scan to complete
- Check browser console for errors
- Verify backend returned data: http://localhost:5000/api/cameras

## Next Steps

### Customize Scan Interval

Edit `backend/api_server.py`:
```python
SCAN_INTERVAL = 600  # Change to 300 for 5 minutes, 900 for 15 minutes
```

### Customize Polling Interval

Edit `frontend/src/App.jsx`:
```jsx
}, 30000); // Change to 60000 for 1 minute updates
```

### Deploy to Production

See deployment guides in:
- `backend/README.md` - Backend deployment
- `frontend/README.md` - Frontend deployment
- `README.md` - Full architecture overview

## System Architecture

```
┌─────────────────────────────────────────┐
│  Browser (localhost:3000)               │
│  React + Leaflet                        │
│  Polls every 30 seconds                 │
└─────────────┬───────────────────────────┘
              │ HTTP GET /api/cameras
              ↓
┌─────────────────────────────────────────┐
│  Flask API (localhost:5000)             │
│  Serves in-memory camera data           │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│  Background Scanner Thread              │
│  • Scans 125 cameras every 10 min      │
│  • 8 parallel workers                   │
│  • Runs YOLO on each image             │
│  • Updates in-memory dict               │
└─────────────────────────────────────────┘
```

## Performance

- **Backend scan time**: ~20-30 seconds (125 cameras)
- **Backend memory**: ~600-800MB
- **API response time**: < 50ms (in-memory)
- **Frontend load time**: < 2 seconds
- **Data update delay**: Max 30 seconds (frontend polling)

## Need Help?

Check the detailed READMEs:
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend documentation
- `README.md` - Project overview

Enjoy your parking map! 🚗🗺️


# Street Parking Map - Frontend

React web application that displays Manhattan parking availability on an interactive map.

## Features

- 🗺️ Interactive Leaflet map of Manhattan
- 🎨 Color-coded camera markers (green/yellow/red/gray)
- 📊 Real-time parking status updates
- 📱 Responsive design (mobile-friendly)
- 🔄 Auto-refreshes every 30 seconds
- 💡 Detailed camera popups with detection stats

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool (fast!)
- **Leaflet** - Map library
- **React Leaflet** - React components for Leaflet
- **Axios** - API calls

## Setup

### 1. Install Dependencies

```bash
cd streetParkingMap/frontend
npm install
```

### 2. Configure Backend URL

The app defaults to `http://localhost:5000`. To change it, edit `.env`:

```bash
VITE_API_URL=http://your-backend-url:5000
```

### 3. Start Development Server

```bash
npm run dev
```

The app will open at **http://localhost:3000**

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## How It Works

### Data Flow

```
Backend API (port 5000)
    ↓
Axios Request (every 30 seconds)
    ↓
App Component (state management)
    ↓
ParkingMap Component (renders Leaflet)
    ↓
CircleMarkers (color-coded by status)
```

### Status Colors

| Status | Color | Meaning |
|--------|-------|---------|
| `open_parking` | 🟢 Green | Parking spots detected |
| `both` | 🟡 Yellow | Mix of parked + open |
| `parked_cars` | 🔴 Red | Only parked cars |
| `none` | ⚪ Gray | No data |

### Components

**`App.jsx`**
- Fetches camera data from API
- Manages global state
- Handles polling (30-second intervals)
- Error handling & loading states

**`ParkingMap.jsx`**
- Renders Leaflet map
- Creates CircleMarkers for each camera
- Handles marker colors based on status
- Displays detailed popups on click

**`Legend.jsx`**
- Shows color legend
- Displays scan stats
- Shows last/next scan times

**`api.js`**
- Axios wrapper for backend API
- Endpoints: `/api/cameras`, `/api/health`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ParkingMap.jsx       # Leaflet map + markers
│   │   └── Legend.jsx           # Sidebar legend
│   ├── services/
│   │   └── api.js               # Backend API calls
│   ├── App.jsx                  # Main app component
│   ├── App.css                  # Styles
│   └── main.jsx                 # Entry point
├── public/
├── index.html
├── package.json
├── vite.config.js
└── .env
```

## Deployment

### Option 1: Static Hosting (Netlify, Vercel)

1. Build the app:
   ```bash
   npm run build
   ```

2. Deploy `dist/` folder to:
   - **Netlify**: Drag & drop or connect to Git
   - **Vercel**: `vercel deploy`
   - **GitHub Pages**: Use `gh-pages` package

3. **Important**: Set environment variable for production backend URL:
   ```
   VITE_API_URL=https://your-backend-url.com
   ```

### Option 2: Serve with Backend

Copy the `dist/` folder to your backend server and serve as static files.

## Customization

### Change Map Style

Edit the TileLayer URL in `ParkingMap.jsx`:

```jsx
// Dark mode
url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

// Satellite
url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
```

### Change Polling Interval

Edit `App.jsx`:

```jsx
// Poll every 60 seconds instead of 30
setInterval(() => {
  fetchCameras();
}, 60000);
```

### Change Map Center/Zoom

Edit `ParkingMap.jsx`:

```jsx
const center = [40.7831, -73.9712]; // Manhattan center
const zoom = 12; // Zoom level (higher = closer)
```

## Troubleshooting

### Map Not Loading

**Problem**: White screen or map tiles not loading

**Fix**: Check that Leaflet CSS is imported in `index.html`:
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

### API Connection Error

**Problem**: "Failed to load camera data"

**Fix**: 
1. Ensure backend is running on port 5000
2. Check CORS is enabled in backend (`flask-cors`)
3. Verify `.env` has correct `VITE_API_URL`

### Markers Not Showing

**Problem**: Map loads but no markers visible

**Fix**: 
1. Check browser console for errors
2. Verify backend `/api/cameras` returns data
3. Check camera coordinates are valid

## Performance

- **Initial load**: < 2 seconds
- **Map rendering**: Instant (125 markers)
- **Polling overhead**: Minimal (~10KB per request)
- **Memory usage**: ~50MB (typical React app)

## Browser Support

- Chrome/Edge: ✅
- Firefox: ✅
- Safari: ✅
- Mobile browsers: ✅

## License

Same as parent project (MIT)


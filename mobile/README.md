# Parking Spotter

A React Native mobile application that helps users find available parking spots in New York City using real-time traffic camera feeds.

## Key Features

- **No Login Required**: Start using the app immediately without creating accounts
- **No Data Collection**: Your location and usage data stay on your device
- **Privacy First**: No user tracking, analytics, or personal information storage
- **Location-Based Search**: Find the 5 nearest parking cameras to your current location
- **Direct Search**: Search for specific camera locations by address
- **Real-Time Camera Feeds**: View live traffic camera images to assess parking availability
- **AI-Powered Monitoring**: Watch cameras with computer vision detection for parking availability
- **Real-Time Notifications**: Get notified via WebSocket when parking status changes
- **NYC Coverage**: Comprehensive coverage of New York City parking cameras

## Privacy & Security

**This app respects your privacy:**
- No user accounts or registration required
- No personal data collection or storage
- Location data is processed locally and never transmitted to our servers
- No user tracking or analytics
- No advertisements or third-party data sharing
- Open source - you can verify what the code actually does

## Tech Stack

### Frontend (React Native)
- **React Native** - Cross-platform mobile development
- **TypeScript** - Type-safe development
- **React Navigation** - Navigation framework
- **Geolocation Services** - Location-based features (processed locally)

### Backend (Python/Flask)
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support for real-time notifications
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Production database
- **Waitress** - WSGI server
- **Flask-CORS** - Cross-origin resource sharing
- **YOLOv8** - Computer vision model for parking detection
- **Ultralytics** - YOLO model framework
- **PIL/Pillow** - Image processing

## Project Structure

```
parkingSpotter/
├── frontEnd/                 # React Native mobile app
│   ├── components/           # Reusable UI components
│   ├── screens/             # App screens
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript type definitions
│   ├── data/                # Static data files
│   └── utils/               # Utility functions
└── backend/                 # Flask backend API
    ├── routes/              # API route handlers
    ├── database/            # Database models and config
    ├── helpers/             # Helper functions (image fetching, etc)
    ├── scripts/             # Utility scripts (camera population, etc)
    ├── model/               # YOLO model weights
    ├── main.py              # Main Flask API server
    ├── websocket_server.py  # WebSocket notification server
    └── camera_watcher_service.py  # Background camera monitoring service
```

## Prerequisites

### For Backend Development
- **Python** (3.8 or higher)
- **PostgreSQL** (for database)

### For Frontend Development  
- **Node.js** (v16 or higher) - Required for React Native
- **npm** or **yarn** - Package management
- **React Native development environment** ([Setup Guide](https://reactnative.dev/docs/environment-setup))

### For Android Development
- **Android Studio**
- **Android SDK**
- **Java Development Kit (JDK)**

### For iOS Development (macOS only)
- **Xcode**
- **CocoaPods**

## Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/parkingSpotter.git
   cd parkingSpotter/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=parking_spotter
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   ```

5. **Set up the database**
   Initialize the database and populate cameras (one-time setup):
   ```bash
   python scripts/populate_cameras.py
   ```

6. **Download the vision model**
   Place your trained YOLOv8 model weights at `backend/model/weights.pt`
   
   Or download a pre-trained model:
   ```bash
   pip install ultralytics
   yolo download model yolov8l.pt
   mv yolov8l.pt model/weights.pt
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontEnd
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   Create a `.env` file in the frontend directory:
   ```env
   BACKEND_URL=http://localhost:8000  # For development
   # BACKEND_URL=https://your-production-backend-url.com  # For production
   ```

4. **Install iOS dependencies (macOS only)**
   ```bash
   cd ios && pod install && cd ..
   ```

## Running the Application

### Start the Backend Services

The backend consists of three services that need to run simultaneously:

1. **Main API Server** (port 8000)
   ```bash
   cd backend
   python main.py
   ```

2. **WebSocket Server** (port 8001)
   ```bash
   cd backend
   python websocket_server.py
   ```

3. **Camera Watcher Service** (background polling)
   ```bash
   cd backend
   python camera_watcher_service.py
   ```

All three services must be running for full functionality:
- Main API handles camera searches and watch requests
- WebSocket server sends real-time notifications to clients
- Watcher service monitors cameras every 5 minutes with AI vision

### Start the React Native App

1. **Start Metro bundler**
   ```bash
   cd frontEnd
   npm start
   # or
   yarn start
   ```

2. **Run on Android**
   ```bash
   npm run android
   # or
   yarn android
   ```

3. **Run on iOS** (macOS only)
   ```bash
   npm run ios
   # or
   yarn ios
   ```

## API Endpoints

### Camera Search
- **POST** `/five_nearest` - Get 5 nearest cameras to coordinates
- **POST** `/search_cameras` - Search cameras by address list

### Camera Watching
- **POST** `/watch_camera` - Register to watch a camera
  - Parameters: `address`, `client_id`, `timeToLive` (10-180 minutes, multiples of 5)
  - Returns: Success status
  - Camera will be monitored by AI vision model every 5 minutes
  
- **POST** `/unwatch_camera` - Stop watching a camera
  - Parameters: `address`, `client_id`
  - Returns: Success status

### WebSocket Events (port 8001)
- **Connect**: `ws://localhost:8001?client_id=<your_client_id>`
- **Event: `camera_update`** - Receives parking status changes
  - Payload: `{ address, status, timestamp }`
  - Status values: `"none"`, `"parked_cars"`, `"open_parking"`, `"both"`

## Environment Variables

### Backend
| Variable | Description | Required |
|----------|-------------|----------|
| `DB_USER` | PostgreSQL username | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_HOST` | Database host | Yes |
| `DB_PORT` | Database port | Yes |
| `DB_NAME` | Database name | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Yes |

### Frontend
| Variable | Description | Required |
|----------|-------------|----------|
| `BACKEND_URL` | Backend API URL | Yes |

## Database Schema

### Tables

**cameras**
- `address` (primary key) - Human-readable camera location
- `camera_id` - NYC DOT camera identifier for image fetching
- `latitude`, `longitude` - Geographic coordinates
- `last_status` - Most recent detection status (null, "none", "parked_cars", "open_parking", "both")
- `parked_cars_confidence` - Average confidence from last scan
- `open_parking_confidence` - Average confidence from last scan

**watchers**
- `id` (primary key)
- `camera_address` (foreign key to cameras)
- `client_id` - Unique client identifier for WebSocket routing
- `time_to_live` - Duration in minutes (10-180, multiples of 5)
- `expires_at` - Timestamp when watch expires
- `is_connected` - WebSocket connection status
- `created_at` - Registration timestamp

**camera_status_history**
- `id` (primary key)
- `camera_address` (foreign key to cameras)
- `status` - Historical status value
- `recorded_at` - Timestamp of status change

## Data Handling

**What data we handle:**
- Camera addresses and locations (public NYC data)
- Camera image URLs (public traffic cameras)
- Temporary watch registrations (expire after timeToLive)
- Client IDs for WebSocket routing (no personal information)

**What data we DON'T collect:**
- User location (processed locally only)
- Personal information
- Usage patterns
- Device information
- Analytics or tracking data

## Deployment

### Backend (Render or VPS)

The backend requires three processes running simultaneously:

**Option 1: Cloud Platform (Render, Railway, etc.)**
1. Deploy three separate services:
   - Main API (`python main.py`) on port 8000
   - WebSocket server (`python websocket_server.py`) on port 8001
   - Camera watcher (`python camera_watcher_service.py`) as background worker
2. Set environment variables in platform dashboard
3. Run `python scripts/populate_cameras.py` once after first deployment

**Option 2: VPS (DigitalOcean, AWS, etc.)**
1. Set up process manager (systemd, supervisor, or PM2)
2. Configure three services to run on startup
3. Set up reverse proxy (nginx) for ports 8000 and 8001
4. Run camera population script once after setup

### Frontend (Android Play Store)
1. Generate a signed APK:
   ```bash
   cd frontEnd/android
   ./gradlew assembleRelease
   ```
2. Upload to Google Play Console
3. Follow Play Store review process


## Development Guidelines

- **Code Style**: Follow TypeScript/Python best practices
- **Testing**: Write tests for new features
- **Documentation**: Update README and inline documentation
- **Privacy**: Never add tracking, analytics, or data collection
- **Security**: Never commit sensitive data or API keys

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, create an issue on GitHub.

## Acknowledgments

- NYC Department of Transportation for providing public camera data
- React Native community for excellent documentation
- Open source contributors

## AI Vision Monitoring

### How It Works

The camera monitoring system uses a custom-trained YOLOv8 computer vision model to detect parking availability:

1. **Watch Registration**: Users register to watch specific cameras via `/watch_camera` endpoint
2. **Periodic Scanning**: Background service polls all watched cameras every 5 minutes
3. **Image Analysis**: YOLO model analyzes camera feeds for two classes:
   - `parkedCars` - Vehicles occupying parking spaces
   - `openParking` - Available parking spots
4. **Status Determination**: System calculates average confidence for each class and determines status:
   - `"none"` - No parking or cars detected
   - `"parked_cars"` - Only parked cars detected
   - `"open_parking"` - Only open spots detected
   - `"both"` - Both parked cars and open spots detected
5. **Change Detection**: When status changes from previous scan, all watching users are notified via WebSocket
6. **Auto-Cleanup**: Watch registrations expire after their `timeToLive` period

### Model Performance

Current model stats (with low confidence threshold):
- **mAP@50**: 71.3%
- **Precision**: 77.9%
- **Recall**: 59.9%

The model runs with a very low confidence threshold (0.01) and aggregates multiple detections to reduce false negatives.

## Model Setup

The vision model weights should be placed at `backend/model/weights.pt`. 

For development/testing, you can use a pre-trained YOLOv8 model:
```bash
pip install ultralytics
yolo download model yolov8l.pt
mv yolov8l.pt backend/model/weights.pt
```

Note: Model files are not included in the repository due to their size. For production, use a custom-trained model on NYC parking camera data.

---

**A privacy-respecting parking solution for NYC drivers** 
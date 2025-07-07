# Parking Spotter

A React Native mobile application that helps users find available parking spots in New York City using real-time traffic camera feeds.

## Key Features

- **No Login Required**: Start using the app immediately without creating accounts
- **No Data Collection**: Your location and usage data stay on your device
- **Privacy First**: No user tracking, analytics, or personal information storage
- **Location-Based Search**: Find the 5 nearest parking cameras to your current location
- **Direct Search**: Search for specific camera locations by address
- **Real-Time Camera Feeds**: View live traffic camera images to assess parking availability
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
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Production database
- **Waitress** - WSGI server
- **Flask-CORS** - Cross-origin resource sharing

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
└── parkingSpotterBackend/   # Flask backend API
    ├── routes/              # API route handlers
    ├── database/            # Database models and config
    ├── helpers/             # Helper functions
    ├── scripts/             # Utility scripts
    └── static/              # Static files
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
   cd parkingSpotter/parkingSpotterBackend
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

5. **Start the backend server**
   ```bash
   python main.py
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

### Start the Backend
```bash
cd parkingSpotterBackend
python main.py
```
Backend will be available at `http://localhost:8000`

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

### Camera Watching (WebSocket)
- **POST** `/watch_camera` - Start watching a camera for changes
- **POST** `/unwatch_camera` - Stop watching a camera

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

## Data Handling

**What data we handle:**
- Camera addresses and locations (public NYC data)
- Camera image URLs (public traffic cameras)

**What data we DON'T collect:**
- User location (processed locally only)
- Personal information
- Usage patterns
- Device information
- Analytics or tracking data

## Deployment

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy automatically on push to main branch

### Frontend (Android Play Store)
1. Generate a signed APK:
   ```bash
   cd frontEnd/android
   ./gradlew assembleRelease
   ```
2. Upload to Google Play Console
3. Follow Play Store review process

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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

## Model Setup
After cloning the repository, you'll need to download the YOLO models:

1. Create a `modelTesting` directory if it doesn't exist
2. Download the models from Ultralytics:
   - YOLOv8x: `pip install ultralytics && yolo download model yolov8x.pt`
   - YOLOv8l: `pip install ultralytics && yolo download model yolov8l.pt`
3. Move the downloaded .pt files to the `modelTesting` directory

Note: Model files are not included in the repository due to their size.

---

**A privacy-respecting parking solution for NYC drivers** 
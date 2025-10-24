# Changelog

All notable changes to Parking Spotter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
- Privacy policy for app store compliance
- Contributing guidelines for open source development
- Deployment guide for production setup
- API documentation for developers

### Changed
- Cleaned up all console.log statements for production
- Removed unused imports across the codebase
- Improved error handling throughout the application

## [1.0.0] - Initial Release

### Added
- React Native mobile application for iOS and Android
- Location-based camera search (5 nearest cameras)
- Direct camera search by address
- Real-time traffic camera image viewing
- NYC boundary validation for location services
- Flask backend API with PostgreSQL database
- Camera watching functionality with WebSocket support
- Rate limiting for API protection
- Privacy-first design (no user data collection)
- TypeScript implementation for type safety

### Features
- **No Login Required**: Immediate app usage without accounts
- **Privacy Focused**: Location processing stays on device
- **Real-time Data**: Live traffic camera feeds
- **NYC Coverage**: Comprehensive camera network coverage
- **Cross-platform**: iOS and Android support

### Backend
- Flask web framework with Waitress WSGI server
- PostgreSQL database with SQLAlchemy ORM
- RESTful API endpoints for camera data
- WebSocket support for real-time features
- Rate limiting with Flask-Limiter
- Environment-based configuration
- Production-ready database connection pooling

### Frontend
- React Native with TypeScript
- React Navigation for screen management
- Geolocation services integration
- Image loading and display optimization
- Error handling and user feedback
- NYC-specific location validation
- Clean, intuitive user interface

### Security
- Input validation on all endpoints
- SQL injection protection via ORM
- CORS configuration for web security
- Rate limiting to prevent abuse
- No sensitive data logging
- Environment variable protection

---

## Version Numbering

- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes or significant new features
- **Minor**: New features that are backward compatible
- **Patch**: Bug fixes and small improvements

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements 
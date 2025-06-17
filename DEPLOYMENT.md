# Deployment Guide

This guide covers deploying Parking Spotter to production environments.

## Backend Deployment (Render)

### Prerequisites
- Render account
- PostgreSQL database
- Environment variables ready
- GitHub repository connected

### Step 1: Database Setup

**Create PostgreSQL Database on Render:**
1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Configure database:
   - Name: `parking-spotter-db`
   - Database Name: `parking_spotter`
   - User: `parking_spotter_user`
   - Region: Choose closest to your users
4. Note the connection details for environment variables

### Step 2: Backend Service Setup

**Create Web Service:**
1. Click "New" → "Web Service"
2. Connect GitHub repository
3. Configure service:
   - Name: `parking-spotter-backend`
   - Root Directory: `parkingSpotterBackend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

### Step 3: Environment Variables

**Required variables in Render dashboard:**
```
DATABASE_URL=postgresql://user:password@host:port/dbname
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
FLASK_ENV=production
```

**Optional variables:**
```
DB_USER=parking_spotter_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=parking_spotter
```

### Step 4: Deploy Backend

1. Click "Create Web Service"
2. Wait for initial deployment
3. Check logs for successful startup
4. Test API endpoints

### Step 5: Domain Setup (Optional)

**Custom Domain:**
1. Go to service settings
2. Add custom domain
3. Configure DNS records
4. Enable SSL certificate

## Frontend Deployment (Android)

### Prerequisites
- Android Studio
- Java Development Kit (JDK 8+)
- Signing keys for release build
- Google Play Console account

### Step 1: Environment Configuration

**Update production environment:**
```bash
cd frontEnd
```

**Edit `.env` file:**
```env
BACKEND_URL=https://your-backend-url.onrender.com
```

### Step 2: Generate Signing Key

**Create keystore (first time only):**
```bash
cd android/app
keytool -genkeypair -v -storetype PKCS12 -keystore my-upload-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

**Configure gradle:**
Edit `android/gradle.properties`:
```properties
MYAPP_UPLOAD_STORE_FILE=my-upload-key.keystore
MYAPP_UPLOAD_KEY_ALIAS=my-key-alias
MYAPP_UPLOAD_STORE_PASSWORD=****
MYAPP_UPLOAD_KEY_PASSWORD=****
```

### Step 3: Build Release APK

**Generate signed bundle:**
```bash
cd android
./gradlew bundleRelease
```

**Generate signed APK (alternative):**
```bash
./gradlew assembleRelease
```

### Step 4: Test Release Build

**Install and test:**
```bash
npx react-native run-android --variant=release
```

### Step 5: Google Play Store

**Upload to Play Console:**
1. Create app listing
2. Upload APK/Bundle
3. Add store listing details:
   - App description
   - Screenshots
   - Privacy policy link
4. Submit for review

## iOS Deployment (Optional)

### Prerequisites
- macOS with Xcode
- Apple Developer account
- iOS device for testing

### Step 1: iOS Build Configuration

**Update iOS environment:**
```bash
cd ios
pod install
```

**Configure signing in Xcode:**
1. Open `ios/ParkingSpotter.xcworkspace`
2. Select project → Signing & Capabilities
3. Configure development team and bundle ID

### Step 2: Build for Release

**Archive build:**
1. In Xcode: Product → Archive
2. Follow App Store distribution process
3. Upload to App Store Connect

## Production Monitoring

### Backend Monitoring

**Health Check Endpoint:**
Create `parkingSpotterBackend/routes/health.py`:
```python
from flask import Blueprint, jsonify

bp = Blueprint('health', __name__)

@bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'parking-spotter'})
```

**Monitor in Render:**
- Check service logs regularly
- Set up uptime monitoring
- Monitor database performance

### Database Maintenance

**Regular tasks:**
- Monitor connection counts
- Check database size
- Clean up old data if applicable
- Backup critical data

### Environment Management

**Production vs Development:**
- Use environment-specific configurations
- Never use development keys in production
- Implement proper logging levels
- Enable security headers

## Security Checklist

**Pre-deployment security:**
- [ ] All environment variables secured
- [ ] No hardcoded secrets in code
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation implemented
- [ ] Error handling doesn't expose internals
- [ ] Database access restricted
- [ ] CORS properly configured

## Rollback Plan

**If deployment fails:**
1. Check service logs in Render
2. Verify environment variables
3. Test database connectivity
4. Rollback to previous working commit
5. Investigate issues in development

**Database rollback:**
- Keep database migration scripts
- Have backup restoration plan
- Test rollback procedures

## Performance Optimization

**Backend optimization:**
- Enable gzip compression
- Implement caching where appropriate
- Optimize database queries
- Monitor response times

**Frontend optimization:**
- Minimize bundle size
- Optimize images
- Enable code splitting
- Test on various devices

## Troubleshooting

**Common issues:**

**Database connection fails:**
- Verify DATABASE_URL format
- Check database service status
- Confirm network connectivity

**Build fails:**
- Clear node_modules and reinstall
- Check Node.js version compatibility
- Verify environment variables

**API requests fail:**
- Check CORS configuration
- Verify backend URL in frontend
- Test endpoints directly

**App crashes on startup:**
- Check device logs
- Verify signing configuration
- Test on multiple devices

## Maintenance Schedule

**Weekly:**
- Check service health
- Review error logs
- Monitor resource usage

**Monthly:**
- Update dependencies
- Review security patches
- Check database performance

**Quarterly:**
- Review and update documentation
- Analyze usage patterns
- Plan feature updates

---

**Remember: Always test deployments in a staging environment first!** 
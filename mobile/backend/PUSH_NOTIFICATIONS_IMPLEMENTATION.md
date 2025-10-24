# Push Notifications Implementation Summary

## Overview

The backend now supports push notifications via Firebase Cloud Messaging (FCM) instead of relying solely on WebSockets. This enables reliable notifications even when the mobile app is in the background or closed.

## What Changed

### 1. Database Schema Updates

**File:** `backend/database/models.py`

Added two new fields to the `Watcher` model:
- `push_token` (String, nullable) - FCM device token
- `platform` (String, nullable) - 'ios' or 'android'

These fields store the user's push notification token so the backend can send notifications even when they're not connected via WebSocket.

### 2. API Endpoint Updates

**File:** `backend/routes/watch_camera.py`

Modified `/watch_camera` endpoint to accept optional push notification parameters:
```json
{
  "address": "10_Ave_42_St",
  "client_id": "unique-user-id",
  "timeToLive": 60,
  "pushToken": "fcm-token-here",  // Optional but recommended
  "platform": "android"            // Optional
}
```

### 3. Push Notification Service

**File:** `backend/helpers/push_notification.py` (NEW)

Created a new module that handles:
- Firebase Admin SDK initialization
- Sending individual push notifications
- Sending batch notifications
- Handling invalid/expired tokens
- Error logging and debugging

Key functions:
- `init_firebase()` - Initialize Firebase (call once at startup)
- `send_push_notification(token, title, body, data)` - Send to single device
- `send_batch_notifications(tokens_and_messages)` - Send to multiple devices

### 4. Camera Watcher Service Updates

**File:** `backend/camera_watcher_service.py`

Major changes:
- Added Firebase initialization in `__init__()`
- Created `notify_watchers()` method that sends push notifications
- Updated `process_camera()` to use push notifications instead of WebSocket
- Automatically cleans up invalid push tokens from database

### 5. Dependencies

**File:** `backend/requirements.txt`

Added:
- `firebase-admin==6.4.0` - Firebase Admin SDK for Python
- `ultralytics==8.1.0` - YOLOv8 model (if not already there)

### 6. Security

**File:** `.gitignore`

Added Firebase credentials to gitignore:
- `backend/firebase-credentials.json`
- `firebase-credentials.json`

## Architecture

### Before (WebSocket Only)
```
User App → Watch Request → Backend stores watch
                              ↓
Backend WebSocket Server ← Vision Service detects change
                              ↓
User App (if connected) ← WebSocket notification
```

**Problem:** Doesn't work when app is in background/closed

### After (Push Notifications)
```
User App → Watch Request with Push Token → Backend stores watch + token
                                              ↓
                            Vision Service detects change
                                              ↓
                            Firebase Cloud Messaging
                                              ↓
                            User Device (always reachable)
```

**Benefit:** Works 24/7, regardless of app state

## How It Works

### 1. User Registers to Watch Camera

Frontend sends push token to backend:
```typescript
const response = await fetch('/watch_camera', {
  method: 'POST',
  body: JSON.stringify({
    address: cameraAddress,
    client_id: userId,
    timeToLive: 60,
    pushToken: await getFCMToken(),
    platform: Platform.OS
  })
});
```

### 2. Backend Stores Token

The `Watcher` record now includes:
- Camera to watch
- User's client_id
- Push token
- Platform (ios/android)
- Expiration time

### 3. Vision Service Monitors Camera

Every 5 minutes:
1. Fetch image from camera
2. Run YOLO model
3. Determine status (none, parked_cars, open_parking, both)
4. Compare to previous status
5. If changed → send push notifications

### 4. Push Notification Delivery

```python
def notify_watchers(camera_address, new_status):
    # Get all watchers with push tokens
    watchers = db.query(Watcher).filter_by(
        camera_address=camera_address,
        push_token != None
    ).all()
    
    # Send to each watcher
    for watcher in watchers:
        send_push_notification(
            watcher.push_token,
            "Parking Update",
            f"{camera_address}: Open spots available!",
            {"status": new_status}
        )
```

### 5. User Receives Notification

Even if app is:
- In background
- Completely closed
- Not connected to internet at the moment (will receive when reconnected)

## Notification Format

Users receive notifications with:

**Title:** "Parking Update"

**Body:** Human-readable message based on status:
- `none` → "No parking detected"
- `parked_cars` → "Only parked cars visible"
- `open_parking` → "Open parking spots available!" ⭐
- `both` → "Mixed - some spots available"

**Data Payload:**
```json
{
  "camera_address": "10_Ave_42_St",
  "status": "open_parking",
  "timestamp": "2025-10-09T12:34:56.789Z"
}
```

## Setup Required

### Backend

1. **Create Firebase project** at https://console.firebase.google.com
2. **Download service account key** (JSON file)
3. **Save as** `backend/firebase-credentials.json`
4. **Install dependencies:** `pip install -r requirements.txt`
5. **Run migration** to add new database columns

### Frontend

1. **Install Firebase SDK:** `npm install @react-native-firebase/messaging`
2. **Add Firebase config files:**
   - Android: `google-services.json`
   - iOS: `GoogleService-Info.plist`
3. **Request permission** for push notifications
4. **Get FCM token** and send with watch requests

See `FIREBASE_SETUP.md` for detailed instructions.

## Token Management

### Auto-Cleanup

The backend automatically handles invalid tokens:
- When a notification fails to send
- Token is marked as invalid
- System tries to send notification
- If token is invalid/unregistered:
  - Failed token is removed from database
  - User won't receive notifications until they update token

### Token Refresh

Frontend should handle token refresh:
```typescript
messaging().onTokenRefresh(async (newToken) => {
  // Update all active watches with new token
  await updatePushToken(newToken);
});
```

## Testing

### Without Firebase Setup

If Firebase credentials aren't configured:
- Service prints warning but doesn't crash
- Vision model still works
- Notifications just won't send
- Good for testing the vision pipeline

### With Firebase Setup

1. Get your device's FCM token
2. Register to watch a camera
3. Use test script to manually trigger notification
4. Or wait for actual status change

## Backward Compatibility

The push token is **optional**:
- Old API calls without `pushToken` still work
- WebSocket server still exists for real-time updates
- Can use both simultaneously:
  - WebSocket for foreground updates (instant)
  - Push notifications for background updates (reliable)

## Production Considerations

1. **Database Migration:** Need to add new columns to existing database
2. **Token Rotation:** Handle token refresh in mobile app
3. **Batch Sending:** For many watchers, use batch API to reduce latency
4. **Rate Limits:** Firebase has generous limits but monitor usage
5. **Error Monitoring:** Track failed notification sends
6. **User Preferences:** Consider letting users opt out of certain notification types

## Cost

Firebase Cloud Messaging is **free** for unlimited notifications.

## Security

- Service account key has admin access to Firebase project
- Never commit credentials to git
- Use environment variables in production
- Rotate keys periodically
- Consider using Google Secret Manager for production

## Next Steps

1. Follow `FIREBASE_SETUP.md` to configure Firebase
2. Update frontend to request notification permissions
3. Test with a single device
4. Run database migration to add new columns
5. Deploy updated backend

## Files Modified

- ✏️ `backend/database/models.py` - Added push_token and platform fields
- ✏️ `backend/routes/watch_camera.py` - Accept push tokens in API
- ✏️ `backend/camera_watcher_service.py` - Send push notifications
- ✏️ `backend/requirements.txt` - Added firebase-admin
- ✏️ `.gitignore` - Ignore Firebase credentials
- ➕ `backend/helpers/push_notification.py` - Push notification logic
- ➕ `backend/FIREBASE_SETUP.md` - Setup instructions

## WebSocket Server

The `websocket_server.py` can now be considered **optional**:
- Keep it for real-time foreground updates
- Or remove it and use push notifications exclusively
- Push notifications are the primary notification mechanism

For mobile apps, **push notifications are the recommended approach**.


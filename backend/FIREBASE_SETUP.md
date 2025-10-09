# Firebase Push Notification Setup

This guide explains how to set up Firebase Cloud Messaging (FCM) for push notifications.

## Why Firebase?

Firebase Cloud Messaging works for both iOS and Android, making it the industry standard for mobile push notifications. It's free for most use cases and handles all the complexity of delivering notifications to devices.

## Backend Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add project" or use an existing project
3. Follow the wizard (you can disable Google Analytics if you want)

### 2. Generate Service Account Credentials

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Go to **Service Accounts** tab
3. Click **Generate new private key**
4. Save the downloaded JSON file as `firebase_credentials.json` in the `backend/` directory

**IMPORTANT**: Never commit this file to git! It's already in `.gitignore`.

### 3. Update Environment Variables (Optional)

If you want to store credentials elsewhere:

```bash
# .env file
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase_credentials.json
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes `firebase-admin` package.

### 5. Test the Setup

Start the camera watcher service:
```bash
python camera_watcher_service.py
```

You should see:
```
Initializing Firebase for push notifications...
Firebase Admin SDK initialized successfully
```

If you see a warning about missing credentials, check that `firebase_credentials.json` exists in the correct location.

## Frontend Setup (React Native)

### 1. Install Firebase SDK

For React Native:
```bash
npm install @react-native-firebase/app @react-native-firebase/messaging
```

For Expo:
```bash
npx expo install expo-notifications
```

### 2. Add Firebase Config Files

#### For Android:
1. In Firebase Console, go to Project Settings
2. Add an Android app (or select existing)
3. Download `google-services.json`
4. Place it in `frontEnd/android/app/google-services.json`

#### For iOS:
1. In Firebase Console, add an iOS app
2. Download `GoogleService-Info.plist`
3. Place it in `frontEnd/ios/GoogleService-Info.plist`
4. Add to Xcode project

### 3. Request Push Notification Permission

```typescript
import messaging from '@react-native-firebase/messaging';

async function requestUserPermission() {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    console.log('Authorization status:', authStatus);
    return true;
  }
  return false;
}
```

### 4. Get FCM Token

```typescript
import messaging from '@react-native-firebase/messaging';

async function getFCMToken() {
  const token = await messaging().getToken();
  console.log('FCM Token:', token);
  return token;
}
```

### 5. Send Token to Backend

When watching a camera:
```typescript
const token = await getFCMToken();
const platform = Platform.OS; // 'ios' or 'android'

await fetch('http://your-api.com/watch_camera', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    address: cameraAddress,
    client_id: clientId,
    timeToLive: 60, // minutes
    pushToken: token,
    platform: platform
  })
});
```

### 6. Handle Incoming Notifications

```typescript
import messaging from '@react-native-firebase/messaging';

// Foreground notifications
messaging().onMessage(async remoteMessage => {
  console.log('Notification received in foreground:', remoteMessage);
  // Show an alert or update UI
});

// Background/Quit notifications
messaging().setBackgroundMessageHandler(async remoteMessage => {
  console.log('Message handled in the background:', remoteMessage);
});
```

## API Endpoints

### Watch Camera (with Push Token)

**POST** `/watch_camera`

```json
{
  "address": "10_Ave_42_St",
  "client_id": "unique-user-id",
  "timeToLive": 60,
  "pushToken": "fcm-device-token-here",
  "platform": "android"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Camera added to watch list",
  "address": "10_Ave_42_St"
}
```

## Push Notification Format

When parking status changes, users receive:

**Notification:**
- Title: "Parking Update"
- Body: "10_Ave_42_St: Open parking spots available!"

**Data Payload:**
```json
{
  "camera_address": "10_Ave_42_St",
  "status": "open_parking",
  "timestamp": "2025-10-09T12:34:56.789Z"
}
```

## Status Messages

The backend translates status codes to user-friendly messages:

| Status | User Message |
|--------|-------------|
| `none` | "No parking detected" |
| `parked_cars` | "Only parked cars visible" |
| `open_parking` | "Open parking spots available!" |
| `both` | "Mixed - some spots available" |

## Troubleshooting

### Backend Issues

**"Firebase credentials not found"**
- Check that `firebase_credentials.json` exists in `backend/` directory
- Check `FIREBASE_CREDENTIALS_PATH` environment variable

**"Error initializing Firebase"**
- Verify the JSON file is valid
- Ensure you downloaded the correct service account key

### Frontend Issues

**Not receiving notifications on Android**
- Ensure `google-services.json` is in the correct location
- Check that Firebase Cloud Messaging is enabled in Firebase Console
- Verify app package name matches Firebase project

**Not receiving notifications on iOS**
- Upload APNs certificate to Firebase Console
- Enable Push Notifications capability in Xcode
- Check that app is registered for remote notifications

**Token is null/undefined**
- Check that you've requested notification permissions
- On iOS, user must grant permission
- Token may not be available immediately after app install

## Testing

### Test with a Single Device

1. Get your device's FCM token (print it in the app)
2. Use the backend to manually send a test notification:

```python
from helpers.push_notification import init_firebase, send_push_notification

init_firebase()
send_push_notification(
    push_token="your-device-token",
    title="Test Notification",
    body="This is a test",
    data={"test": "true"}
)
```

### Monitor in Firebase Console

Firebase Console → Cloud Messaging → View messages sent and delivery stats

## Production Considerations

1. **Token Refresh**: FCM tokens can change. Handle `messaging().onTokenRefresh()` in your app
2. **Invalid Tokens**: The backend automatically removes invalid tokens after failed sends
3. **Rate Limits**: Firebase has generous limits, but be aware of them for high-traffic apps
4. **Battery**: Push notifications are battery-efficient compared to WebSockets

## Cost

Firebase Cloud Messaging is **free** for unlimited notifications.

## Security

- **Never commit** `firebase_credentials.json` to version control
- The service account key has admin access to your Firebase project
- Use environment variables or secret management in production
- Rotate keys periodically

## Additional Resources

- [Firebase Cloud Messaging Documentation](https://firebase.google.com/docs/cloud-messaging)
- [React Native Firebase](https://rnfirebase.io/)
- [Expo Notifications](https://docs.expo.dev/push-notifications/overview/)


# Firebase Push Notification Setup - Final Steps

All the code has been implemented! Here's what you need to do to get push notifications working:

## Step 1: Place Firebase Config Files

You mentioned you've already downloaded these files from Firebase. Place them here:

**Android:**
```
frontEnd/android/app/google-services.json
```

**iOS:**
```
frontEnd/ios/GoogleService-Info.plist
```

## Step 2: Install Dependencies

```bash
cd frontEnd
npm install @react-native-firebase/app @react-native-firebase/messaging
```

## Step 3: iOS Setup (if testing on iOS)

```bash
cd ios
pod install
cd ..
```

## Step 4: Run the App

**For Android:**
```bash
npm run android
```

**For iOS:**
```bash
npm run ios
```

## Step 5: Test the Complete Flow

1. **Start Backend Services:**
   - Terminal 1: `cd backend && python main.py`
   - Terminal 2: `cd backend && python camera_watcher_service.py`

2. **Open the Mobile App:**
   - You should see a permission request for notifications
   - Grant permission

3. **Search for a Camera:**
   - Use "Find Nearest Parking" or "Search Cameras"
   - Camera images will load

4. **Click "Watch Camera" Button:**
   - Button should appear below each camera image
   - Click it to start watching
   - You'll see a confirmation alert

5. **Check Backend Logs:**
   - In the camera_watcher_service terminal, you should see:
     ```
     Found 1 cameras being watched
     Processing camera: 10_Ave_42_St
     ```

6. **Wait for Status Change:**
   - Within 5 minutes, if parking status changes
   - You'll receive a push notification on your device!

## What Was Implemented

### New Files Created:
- `hooks/useNotifications.ts` - Firebase notification hook
- `components/WatchCameraButton.tsx` - Watch/unwatch button component

### Files Modified:
- `App.tsx` - Initialize Firebase on app start
- `screens/NearestParkingScreen.tsx` - Added watch button to camera cards
- `screens/DirectSearchScreen.tsx` - Added watch button to camera cards
- `android/app/build.gradle` - Added Google Services plugin
- `android/build.gradle` - Added Google Services classpath

## Troubleshooting

### "No notification permission"
- Grant permission in Settings > Apps > Parking Spotter > Notifications

### "FCM Token is null"
- Check that google-services.json is in the correct location
- Rebuild the app: `npm run android --reset-cache`

### "Backend returns error"
- Make sure backend services are running
- Check that your device can reach localhost (use `adb reverse` or ngrok for Android)

### For Android Development:
```bash
# Forward backend port to Android emulator
adb reverse tcp:8000 tcp:8000
```

### For iOS Simulator:
- Use `http://localhost:8000` - should work automatically

### For Real Device:
- Backend needs to be accessible on your network
- Update `BACKEND_URL` in `.env` file to your computer's IP
- Example: `BACKEND_URL=http://192.168.1.100:8000`

## Expected Behavior

When you click "Watch Camera":
1. Button shows loading spinner
2. API call to backend with FCM token
3. Success alert appears
4. Button changes to "Stop Watching" with orange color
5. Backend starts monitoring that camera
6. You receive push notification when status changes!

## Next Steps

- Test with multiple cameras
- Test background notifications (put app in background)
- Test notification tap (should open app)
- Customize notification messages if needed


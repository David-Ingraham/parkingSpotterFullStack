import { useState, useEffect, useCallback } from 'react';
import { Platform, PermissionsAndroid, Alert } from 'react-native';
import messaging from '@react-native-firebase/messaging';

export function useNotifications() {
  const [fcmToken, setFcmToken] = useState<string | null>(null);
  const [isPermissionGranted, setIsPermissionGranted] = useState(false);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    try {
      if (Platform.OS === 'ios') {
        const authStatus = await messaging().requestPermission();
        const enabled =
          authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
          authStatus === messaging.AuthorizationStatus.PROVISIONAL;

        setIsPermissionGranted(enabled);
        return enabled;
      } else if (Platform.OS === 'android') {
        if (Platform.Version >= 33) {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
          );
          const enabled = granted === PermissionsAndroid.RESULTS.GRANTED;
          setIsPermissionGranted(enabled);
          return enabled;
        } else {
          // Android < 13 doesn't need runtime permission
          setIsPermissionGranted(true);
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('Error requesting permission:', error);
      return false;
    }
  }, []);

  // Get FCM token
  const getToken = useCallback(async () => {
    try {
      const token = await messaging().getToken();
      setFcmToken(token);
      console.log('FCM Token:', token);
      return token;
    } catch (error) {
      console.error('Error getting FCM token:', error);
      return null;
    }
  }, []);

  // Initialize notifications
  const initialize = useCallback(async () => {
    const hasPermission = await requestPermission();
    if (hasPermission) {
      await getToken();
    }
  }, [requestPermission, getToken]);

  // Listen for token refresh
  useEffect(() => {
    const unsubscribe = messaging().onTokenRefresh(token => {
      console.log('FCM Token refreshed:', token);
      setFcmToken(token);
    });

    return unsubscribe;
  }, []);

  // Setup notification handlers
  useEffect(() => {
    // Handle notifications when app is in foreground
    const unsubscribeForeground = messaging().onMessage(async remoteMessage => {
      console.log('Notification received in foreground:', remoteMessage);
      
      // Show alert to user
      if (remoteMessage.notification) {
        Alert.alert(
          remoteMessage.notification.title || 'Parking Update',
          remoteMessage.notification.body || 'Status changed'
        );
      }
    });

    // Handle notification opened app
    messaging().onNotificationOpenedApp(remoteMessage => {
      console.log('Notification opened app:', remoteMessage);
      // Navigate to specific camera if needed
      // navigation.navigate('CameraDetail', { address: remoteMessage.data?.camera_address });
    });

    // Check if app was opened by notification
    messaging()
      .getInitialNotification()
      .then(remoteMessage => {
        if (remoteMessage) {
          console.log('App opened by notification:', remoteMessage);
          // Navigate to specific camera
        }
      });

    return () => {
      unsubscribeForeground();
    };
  }, []);

  return {
    fcmToken,
    isPermissionGranted,
    requestPermission,
    initialize,
  };
}


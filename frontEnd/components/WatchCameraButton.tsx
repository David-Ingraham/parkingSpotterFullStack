import React, { useState } from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, Alert, Platform } from 'react-native';
import { API_CONFIG } from '../config';

interface WatchCameraButtonProps {
  cameraAddress: string;
  fcmToken: string | null;
  onWatchSuccess?: () => void;
}

export function WatchCameraButton({ cameraAddress, fcmToken, onWatchSuccess }: WatchCameraButtonProps) {
  const [isWatching, setIsWatching] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleWatch = async () => {
    if (!fcmToken) {
      Alert.alert(
        'Notifications Required',
        'Please enable notifications to watch cameras.',
        [{ text: 'OK' }]
      );
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/watch_camera`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: cameraAddress,
          client_id: `user_${Date.now()}`,
          timeToLive: 60,
          pushToken: fcmToken,
          platform: Platform.OS,
        }),
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        setIsWatching(true);
        Alert.alert(
          'Watching Camera',
          `You'll receive notifications when parking status changes at ${cameraAddress.replace(/_/g, ' ')}`,
          [{ text: 'OK' }]
        );
        onWatchSuccess?.();
      } else {
        throw new Error(data.message || 'Failed to watch camera');
      }
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to watch camera');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnwatch = async () => {
    setIsLoading(true);

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/unwatch_camera`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: cameraAddress,
          client_id: `user_${Date.now()}`,
        }),
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        setIsWatching(false);
        Alert.alert('Stopped Watching', 'You will no longer receive notifications for this camera.');
      } else {
        throw new Error(data.message || 'Failed to unwatch camera');
      }
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to unwatch camera');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <TouchableOpacity style={[styles.button, styles.buttonDisabled]} disabled>
        <ActivityIndicator size="small" color="#fff" />
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      style={[styles.button, isWatching ? styles.buttonWatching : styles.buttonWatch]}
      onPress={isWatching ? handleUnwatch : handleWatch}
      activeOpacity={0.8}
    >
      <Text style={styles.buttonText}>
        {isWatching ? 'Stop Watching' : 'Watch Camera'}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
  },
  buttonWatch: {
    backgroundColor: '#8B5FBF',
  },
  buttonWatching: {
    backgroundColor: '#FFB366',
  },
  buttonDisabled: {
    backgroundColor: '#666',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});


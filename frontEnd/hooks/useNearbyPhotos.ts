import { useState, useEffect } from 'react';
import { Alert, Platform, PermissionsAndroid } from 'react-native';
import Geolocation from 'react-native-geolocation-service';
import axios from 'axios';
import { API_CONFIG } from '../config';

const SERVER_URL = `${API_CONFIG.baseUrl}/fiveNearest`;

// NYC boundary coordinates
const NYC_BOUNDS = {
  LAT_MIN: 40.4774,
  LAT_MAX: 40.9176,
  LNG_MIN: -74.2591,
  LNG_MAX: -73.7004
} as const;

function isWithinNYC(lat: number, lng: number): boolean {
  return (
    NYC_BOUNDS.LAT_MIN <= lat &&
    lat <= NYC_BOUNDS.LAT_MAX &&
    NYC_BOUNDS.LNG_MIN <= lng &&
    lng <= NYC_BOUNDS.LNG_MAX
  );
}

// Shape of each item we're rendering
type PhotoItem = {
  address: string;
  uri: string;
};

/**
 * Ask for Android location permission at runtime.
 */
async function askLocationPermission(): Promise<boolean> {
  if (Platform.OS !== 'android') {
    return true;
  }

  const status = await PermissionsAndroid.request(
    PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
  );

  return status === PermissionsAndroid.RESULTS.GRANTED;
}

/**
 * Get the device's current position with high accuracy.
 */
function getCurrentPosition(): Promise<{ lat: number; lng: number }> {
  return new Promise((resolve, reject) => {
    Geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
      },
      (err) => reject(err),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
    );
  });
}

/**
 * POST lat/lng to the backend, parse JSON response,
 * and return an array of PhotoItem with data URI.
 */
async function fetchPhotos(
  lat: number,
  lng: number,
  numCams: number = 5
): Promise<PhotoItem[]> {
  try {
    const response = await fetch(SERVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat, lng, numCams }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const responseData = await response.json();
    const { images } = responseData;

    // Convert each image to PhotoItem - keep intermediate variable!
    const photos = images.map((img: any) => ({
      address: img.address,
      uri: img.url,
    }));
    
    return photos;
  } catch (err: any) {
    throw new Error(`Failed to fetch photos: ${err.message}`);
  }
}

/**
 * Custom hook to manage loading location + photos.
 */
export function useNearbyPhotos(numCams: number = 5) {
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [photos, setPhotos] = useState<PhotoItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPhotos() {
    setError(null);
    setLoading(true);
    setPhotos([]);

    try {
      if (Platform.OS === 'ios') {
        const status = await Geolocation.requestAuthorization('whenInUse');
        if (status !== 'granted') {
          throw new Error('Location permission denied');
        }
      } else if (Platform.OS === 'android') {
        const permission = await askLocationPermission();
        if (!permission) {
          throw new Error('Location permission denied');
        }
      }

      const { lat, lng } = await getCurrentPosition();
      
      // Set coordinates first so they're available even if NYC check fails
      setCoords({ lat, lng });
      
      // Check if coordinates are within NYC bounds
      if (!isWithinNYC(lat, lng)) {
        throw new Error('This Feature of Parking Spotter Only Works in NYC. Check your location services or VPNs');
      }

      const fetched = await fetchPhotos(lat, lng, numCams);
      setPhotos(fetched);
    } catch (err: any) {
      setError(err.message);
      // Alert.alert('Location Error', err.message);
    } finally {
      setLoading(false);
    }
  }

  return { coords, photos, loading, error, loadPhotos };
} 
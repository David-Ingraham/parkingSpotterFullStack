import { BACKEND_URL } from '@env';

// Force HTTPS in production
const enforceHttps = (url: string): string => {
  if (!__DEV__ && url && url.startsWith('http://')) {
    return url.replace('http://', 'https://');
  }
  return url;
};

// Get the appropriate backend URL
const getBackendUrl = (): string => {
  console.log('=== config.ts getBackendUrl ===');
  console.log('BACKEND_URL from .env:', BACKEND_URL);
  console.log('__DEV__ is:', __DEV__);
  
  if (__DEV__) {
    // In development, use the environment variable or fallback to emulator URL
    const url = BACKEND_URL || 'http://10.0.2.2:8000';
    console.log('Returning dev URL:', url);
    return url;
  } else {
    // In production, use the environment variable with a proper fallback
    const url = enforceHttps(BACKEND_URL || 'https://parkingspotterbackend.onrender.com');
    console.log('Returning prod URL:', url);
    return url;
  }
};

export const API_CONFIG = {
  baseUrl: getBackendUrl(),
  timeout: 15000,
  retryAttempts: 3,
  retryDelay: 1000,
};

// Sanitize any user input before sending to backend
export const sanitizeInput = (input: string): string => {
  return input.replace(/[<>]/g, '').trim();
};

// Error messages for users (no implementation details)
export const ERROR_MESSAGES = {
  NETWORK: 'Unable to connect. Please check your connection.',
  SERVER: 'Service temporarily unavailable. Please try again later.',
  LOCATION: 'Location services are required for this feature.',
  TIMEOUT: 'Request timed out. Please try again.',
} as const;
 
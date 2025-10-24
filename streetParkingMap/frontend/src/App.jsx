import React, { useState, useEffect } from 'react';
import ParkingMap from './components/ParkingMap';
import Legend from './components/Legend';
import api from './services/api';
import './App.css';

function App() {
  const [cameras, setCameras] = useState(null);
  const [lastScan, setLastScan] = useState(null);
  const [cameraCount, setCameraCount] = useState(0);
  const [scanInterval, setScanInterval] = useState(600); // Default 10 minutes
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch cameras from API
  const fetchCameras = async () => {
    try {
      const data = await api.getCameras();
      setCameras(data.cameras);
      setLastScan(data.last_scan);
      setCameraCount(data.camera_count);
      setScanInterval(data.scan_interval || 600);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
      setError('Failed to load camera data. Is the backend running?');
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchCameras();
  }, []);

  // Poll for updates every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchCameras();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading parking data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <div className="error-icon">⚠️</div>
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button onClick={fetchCameras} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="sidebar">
        <Legend 
          cameraCount={cameraCount}
          lastScan={lastScan}
          scanInterval={scanInterval}
        />
      </div>
      <div className="map-container">
        <ParkingMap cameras={cameras} />
      </div>
    </div>
  );
}

export default App;


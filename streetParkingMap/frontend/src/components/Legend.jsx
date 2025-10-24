import React from 'react';

const Legend = ({ cameraCount, lastScan, scanInterval }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  const getNextScanTime = (lastScan, interval) => {
    if (!lastScan) return 'Soon';
    const nextScan = new Date((lastScan + interval) * 1000);
    return nextScan.toLocaleTimeString();
  };

  return (
    <div className="legend">
      <h2>Manhattan Parking Map</h2>
      
      <div className="legend-stats">
        <div className="stat">
          <span className="stat-label">Cameras:</span>
          <span className="stat-value">{cameraCount || 0}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Last Scan:</span>
          <span className="stat-value">{formatTime(lastScan)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Next Scan:</span>
          <span className="stat-value">{getNextScanTime(lastScan, scanInterval)}</span>
        </div>
      </div>

      <div className="legend-items">
        <h3>Status Legend</h3>
        <div className="legend-item">
          <div className="marker-icon green"></div>
          <span>Parking Available</span>
        </div>
        <div className="legend-item">
          <div className="marker-icon red"></div>
          <span>No Parking Available</span>
        </div>
        <div className="legend-item">
          <div className="marker-icon gray"></div>
          <span>No Data / Offline</span>
        </div>
      </div>

      <div className="legend-info">
        <p>
          Cameras are scanned every {Math.floor(scanInterval / 60)} minutes using 
          computer vision to detect parking availability.
        </p>
      </div>
    </div>
  );
};

export default Legend;


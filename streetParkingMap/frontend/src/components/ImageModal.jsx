import React, { useState } from 'react';

const ImageModal = ({ camera, onClose }) => {
  const [zoom, setZoom] = useState(1);

  if (!camera) return null;

  const formatAddress = (address) => {
    return address.replace(/_/g, ' ');
  };

  const handleBackdropClick = (e) => {
    if (e.target.classList.contains('modal-backdrop')) {
      onClose();
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 3)); // Max 3x zoom
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 0.5)); // Min 0.5x zoom
  };

  const handleResetZoom = () => {
    setZoom(1);
  };

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>
          ×
        </button>
        
        <div className="modal-header">
          <h2>{formatAddress(camera.address)}</h2>
          <p className="modal-subtitle">Detection Image</p>
        </div>

        <div className="modal-body">
          {camera.annotated_image ? (
            <>
              <div className="zoom-controls">
                <button 
                  onClick={handleZoomOut} 
                  className="zoom-button"
                  disabled={zoom <= 0.5}
                  title="Zoom Out"
                >
                  −
                </button>
                <span className="zoom-level">{Math.round(zoom * 100)}%</span>
                <button 
                  onClick={handleZoomIn} 
                  className="zoom-button"
                  disabled={zoom >= 3}
                  title="Zoom In"
                >
                  +
                </button>
                {zoom !== 1 && (
                  <button 
                    onClick={handleResetZoom} 
                    className="zoom-reset"
                    title="Reset Zoom"
                  >
                    Reset
                  </button>
                )}
              </div>
              <div className="image-container">
                <img
                  src={`data:image/jpeg;base64,${camera.annotated_image}`}
                  alt={`Detection for ${formatAddress(camera.address)}`}
                  className="detection-image"
                  style={{ transform: `scale(${zoom})` }}
                />
              </div>
            </>
          ) : (
            <div className="no-image">
              <p>No detection image available</p>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="modal-stats">
            {camera.parked_cars_count > 0 && (
              <div className="modal-stat">
                <span className="stat-icon">🚗</span>
                <span>{camera.parked_cars_count} Parked Cars</span>
                <span className="stat-confidence">
                  ({(camera.parked_cars_confidence * 100).toFixed(1)}%)
                </span>
              </div>
            )}
            {camera.open_parking_count > 0 && (
              <div className="modal-stat">
                <span className="stat-icon">🅿️</span>
                <span>{camera.open_parking_count} Open Spots</span>
                <span className="stat-confidence">
                  ({(camera.open_parking_confidence * 100).toFixed(1)}%)
                </span>
              </div>
            )}
            {camera.parked_cars_count === 0 && camera.open_parking_count === 0 && (
              <div className="modal-stat">
                <span className="stat-icon">⚪</span>
                <span>No detections</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageModal;


import React, { useMemo, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import ImageModal from './ImageModal';

const ParkingMap = ({ cameras }) => {
  // Manhattan center coordinates
  const center = [40.7831, -73.9712];
  const zoom = 12;

  // Modal state
  const [selectedCamera, setSelectedCamera] = useState(null);

  // Color mapping for status
  const getMarkerColor = (status) => {
    switch (status) {
      case 'open_parking':
        return '#10b981'; // Green - parking available!
      case 'parked_cars':
        return '#ef4444'; // Red - no parking
      case 'none':
      default:
        return '#9ca3af'; // Gray - no data
    }
  };

  // Convert cameras object to array
  const cameraArray = useMemo(() => {
    if (!cameras) return [];
    return Object.values(cameras);
  }, [cameras]);

  const formatAddress = (address) => {
    return address.replace(/_/g, ' ');
  };

  const formatTime = (isoString) => {
    if (!isoString) return 'Unknown';
    const date = new Date(isoString);
    return date.toLocaleTimeString();
  };

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: '100%', width: '100%' }}
      className="parking-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {cameraArray.map((camera) => (
        <CircleMarker
          key={camera.address}
          center={[camera.latitude, camera.longitude]}
          radius={8}
          fillColor={getMarkerColor(camera.status)}
          color="#fff"
          weight={2}
          opacity={1}
          fillOpacity={0.8}
        >
          <Popup>
            <div className="camera-popup">
              <h3>{formatAddress(camera.address)}</h3>
              
              <div className="popup-status">
                <span 
                  className="status-indicator"
                  style={{ backgroundColor: getMarkerColor(camera.status) }}
                ></span>
                <span className="status-text">
                  {camera.status === 'open_parking' && 'Parking Available'}
                  {camera.status === 'parked_cars' && 'No Parking Available'}
                  {camera.status === 'none' && 'No Data'}
                </span>
              </div>

              <div className="popup-details">
                {camera.parked_cars_count > 0 && (
                  <div className="detail-row">
                    <span>Parked Cars:</span>
                    <span>{camera.parked_cars_count} detected</span>
                  </div>
                )}
                {camera.open_parking_count > 0 && (
                  <div className="detail-row">
                    <span>Open Spots:</span>
                    <span>{camera.open_parking_count} detected</span>
                  </div>
                )}
                {camera.parked_cars_confidence > 0 && (
                  <div className="detail-row">
                    <span>Parked Confidence:</span>
                    <span>{(camera.parked_cars_confidence * 100).toFixed(1)}%</span>
                  </div>
                )}
                {camera.open_parking_confidence > 0 && (
                  <div className="detail-row">
                    <span>Open Confidence:</span>
                    <span>{(camera.open_parking_confidence * 100).toFixed(1)}%</span>
                  </div>
                )}
                <div className="detail-row">
                  <span>Last Scanned:</span>
                  <span>{formatTime(camera.last_scanned)}</span>
                </div>
              </div>

              {camera.annotated_image && (
                <button 
                  className="view-image-button"
                  onClick={() => setSelectedCamera(camera)}
                >
                  🔍 View Detection Image
                </button>
              )}
            </div>
          </Popup>
        </CircleMarker>
      ))}

      {selectedCamera && (
        <ImageModal 
          camera={selectedCamera} 
          onClose={() => setSelectedCamera(null)} 
        />
      )}
    </MapContainer>
  );
};

export default ParkingMap;


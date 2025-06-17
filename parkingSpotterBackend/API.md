# Parking Spotter API Documentation

## Overview

Simple REST API for accessing NYC parking camera data. Designed for privacy - no user data collection or tracking.

## Base URL

```
Production: https://parkingspotterbackend.onrender.com
Development: http://localhost:8000
```

## Rate Limiting

- **50 requests per hour** per IP address
- **1 request per second** per endpoint
- Returns `429 Too Many Requests` when exceeded

## Endpoints

### 1. Find Nearest Cameras

Get the 5 closest parking cameras to given coordinates.

**Endpoint:** `POST /five_nearest`

**Request Body:**
```json
{
  "lat": 40.7589,
  "lng": -73.9851
}
```

**Response:**
```json
{
  "images": [
    {
      "address": "Camera_Address_Name",
      "url": "data:image/jpeg;base64,..."
    }
  ]
}
```

**Error Responses:**
- `400` - Invalid coordinates
- `429` - Rate limit exceeded
- `500` - Server error

### 2. Search Specific Cameras

Get images for specific camera addresses.

**Endpoint:** `POST /search_cameras`

**Request Body:**
```json
{
  "addresses": ["Camera_Address_1", "Camera_Address_2"]
}
```

**Response:**
```json
{
  "images": [
    {
      "address": "Camera_Address_1",
      "url": "data:image/jpeg;base64,..."
    }
  ]
}
```

### 3. Camera Watching (WebSocket Features)

**Start Watching:** `POST /watch_camera`
```json
{
  "address": "Camera_Address",
  "client_id": "unique_client_id",
  "notification_interval": 30
}
```

**Stop Watching:** `POST /unwatch_camera`
```json
{
  "address": "Camera_Address",
  "client_id": "unique_client_id"
}
```

## Data Format

**Coordinates:**
- Latitude: Float between 40.4774 and 40.9176 (NYC bounds)
- Longitude: Float between -74.2591 and -73.7004 (NYC bounds)

**Camera Addresses:**
- Format: `Street_Name_and_Cross_Street`
- Example: `BROADWAY_at_42ND_ST`

**Images:**
- Format: Base64-encoded JPEG
- Prefix: `data:image/jpeg;base64,`

## Error Handling

**Common Error Codes:**
- `400` - Bad Request (invalid input)
- `404` - Camera not found
- `429` - Rate limit exceeded
- `500` - Internal server error

**Error Response Format:**
```json
{
  "status": "error",
  "message": "Description of error"
}
```

## Privacy Notes

- No user authentication required
- No personal data stored
- Location coordinates are not logged
- Requests are anonymous

## Usage Examples

**Find nearest cameras with cURL:**
```bash
curl -X POST https://parkingspotterbackend.onrender.com/five_nearest \
  -H "Content-Type: application/json" \
  -d '{"lat": 40.7589, "lng": -73.9851}'
```

**Search specific camera:**
```bash
curl -X POST https://parkingspotterbackend.onrender.com/search_cameras \
  -H "Content-Type: application/json" \
  -d '{"addresses": ["BROADWAY_at_42ND_ST"]}'
```

## Development

**Local Testing:**
```bash
# Start backend
cd parkingSpotterBackend
python main.py

# Test endpoint
curl -X POST http://localhost:8000/five_nearest \
  -H "Content-Type: application/json" \
  -d '{"lat": 40.7589, "lng": -73.9851}'
```

## Support

- Create an issue on GitHub for API problems
- Check status at: [Backend URL]/health (when health endpoint is added)
- Response time typically under 2 seconds

---

**Note: This API is designed for the Parking Spotter mobile app but can be used by other applications respecting rate limits.** 
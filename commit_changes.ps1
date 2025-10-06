# PowerShell script to commit each file individually

# 1. Database Models
git add database/models.py
git commit -m "feat(database): add camera metadata and confidence tracking

- Add camera_id, latitude, longitude fields to Camera model
- Add parked_cars_confidence and open_parking_confidence fields
- Change last_status default to None (null) for unscanned cameras
- Remove last_checked field (no longer needed)
- Rename notification_interval to time_to_live for clarity
- Add helper function get_watched_cameras() to query cameras with active watchers"
git push

# 2. Watch Camera Route
git add routes/watch_camera.py
git commit -m "refactor(api): rename notification_interval to timeToLive

- Update /watch_camera endpoint to use timeToLive parameter
- Update validation function name for consistency
- Update response format to remove last_checked field
- Validate cameras against database instead of JSON file"
git push

# 3. Populate Cameras Script
git add scripts/populate_cameras.py
git commit -m "feat(scripts): add one-time camera population script

- Create script to populate all cameras from JSON into database
- Handles both initial population and updates to existing cameras
- Designed to run once manually, not on every server start"
git push

# 4. Camera Watcher Service
git add camera_watcher_service.py
git commit -m "feat(vision): add background camera monitoring service

- Create polling service that runs every 5 minutes
- Fetch images from watched cameras and run YOLO vision model
- Calculate average confidence for parkedCars and openParking classes
- Determine camera status: none, parked_cars, open_parking, or both
- Notify connected users via websocket when status changes
- Store confidence values in database for future comparison"
git push

# 5. WebSocket Server
git add websocket_server.py
git commit -m "fix(websocket): simplify emit_camera_update function

- Remove redundant database update (handled by watcher service)
- Add debug logging for notification delivery
- Clean up error handling"
git push

# 6. Main Server
git add main.py
git commit -m "refactor(init): remove automatic camera population on startup

- Camera population now handled by one-time manual script
- Reduces server startup time and unnecessary database operations"
git push

Write-Host "All changes committed and pushed successfully!" -ForegroundColor Green

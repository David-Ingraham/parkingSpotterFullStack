# Database Setup

## Local Development (SQLite)

For local development, the app uses SQLite - no setup required!

### Automatic Setup

The database file will be created automatically at `backend/parking_spotter.db` when you first run the application.

### Initialize Database

1. **Populate cameras** (one-time):
   ```bash
   cd backend
   python scripts/populate_cameras.py
   ```

2. **Add push notification fields** (if updating existing DB):
   ```bash
   python scripts/add_push_notification_fields.py
   ```

That's it! SQLite database is ready to use.

### Database Location

`backend/parking_spotter.db` - This file is gitignored

### Viewing the Database

You can use any SQLite browser:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (recommended)
- SQLite CLI: `sqlite3 parking_spotter.db`
- VS Code extension: SQLite Viewer

## Production Deployment (PostgreSQL/MySQL)

For production, you can use any database by setting the `DATABASE_URL` environment variable:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/dbname

# MySQL
DATABASE_URL=mysql://user:password@host:port/dbname
```

The app will automatically use the provided DATABASE_URL instead of SQLite.

## Database Schema

### Tables

**cameras**
- `address` (primary key) - Camera location identifier
- `camera_id` - NYC DOT camera UUID
- `latitude`, `longitude` - Geographic coordinates
- `last_status` - Most recent parking status (null, "none", "parked_cars", "open_parking", "both")
- `parked_cars_confidence` - Average detection confidence
- `open_parking_confidence` - Average detection confidence

**watchers**
- `id` (primary key)
- `camera_address` (foreign key to cameras)
- `client_id` - Unique client identifier
- `time_to_live` - Watch duration in minutes (10-180)
- `expires_at` - Expiration timestamp
- `is_connected` - WebSocket connection status
- `push_token` - FCM device token (nullable)
- `platform` - 'ios' or 'android' (nullable)
- `created_at` - Registration timestamp

**camera_status_history**
- `id` (primary key)
- `camera_address` (foreign key to cameras)
- `status` - Historical status value
- `recorded_at` - Timestamp

## Migration Scripts

### populate_cameras.py
Loads all NYC traffic cameras from `camera_id_lat_lng_wiped.json` into the database.

Run once to initialize camera data.

### add_push_notification_fields.py
Adds push notification columns to an existing watchers table.

Only needed if you're upgrading from an older version without push notification support.

## Troubleshooting

### "No such table: cameras"
Run: `python scripts/populate_cameras.py`

### "No such column: push_token"
Run: `python scripts/add_push_notification_fields.py`

### Database locked
- Close any SQLite browser windows
- Make sure only one process is accessing the database
- Restart your services

### Start fresh
Delete `parking_spotter.db` and run `populate_cameras.py` again.

## Backup

To backup your SQLite database:
```bash
cp parking_spotter.db parking_spotter_backup.db
```

Or use SQLite's built-in backup:
```bash
sqlite3 parking_spotter.db ".backup parking_spotter_backup.db"
```

## No Environment Variables Needed!

Unlike the old PostgreSQL setup, SQLite doesn't need:
- ~~DB_USER~~
- ~~DB_PASSWORD~~
- ~~DB_HOST~~
- ~~DB_PORT~~
- ~~DB_NAME~~

Just run the scripts and you're done!


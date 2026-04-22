#!/bin/bash

# test_email_notifications.sh
# Script to test email notifications with image attachments

set -e  # Exit on any error

DB_PATH="./watchlist.sqlite3"
YOUR_EMAIL="your-email@example.com"  # CHANGE THIS!

echo "Setting up test for email notifications..."

# 1. Initialize the database with schema
echo "Creating database schema..."
sqlite3 "$DB_PATH" << 'EOF'
CREATE TABLE IF NOT EXISTS camera_state (
    address TEXT PRIMARY KEY,
    camera_id TEXT NOT NULL,
    open_parking_status INTEGER,
    last_checked_utc TEXT,
    last_status_change_utc TEXT
);

CREATE TABLE IF NOT EXISTS watchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    email TEXT NOT NULL,
    requested_minutes INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL,
    expires_at_utc TEXT NOT NULL,
    notified_on_current_status INTEGER NOT NULL DEFAULT 0,
    UNIQUE(address, email)
);

CREATE INDEX IF NOT EXISTS idx_watchers_address ON watchers(address);
CREATE INDEX IF NOT EXISTS idx_watchers_expires ON watchers(expires_at_utc);
EOF

# 2. Add camera and watcher
echo "Adding camera state and watcher for $YOUR_EMAIL..."
sqlite3 "$DB_PATH" << EOF
INSERT OR REPLACE INTO camera_state (address, camera_id, open_parking_status, last_checked_utc, last_status_change_utc)
VALUES ('Delancey_St_Bowery_St', 'a3058350-1552-459f-8379-2fd06895e70a', 0, datetime('now'), datetime('now'));

INSERT OR REPLACE INTO watchers (address, email, requested_minutes, created_at_utc, expires_at_utc, notified_on_current_status)
VALUES ('Delancey_St_Bowery_St', '$YOUR_EMAIL', 60, datetime('now'), datetime('now', '+60 minutes'), 0);
EOF

# 3. Verify setup
echo "Verifying setup..."
sqlite3 "$DB_PATH" << 'EOF'
SELECT 'Camera state:' as label;
SELECT * FROM camera_state WHERE address = 'Delancey_St_Bowery_St';

SELECT 'Watchers:' as label;
SELECT * FROM watchers WHERE address = 'Delancey_St_Bowery_St';
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure gunicorn is running (the worker needs to be active)"
ho "2. Run this command to trigger the notification:"
echo ""
echo "   sqlite3 $DB_PATH \"UPDATE camera_state SET open_parking_status = 1, last_status_change_utc = datetime('now') WHERE address = 'Delancey_St_Bowery_St'; UPDATE watchers SET notified_on_current_status = 0 WHERE address = 'Delancey_St_Bowery_St';\""
echo ""
echo "3. Check your email at $YOUR_EMAIL for the notification with image attachment"
echo "4. Check gunicorn logs for 'Notified X watcher(s)' and 'attachment_bytes=N' messages"

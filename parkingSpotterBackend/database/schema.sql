-- Cameras table stores basic camera info and current status
CREATE TABLE cameras (
    address VARCHAR(255) PRIMARY KEY,
    last_status VARCHAR(50) DEFAULT 'unknown',
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- Watchers table stores watch relationships and settings
CREATE TABLE watchers (
    id SERIAL PRIMARY KEY,
    camera_address VARCHAR(255) REFERENCES cameras(address),
    client_id VARCHAR(255) NOT NULL,
    notification_interval INTEGER NOT NULL CHECK (notification_interval >= 10 AND notification_interval <= 180 AND notification_interval % 5 = 0),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_connected BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(camera_address, client_id)  -- Prevent duplicate watches
);

-- Optional: Camera status history
CREATE TABLE camera_status_history (
    id SERIAL PRIMARY KEY,
    camera_address VARCHAR(255) REFERENCES cameras(address),
    status VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster expiration checks
CREATE INDEX idx_watchers_expires_at ON watchers(expires_at);

-- Index for status history queries
CREATE INDEX idx_status_history_camera_time ON camera_status_history(camera_address, recorded_at); 
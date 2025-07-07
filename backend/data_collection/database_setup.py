import sqlite3
import os
from datetime import datetime

def create_database():
    """Create SQLite database and table for car count history"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'traffic_data.db')
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create car_count_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_count_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_address TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            car_count INTEGER NOT NULL,
            confidence_score REAL,
            processing_time REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_camera_timestamp 
        ON car_count_history(camera_address, timestamp)
    ''')
    
    # Create processing_status table for tracking batches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_timestamp TEXT NOT NULL,
            cameras_processed INTEGER NOT NULL,
            cameras_failed INTEGER NOT NULL,
            total_cameras INTEGER NOT NULL,
            processing_time REAL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Database created successfully at: {db_path}")
    return db_path

def get_database_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'traffic_data.db')
    return sqlite3.connect(db_path)

def insert_car_count(camera_address, timestamp, car_count, confidence_score, processing_time):
    """Insert a single car count record"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO car_count_history 
        (camera_address, timestamp, car_count, confidence_score, processing_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (camera_address, timestamp, car_count, confidence_score, processing_time))
    
    conn.commit()
    conn.close()

def insert_batch_status(batch_timestamp, cameras_processed, cameras_failed, total_cameras, processing_time, status):
    """Insert batch processing status"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO processing_status 
        (batch_timestamp, cameras_processed, cameras_failed, total_cameras, processing_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (batch_timestamp, cameras_processed, cameras_failed, total_cameras, processing_time, status))
    
    conn.commit()
    conn.close()

def get_last_batch_timestamp():
    """Get the timestamp of the last successful batch"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT MAX(batch_timestamp) FROM processing_status 
        WHERE status = 'completed'
    ''')
    
    result = cursor.fetchone()[0]
    conn.close()
    
    return result

if __name__ == "__main__":
    # Create database when run directly
    create_database()
    print("Database setup complete!") 
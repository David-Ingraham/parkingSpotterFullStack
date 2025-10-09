"""
Database migration script to add push notification fields to Watcher table

Run this once to update an existing database with the new push notification columns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import engine

def add_push_notification_fields():
    """Add push_token and platform columns to watchers table"""
    
    print("Adding push notification fields to watchers table...")
    
    try:
        with engine.connect() as conn:
            # SQLite: Check if columns exist using PRAGMA
            from sqlalchemy import text
            
            result = conn.execute(text("PRAGMA table_info(watchers)"))
            existing_columns = [row[1] for row in result]
            
            # Add push_token if it doesn't exist
            if 'push_token' not in existing_columns:
                print("Adding push_token column...")
                conn.execute(text("ALTER TABLE watchers ADD COLUMN push_token VARCHAR(500)"))
                conn.commit()
                print("✓ push_token column added")
            else:
                print("✓ push_token column already exists")
            
            # Add platform if it doesn't exist
            if 'platform' not in existing_columns:
                print("Adding platform column...")
                conn.execute(text("ALTER TABLE watchers ADD COLUMN platform VARCHAR(20)"))
                conn.commit()
                print("✓ platform column added")
            else:
                print("✓ platform column already exists")
        
        print("\nMigration completed successfully!")
        print("The database is now ready for push notifications.")
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        print("\nIf you're starting with a fresh database, you can ignore this")
        print("and just run: python scripts/populate_cameras.py")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Push Notification Database Migration")
    print("=" * 60)
    print()
    
    response = input("This will modify the watchers table. Continue? (y/n): ")
    if response.lower() == 'y':
        add_push_notification_fields()
    else:
        print("Migration cancelled.")


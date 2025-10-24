from database.models import Camera, Watcher
from database.db import SessionLocal
from datetime import datetime

def print_watches():
    """Print all current watches in the database"""
    db = SessionLocal()
    try:
        print("\n=== Current Database State ===\n")
        cameras = db.query(Camera).all()
        if not cameras:
            print("No cameras in database yet!")
            return

        for camera in cameras:
            print(f"\nCamera: {camera.address}")
            print(f"Status: {camera.last_status}")
            print(f"Last Checked: {camera.last_checked}")
            
            if camera.watchers:
                print("\nWatchers:")
                for watcher in camera.watchers:
                    print(f"  Client: {watcher.client_id}")
                    print(f"    Interval: {watcher.notification_interval} mins")
                    print(f"    Expires: {watcher.expires_at}")
                    print(f"    Connected: {watcher.is_connected}")
            else:
                print("\nNo active watchers")
            print("\n" + "-"*50)
    except Exception as e:
        print(f"Error accessing database: {e}")
    finally:
        db.close()

def print_summary():
    """Print a summary of database statistics"""
    db = SessionLocal()
    try:
        print("\n=== Database Summary ===\n")
        
        # Count cameras
        camera_count = db.query(Camera).count()
        print(f"Total Cameras: {camera_count}")
        
        # Count watchers
        watcher_count = db.query(Watcher).count()
        print(f"Total Watchers: {watcher_count}")
        
        # Count active watchers (not expired)
        active_watchers = db.query(Watcher).filter(
            Watcher.expires_at > datetime.now()
        ).count()
        print(f"Active Watchers: {active_watchers}")
        
        # Most watched cameras
        print("\nMost Watched Cameras:")
        most_watched = db.query(
            Camera.address,
            db.func.count(Watcher.id).label('watcher_count')
        ).join(Watcher).group_by(Camera.address).order_by(
            db.func.count(Watcher.id).desc()
        ).limit(5).all()
        
        for camera, count in most_watched:
            print(f"  {camera}: {count} watchers")
    except Exception as e:
        print(f"Error generating summary: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print_summary()
    print_watches() 
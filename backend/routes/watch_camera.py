from flask import Blueprint, request, jsonify
from flask_socketio import emit
from datetime import datetime, timezone, timedelta
import json
from sqlalchemy.exc import IntegrityError
from database.models import Camera, Watcher
from database.db import SessionLocal

bp = Blueprint('watch_camera', __name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_camera_data():
    """Load camera data to validate addresses"""
    try:
        with open('camera_id_lat_lng_wiped.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading camera data: {e}")
        return {}

def is_valid_time_to_live(ttl):
    """Check if time to live is valid (10-180 mins, multiple of 5)"""
    return (
        isinstance(ttl, int) and 
        10 <= ttl <= 180 and 
        ttl % 5 == 0
    )

def cleanup_expired_watches():
    """Remove expired watch entries"""
    db = next(get_db())
    try:
        # Delete expired watchers
        db.query(Watcher).filter(
            Watcher.expires_at < datetime.now(timezone.utc)
        ).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error cleaning up expired watches: {e}")
    finally:
        db.close()

@bp.route("/watch_camera", methods=['POST'])
def watch_camera():
    data = request.get_json()
    db = next(get_db())
    
    try:
        # Validate required fields
        required_fields = ['address', 'client_id', 'timeToLive']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "message": f"Missing required fields. Need: {', '.join(required_fields)}"
            }), 400
        
        # Optional push notification fields
        push_token = data.get('pushToken')
        platform = data.get('platform')  # 'ios' or 'android'
        
        # Validate time to live
        if not is_valid_time_to_live(data['timeToLive']):
            return jsonify({
                "status": "error",
                "message": "Invalid timeToLive. Must be between 10-180 minutes and multiple of 5."
            }), 400
        
        # Validate camera exists in database
        camera = db.query(Camera).filter_by(address=data['address']).first()
        if not camera:
            return jsonify({
                "status": "error",
                "message": "Invalid camera address"
            }), 400
        
        # Clean up expired watches
        cleanup_expired_watches()
        
        # Calculate expiration time based on time to live
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=data['timeToLive'])
        
        # Get existing watcher or create new one
        watcher = db.query(Watcher).filter_by(
            camera_address=data['address'],
            client_id=data['client_id']
        ).first()
        
        if watcher:
            # Update existing watcher
            watcher.time_to_live = data['timeToLive']
            watcher.expires_at = expires_at
            if push_token:
                watcher.push_token = push_token
                watcher.platform = platform
            message = "Watch parameters updated"
        else:
            # Create new watcher
            watcher = Watcher(
                camera_address=data['address'],
                client_id=data['client_id'],
                time_to_live=data['timeToLive'],
                expires_at=expires_at,
                push_token=push_token,
                platform=platform
            )
            db.add(watcher)
            message = "Camera added to watch list"
        
        db.commit()
        
        return jsonify({
            "status": "success",
            "message": message,
            "address": data['address']
        })
        
    except IntegrityError as e:
        db.rollback()
        return jsonify({
            "status": "error",
            "message": "Database constraint violation"
        }), 400
    except Exception as e:
        db.rollback()
        print(f"Error in watch_camera: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
    finally:
        db.close()

@bp.route("/unwatch_camera", methods=['POST'])
def unwatch_camera():
    data = request.get_json()
    db = next(get_db())
    
    try:
        # Validate required fields
        if not data or 'address' not in data or 'client_id' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required fields: address and client_id"
            }), 400
        
        # Find and delete the watch
        deleted = db.query(Watcher).filter_by(
            camera_address=data['address'],
            client_id=data['client_id']
        ).delete()
        
        if deleted:
            db.commit()
            return jsonify({
                "status": "success",
                "message": "Camera removed from watch list"
            })
        
        return jsonify({
            "status": "error",
            "message": "Watch not found"
        }), 404
        
    except Exception as e:
        db.rollback()
        print(f"Error in unwatch_camera: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
    finally:
        db.close()

# Helper function to get all watched cameras
def get_watched_cameras():
    """Get all active watches from database"""
    db = next(get_db())
    try:
        cleanup_expired_watches()
        
        # Get all cameras with their watchers
        cameras = db.query(Camera).all()
        
        # Convert to the same format as before for compatibility
        result = {}
        for camera in cameras:
            result[camera.address] = {
                "watchers": {
                    w.client_id: {
                        "time_to_live": w.time_to_live,
                        "expires_at": int(w.expires_at.timestamp() * 1000),
                        "is_connected": w.is_connected
                    } for w in camera.watchers
                },
                "last_status": camera.last_status
            }
        
        return result
    finally:
        db.close() 
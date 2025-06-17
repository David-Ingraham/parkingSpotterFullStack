from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
from routes.watch_camera import get_watched_cameras
from database.db import SessionLocal
from database.models import Watcher, Camera
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def emit_camera_update(camera_address, new_status):
    """
    Emit a camera status update to all connected clients watching this camera.
    
    Args:
        camera_address: The address of the camera that changed status
        new_status: The new status of the camera
    """
    db = next(get_db())
    try:
        # Get all connected watchers for this camera
        watchers = db.query(Watcher).filter_by(
            camera_address=camera_address,
            is_connected=True
        ).all()
        
        # Update camera status in database
        camera = db.query(Camera).filter_by(address=camera_address).first()
        if camera:
            camera.last_status = new_status
            camera.last_checked = datetime.now(timezone.utc)
            db.commit()
        
        # Emit update to each connected watcher
        for watcher in watchers:
            socketio.emit('camera_update', {
                'address': camera_address,
                'status': new_status,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=watcher.client_id)
            
    except Exception as e:
        print(f"Error emitting camera update: {e}")
        db.rollback()
    finally:
        db.close()

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected with SID: {request.sid}")
    
    # Client must send their client_id in the connection query string
    client_id = request.args.get('client_id')
    if not client_id:
        print("Client connection rejected - no client_id provided")
        return False  # Reject the connection
    
    # Update database to mark this client's watchers as connected
    db = next(get_db())
    try:
        watchers = db.query(Watcher).filter_by(client_id=client_id).all()
        for watcher in watchers:
            watcher.is_connected = True
        db.commit()
        print(f"Marked watchers for client {client_id} as connected")
        
        # Join a room named after their client_id for targeted events
        socketio.server.enter_room(request.sid, client_id)
        
    except Exception as e:
        print(f"Error updating watcher connection status: {e}")
        db.rollback()
    finally:
        db.close()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected with SID: {request.sid}")
    
    # Get client_id from session
    client_id = request.args.get('client_id')
    if not client_id:
        return
    
    # Update database to mark this client's watchers as disconnected
    db = next(get_db())
    try:
        watchers = db.query(Watcher).filter_by(client_id=client_id).all()
        for watcher in watchers:
            watcher.is_connected = False
        db.commit()
        print(f"Marked watchers for client {client_id} as disconnected")
        
        # Leave the client_id room
        socketio.server.leave_room(request.sid, client_id)
        
    except Exception as e:
        print(f"Error updating watcher disconnection status: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting WebSocket server on http://0.0.0.0:8001")
    socketio.run(app, host="0.0.0.0", port=8001)
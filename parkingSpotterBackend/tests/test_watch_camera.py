import pytest
import json
from database.models import Camera, Watcher

def test_watch_camera(test_client, db_session):
    """Test adding a watch for a camera."""
    # Test data
    data = {
        "address": "Park_Ave_106_St",  # Using a real camera from our JSON
        "client_id": "test_client_1",
        "notification_interval": 15,
        "expires_at": 1711036800000  # Some future timestamp
    }

    # Make the request
    response = test_client.post(
        '/watch_camera',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 200
    assert response.json['status'] == 'success'

    # Verify database state
    camera = db_session.query(Camera).filter_by(address=data['address']).first()
    assert camera is not None
    assert camera.address == data['address']

    watcher = db_session.query(Watcher).filter_by(
        camera_address=data['address'],
        client_id=data['client_id']
    ).first()
    assert watcher is not None
    assert watcher.notification_interval == data['notification_interval']

def test_unwatch_camera(test_client, db_session):
    """Test removing a watch for a camera."""
    # First add a watch
    camera = Camera(address="Park_Ave_106_St", last_status="unknown")
    watcher = Watcher(
        camera_address="Park_Ave_106_St",
        client_id="test_client_1",
        notification_interval=15,
        expires_at=1711036800000,
        is_connected=True
    )
    db_session.add(camera)
    db_session.add(watcher)
    db_session.commit()

    # Test data for unwatch
    data = {
        "address": "Park_Ave_106_St",
        "client_id": "test_client_1"
    }

    # Make the request
    response = test_client.post(
        '/unwatch_camera',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 200
    assert response.json['status'] == 'success'

    # Verify database state
    watcher = db_session.query(Watcher).filter_by(
        camera_address=data['address'],
        client_id=data['client_id']
    ).first()
    assert watcher is None  # Watcher should be deleted

    # Camera should still exist
    camera = db_session.query(Camera).filter_by(address=data['address']).first()
    assert camera is not None 
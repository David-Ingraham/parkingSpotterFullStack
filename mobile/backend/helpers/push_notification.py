import firebase_admin
from firebase_admin import credentials, messaging
import os

# Initialize Firebase Admin (do this once at startup)
def init_firebase():
    """
    Initialize Firebase Admin SDK with service account
    
    Expects FIREBASE_CREDENTIALS_PATH environment variable or
    firebase-credentials.json in the backend directory
    """
    if firebase_admin._apps:
        print("Firebase already initialized")
        return
    
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase_credentials.json')
    
    if not os.path.exists(cred_path):
        print(f"WARNING: Firebase credentials not found at {cred_path}")
        print("Push notifications will not work. Please set up Firebase.")
        return
    
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

def send_push_notification(push_token, title, body, data=None):
    """
    Send push notification to a single device
    
    Args:
        push_token: FCM device token
        title: Notification title
        body: Notification body text
        data: Optional dict of additional data (must be strings)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not firebase_admin._apps:
        print("Firebase not initialized - cannot send notification")
        return False
    
    if not push_token:
        print("No push token provided")
        return False
    
    try:
        # Ensure data values are strings
        if data:
            data = {k: str(v) for k, v in data.items()}
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=push_token
        )
        
        response = messaging.send(message)
        print(f'Successfully sent notification: {response}')
        return True
        
    except messaging.UnregisteredError:
        print(f'Push token is invalid/unregistered: {push_token[:20]}...')
        return False
    except messaging.InvalidArgumentError as e:
        print(f'Invalid argument for push notification: {e}')
        return False
    except Exception as e:
        print(f'Error sending push notification: {e}')
        return False

def send_batch_notifications(tokens_and_messages):
    """
    Send multiple notifications efficiently
    
    Args:
        tokens_and_messages: List of tuples (token, title, body, data)
    
    Returns:
        tuple: (success_count, failure_count, failed_indices)
    """
    if not firebase_admin._apps:
        print("Firebase not initialized - cannot send notifications")
        return 0, len(tokens_and_messages), list(range(len(tokens_and_messages)))
    
    messages = []
    for token, title, body, data in tokens_and_messages:
        # Ensure data values are strings
        if data:
            data = {k: str(v) for k, v in data.items()}
        
        messages.append(messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token
        ))
    
    if not messages:
        return 0, 0, []
    
    try:
        response = messaging.send_all(messages)
        print(f'Successfully sent {response.success_count}/{len(messages)} notifications')
        
        # Collect indices of failed sends
        failed_indices = [i for i, resp in enumerate(response.responses) if not resp.success]
        
        return response.success_count, response.failure_count, failed_indices
        
    except Exception as e:
        print(f'Error sending batch notifications: {e}')
        return 0, len(messages), list(range(len(messages)))


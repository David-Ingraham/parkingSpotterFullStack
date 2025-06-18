from routes.five_nearest import bp as five_nearest_bp
from routes.watch_camera import bp as watch_camera_bp
from routes.direct_camera_search import bp as direct_camera_search_bp
from flask import Blueprint, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def register_routes(app):
    app.register_blueprint(five_nearest_bp)
    app.register_blueprint(watch_camera_bp)
    app.register_blueprint(direct_camera_search_bp)

# Apply rate limiting to our routes
@limiter.limit("1 per second")
@five_nearest_bp.before_request
@watch_camera_bp.before_request
@direct_camera_search_bp.before_request
def limit_request_rate():
    pass

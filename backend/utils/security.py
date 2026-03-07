from functools import wraps
from flask import request, jsonify
import os
import logging

logger = logging.getLogger(__name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import Config inside function to avoid potential circular imports
        # and ensure Config is fully loaded
        try:
            from config import Config
            expected_key = getattr(Config, 'ADMIN_API_KEY', None)
        except ImportError:
            expected_key = os.getenv('ADMIN_API_KEY')

        # If still not found, fallback to os.getenv directly just in case
        if not expected_key:
            expected_key = os.getenv('ADMIN_API_KEY')

        if not expected_key:
            logger.error("ADMIN_API_KEY not configured in environment")
            return jsonify({'error': 'Server configuration error: ADMIN_API_KEY not set'}), 500

        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')

        if not api_key or api_key != expected_key:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing API key'}), 401

        return f(*args, **kwargs)
    return decorated_function

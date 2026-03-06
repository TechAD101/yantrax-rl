from functools import wraps
from flask import request, jsonify
from config import Config

def require_api_key(f):
    """
    Decorator to require X-API-Key header for sensitive endpoints.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Retrieve the API key from headers
        api_key = request.headers.get('X-API-Key')

        # Check if key is present
        if not api_key:
            return jsonify({
                'error': 'unauthorized',
                'message': 'Authentication required. valid X-API-Key header missing.'
            }), 401

        # Validate the key
        if api_key != Config.YANTRAX_ADMIN_KEY:
             return jsonify({
                 'error': 'unauthorized',
                 'message': 'Invalid API Key'
             }), 401

        return f(*args, **kwargs)
    return decorated_function

from flask import Flask, jsonify
from datetime import datetime
import sys

app = Flask(__name__)

@app.route('/debug', methods=['GET'])
def debug_endpoint():
    """Simple debug endpoint that should always work"""
    return jsonify({
        'message': 'Debug endpoint working',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'flask_version': 'Running'
    }), 200
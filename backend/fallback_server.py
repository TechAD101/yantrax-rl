#!/usr/bin/env python3
"""
Fallback deployment script for when gunicorn fails
Uses Flask development server as backup
"""
import os
import sys
from main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting Flask fallback server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
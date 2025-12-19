#!/bin/bash
# Force fresh install
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Debug info
echo "🚀 STARTING DEPLOYMENT SCRIPT"
echo "📂 Current Directory: $(pwd)"
ls -la
echo "📦 Python Version: $(python --version)"

# Start App
cd backend
gunicorn application:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

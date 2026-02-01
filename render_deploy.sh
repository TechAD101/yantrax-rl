#!/usr/bin/env bash
# render_deploy.sh - Production Deploy Script for Yantra X
# Force redeploy: 2026-02-01T21:59:30Z
set -e

echo "🌊 Starting Yantra X Institutional Deployment..."

# 1. Environment Info
echo "🐍 Environment Statistics:"
python --version
pip --version

# 2. Install dependencies
echo "📦 Installing backend dependencies from slim-build manifest..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 3. Run the application
echo "🏢 Starting Institutional Gunicorn server..."
# Standardizing on Render's dynamic port
export PORT=${PORT:-10000}
cd backend
export PYTHONPATH=$PYTHONPATH:.
echo "🚀 Deployment Port: $PORT"
echo "✅ System Version: 5.21-MVP-Routes-Active"
gunicorn wsgi:app --bind 0.0.0.0:$PORT --log-level info --timeout 120 --workers 2

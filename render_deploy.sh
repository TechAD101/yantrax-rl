#!/usr/bin/env bash
# render_deploy.sh - Production Deploy Script for Yantra X
# Force redeploy: 2026-02-06T00:00:00Z
set -e

echo "🌊 Starting Yantra X Institutional Deployment..."

# 1. Environment Info
echo "🐍 Environment Statistics:"
python --version
pip --version

# 2. Verify gunicorn installation
echo "🔍 Checking Gunicorn installation..."
if ! python -c "import gunicorn; print('Gunicorn version:', gunicorn.__version__)"; then
    echo "❌ Gunicorn not found, installing..."
    pip install gunicorn==22.0.0
fi

# 3. Run the application
echo "🏢 Starting Institutional Gunicorn server..."
# Standardizing on Render's dynamic port
export PORT=${PORT:-10000}
# Add repository root to Python path so that `backend` package can be imported
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "🚀 Deployment Port: $PORT"
echo "✅ System Version: 5.23-STABLE"
exec python -m gunicorn backend.wsgi:app --bind 0.0.0.0:$PORT --log-level info --timeout 120 --workers 2

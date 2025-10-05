# wsgi.py - YantraX RL v4.1 Supernatural AI Firm WSGI Entry Point
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from the updated main.py with v4.1 supernatural recovery fixes
from main import app

if __name__ == "__main__":
    app.run()
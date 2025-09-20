# wsgi.py - YantraX RL Enhanced AI Firm WSGI Entry Point
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from enhanced main with AI firm architecture
from main_enhanced import app

if __name__ == "__main__":
    app.run()

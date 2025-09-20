# app.py - Simplified deployment entry point for YantraX AI Firm
# This ensures Render can easily find and deploy the enhanced version

from main_enhanced import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

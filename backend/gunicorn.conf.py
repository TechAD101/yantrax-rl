import os
import multiprocessing

# Gunicorn Configuration File (gunicorn.conf.py)
# This file is automatically loaded by Gunicorn/Render to configure the server.
# It replaces the need for complex command-line arguments.

# Binding
# Render sets the PORT environment variable.
port = os.getenv("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Worker Configuration
# We use 'gthread' (Threaded Workers) because 'gevent' is incompatible with some
# blocking libraries we use (like yfinance/pandas) in this specific setup.
# 'gthread' allows concurrency without the complexity of async monkey-patching.
worker_class = "gthread"

# Concurrency
# For a streaming app on limited RAM (512MB), we want:
# 1 Worker Process (to minimize RAM overhead)
# Many Threads (to handle multiple concurrent streaming connections)
workers = 1
threads = 8

# Timeout
# CRITICAL: We stream data via Server-Sent Events (SSE).
# Standard timeout (30s) will kill the connection. 
# We set timeout to 0 (unlimited) or a very high number to keep streams alive.
timeout = 0 
keepalive = 5

# Logging
accesslog = "-"  # Stdout
errorlog = "-"   # Stderr
loglevel = "info"

# Process Naming
proc_name = "yantrax-backend"

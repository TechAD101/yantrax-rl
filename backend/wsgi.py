import threading
from main import app, autonomous_ingestion_loop

# Render entry point

# Start autonomous ingestion thread safely using an app context or after worker initialization
# Using a before_request to spawn it only once when the server actually starts serving requests
_ingestion_started = False

@app.before_request
def start_ingestion_thread():
    global _ingestion_started
    if not _ingestion_started:
        _ingestion_started = True
        ingest_thread = threading.Thread(target=autonomous_ingestion_loop, daemon=True)
        ingest_thread.start()

if __name__ == '__main__':
    app.run()

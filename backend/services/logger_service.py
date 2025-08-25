import logging
import os

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logger
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "yantrax.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("YantraX")

def log_message(message: str, level: str = "info"):
    """Log a message to file and console."""
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.debug(message)

def get_logs(n: int = 50):
    """Return last n log lines for dashboard/monitoring."""
    log_file = os.path.join(LOG_DIR, "yantrax.log")
    if not os.path.exists(log_file):
        return ["No logs yet."]
    with open(log_file, "r") as f:
        lines = f.readlines()
        return lines[-n:]

#!/usr/bin/env python3
"""
Yantra X Recovery Cron — safe engineering-goal checkpoint recovery.

Purpose:
- Run every 2-5 hours (configurable via YANTRAX_RECOVERY_INTERVAL env var)
- Acquire a lock file to prevent concurrent runs on VPS restarts/crashes
- Check if the mission checkpoint has been updated within the interval
- If the checkpoint is stale, log a recovery notice and report status
- NEVER trigger trading logic — this is an engineering checkpoint recovery job only

Usage:
    python recovery_cron.py [--dry-run] [--interval <seconds>]

Environment:
    YANTRAX_RECOVERY_INTERVAL  default: 7200 (2 hours)
    YANTRAX_RECOVERY_LOCK_DIR  default: /tmp/yantrax-recovery
    YANTRAX_BACKEND_URL        default: https://yantrax-backend.onrender.com
    YANTRAX_MISSION_DIR        default: /home/ubuntu/yantrax-mission
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Configuration
LOCK_TIMEOUT_HOURS = 3  # Maximum lock age before allowing recovery
DEFAULT_INTERVAL = 7200  # 2 hours
CHECKPOINT_FILENAME = "YANTRAX_CHECKPOINT.md"


def get_lock_path() -> Path:
    """Get the lock file path."""
    lock_dir = Path(os.environ.get("YANTRAX_RECOVERY_LOCK_DIR", "/tmp/yantrax-recovery"))
    lock_dir.mkdir(parents=True, exist_ok=True)
    return lock_dir / "recovery.lock"


def acquire_lock() -> Optional[Path]:
    """Attempt to acquire exclusive lock. Returns lock path or None."""
    lock_path = get_lock_path()
    now = datetime.now(timezone.utc)

    # Check if stale lock exists
    if lock_path.exists():
        try:
            lock_data = json.loads(lock_path.read_text())
            lock_time = datetime.fromisoformat(lock_data["acquired_at"])
            age_hours = (now - lock_time).total_seconds() / 3600

            if age_hours > LOCK_TIMEOUT_HOURS:
                print(f"[RECOVERY] Stale lock detected ({age_hours:.1f}h old), removing")
                lock_path.unlink()
            else:
                print(f"[RECOVERY] Lock held by another process ({age_hours:.1f}h ago)")
                return None
        except (json.JSONDecodeError, KeyError):
            print("[RECOVERY] Corrupt lock file, removing")
            lock_path.unlink()

    # Acquire new lock
    lock_data = {
        "acquired_at": now.isoformat(),
        "hostname": os.uname().nodename,
        "pid": os.getpid(),
        "version": "2.0.0",
    }
    lock_path.write_text(json.dumps(lock_data, indent=2))
    print(f"[RECOVERY] Lock acquired: {lock_path}")
    return lock_path


def release_lock(lock_path: Path):
    """Release the recovery lock."""
    if lock_path.exists():
        lock_path.unlink()
        print("[RECOVERY] Lock released")


def check_backend_health(url: str) -> dict:
    """Check the health endpoint for service status."""
    try:
        req = urllib.request.Request(f"{url}/health", headers={"User-Agent": "YantraX-Recovery/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"[RECOVERY] Health check failed: {e}")
        return {}


def check_checkpoint_staleness(mission_dir: Path) -> dict:
    """Check if the mission checkpoint file exists and is recent."""
    checkpoint_path = mission_dir / CHECKPOINT_FILENAME
    if not checkpoint_path.exists():
        return {"exists": False, "stale": True, "reason": "checkpoint file missing"}

    mtime = datetime.fromtimestamp(checkpoint_path.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    return {
        "exists": True,
        "stale": age_hours > 24,
        "age_hours": age_hours,
        "path": str(checkpoint_path),
    }


def log_recovery_event(action: str, details: dict):
    """Log recovery event to journal file."""
    journal_dir = Path(os.environ.get("YANTRAX_MISSION_DIR", "/home/ubuntu/yantrax-mission"))
    journal_dir.mkdir(parents=True, exist_ok=True)
    journal_path = journal_dir / "recovery_journal.jsonl"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details,
    }

    with open(journal_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[RECOVERY] {action}: {json.dumps(details)}")


def main():
    parser = argparse.ArgumentParser(description="Yantra X Recovery Cron")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--interval", type=int, help="Override recovery interval (seconds)")
    args = parser.parse_args()

    # Configuration
    interval = args.interval or int(os.environ.get("YANTRAX_RECOVERY_INTERVAL", DEFAULT_INTERVAL))
    backend_url = os.environ.get("YANTRAX_BACKEND_URL", "https://yantrax-backend.onrender.com")
    mission_dir = Path(os.environ.get("YANTRAX_MISSION_DIR", "/home/ubuntu/yantrax-mission"))

    print(f"[RECOVERY] Starting recovery check (interval={interval}s, url={backend_url})")

    # Acquire lock
    lock_path = acquire_lock()
    if not lock_path:
        print("[RECOVERY] Skipping: lock held")
        return 0

    try:
        # Check backend health (read-only, no trading)
        health = check_backend_health(backend_url)
        backend_status = health.get("status", "unknown")
        print(f"[RECOVERY] Backend status: {backend_status}")

        # Check checkpoint staleness
        checkpoint = check_checkpoint_staleness(mission_dir)

        if checkpoint["stale"]:
            reason = checkpoint.get("reason", "stale")
            age = checkpoint.get("age_hours", "unknown")
            print(f"[RECOVERY] Checkpoint is stale (age={age}h, reason={reason})")
            if not args.dry_run:
                log_recovery_event("checkpoint_stale", {
                    "reason": reason,
                    "age_hours": age,
                    "backend_status": backend_status,
                })
            else:
                print("[RECOVERY] DRY RUN: Would log checkpoint_stale event")
        else:
            print(f"[RECOVERY] Checkpoint is current ({checkpoint.get('age_hours', 0):.1f}h ago)")
            log_recovery_event("healthy", {
                "age_hours": checkpoint.get("age_hours", 0),
                "backend_status": backend_status,
            })

        return 0

    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    sys.exit(main())
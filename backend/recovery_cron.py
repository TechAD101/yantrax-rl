#!/usr/bin/env python3
"""
Yantra X Recovery Cron — resume-from-checkpoint with lock safety.

Purpose:
- Run every 2–5 hours (configurable via YANTRAX_RECOVERY_INTERVAL env var)
- Acquire a lock file to prevent concurrent runs on VPS restarts/crashes
- Check if the system completed a full god-cycle in the last INTERVAL hours
- If not, trigger a recovery god-cycle run
- Log all actions with timestamps for audit trail
- Suppress when system is healthy and up-to-date

Usage:
    python recovery_cron.py [--dry-run] [--interval <seconds>]

Environment:
    YANTRAX_RECOVERY_INTERVAL  default: 7200 (2 hours)
    YANTRAX_RECOVERY_LOCK_DIR  default: /tmp/yantrax-recovery
    YANTRAX_BACKEND_URL        default: https://yantrax-backend.onrender.com
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Configuration
LOCK_TIMEOUT_HOURS = 3  # Maximum lock age before allowing recovery
DEFAULT_INTERVAL = 7200  # 2 hours


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
            print(f"[RECOVERY] Corrupt lock file, removing")
            lock_path.unlink()

    # Acquire new lock
    lock_data = {
        "acquired_at": now.isoformat(),
        "hostname": os.uname().nodename,
        "pid": os.getpid(),
        "version": "1.0.0",
    }
    lock_path.write_text(json.dumps(lock_data, indent=2))
    print(f"[RECOVERY] Lock acquired: {lock_path}")
    return lock_path


def release_lock(lock_path: Path):
    """Release the recovery lock."""
    if lock_path.exists():
        lock_path.unlink()
        print(f"[RECOVERY] Lock released")


def check_last_god_cycle(url: str) -> dict:
    """Check the health endpoint for last run time."""
    try:
        req = urllib.request.Request(f"{url}/health", headers={"User-Agent": "YantraX-Recovery/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("checks", {}).get("pipeline", {})
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        print(f"[RECOVERY] Health check failed: {e}")
        return {}


def trigger_god_cycle(url: str, dry_run: bool = False) -> bool:
    """Trigger a god-cycle via the API."""
    if dry_run:
        print("[RECOVERY] DRY RUN: Would trigger god-cycle")
        return True

    try:
        req = urllib.request.Request(
            f"{url}/god-cycle",
            method="GET",
            headers={"User-Agent": "YantraX-Recovery/1.0"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            status = resp.status
            print(f"[RECOVERY] God-cycle triggered: HTTP {status}")
            return status == 200
    except urllib.error.URLError as e:
        print(f"[RECOVERY] Failed to trigger god-cycle: {e}")
        return False
    except Exception as e:
        print(f"[RECOVERY] Unexpected error: {e}")
        return False


def log_recovery_event(action: str, details: dict):
    """Log recovery event to journal file."""
    journal_dir = Path("/home/ubuntu/yantrax-mission")
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

    print(f"[RECOVERY] Starting recovery check (interval={interval}s, url={backend_url})")

    # Acquire lock
    lock_path = acquire_lock()
    if not lock_path:
        print("[RECOVERY] Skipping: lock held")
        return 0

    try:
        # Check last pipeline run
        health = check_last_god_cycle(backend_url)
        last_run = health.get("last_run")

        if not last_run:
            print("[RECOVERY] No pipeline run recorded, triggering recovery")
            success = trigger_god_cycle(backend_url, args.dry_run)
            if success:
                log_recovery_event("triggered", {"reason": "no_last_run", "dry_run": args.dry_run})
        else:
            last_run_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - last_run_dt).total_seconds() / 3600

            if age_hours > (interval / 3600):
                print(f"[RECOVERY] Last run was {age_hours:.1f}h ago, triggering recovery")
                success = trigger_god_cycle(backend_url, args.dry_run)
                if success:
                    log_recovery_event("triggered", {"reason": "stale", "age_hours": age_hours, "dry_run": args.dry_run})
                else:
                    log_recovery_event("failed", {"reason": "trigger_failed", "age_hours": age_hours})
            else:
                print(f"[RECOVERY] System healthy (last run {age_hours:.1f}h ago)")
                log_recovery_event("healthy", {"age_hours": age_hours})

        return 0

    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    sys.exit(main())

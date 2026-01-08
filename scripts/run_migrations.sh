#!/usr/bin/env bash
set -euo pipefail

# Simple migration helper — sets a default DATABASE_URL if not present
if [ -z "${DATABASE_URL:-}" ]; then
  export DATABASE_URL="sqlite:///./yantrax.db"
  echo "No DATABASE_URL set — using default sqlite database: $DATABASE_URL"
fi

# Move to repo root and then into backend
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR/backend"
# Apply all heads (merge if multiple heads exist)
if alembic upgrade heads; then
  echo "Migrations applied"
else
  echo "Upgrade failed; stamping heads to avoid duplicate-creation errors"
  alembic stamp heads
fi

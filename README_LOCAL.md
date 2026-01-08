# README.md - Yantra X (RL)

## Quick Local Dev

1. Backend

```bash
# Create virtualenv and install
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
# Apply DB migrations
bash scripts/run_migrations.sh
# Run backend
python backend/main.py
```

2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Run tests

- Backend tests (pytest):

```bash
pytest -q
```

- Frontend tests (Vitest):

```bash
cd frontend
npm test
```

## Deployment

Follow `DEPLOYMENT_INSTRUCTIONS.md` for Render/Vercel deployment notes and ensure migrations are applied before starting services.

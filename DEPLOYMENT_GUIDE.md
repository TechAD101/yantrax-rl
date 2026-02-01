# Deployment Guide

## Overview
This guide covers deploying YantraX to production on Render, Vercel (frontend), and connecting the full stack.

---

## Prerequisites

- GitHub repository linked to Render/Vercel
- Environment variables configured
- Database setup (PostgreSQL recommended for production)
- API keys for market data providers (optional, graceful fallbacks exist)

---

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/yantrax_prod

# API Keys (optional)
FMP_API_KEY=your_fmp_key_here
SECRET_KEY=your_secret_key_generate_with_openssl_rand_hex_32

# Server
PORT=5000
FLASK_ENV=production

# Optional
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```bash
VITE_API_URL=https://yantrax-backend.onrender.com
```

---

## Backend Deployment (Render)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### Step 2: Create Render Service
1. Go to [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select branch: `main`
5. Configure:
   - **Name**: yantrax-backend
   - **Environment**: Python 3.12
   - **Build Command**: `pip install -r backend/requirements.txt && cd backend && python -m alembic upgrade head`
   - **Start Command**: `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT main:app`
   - **Plan**: Standard ($12/month)

### Step 3: Set Environment Variables
In Render dashboard:
1. Go to Service Settings
2. Add Environment Variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `FMP_API_KEY`: Your FMP API key (if available)
   - `SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `FLASK_ENV`: production

### Step 4: Deploy
Click "Deploy" and wait for build to complete (5-10 minutes).

### Step 5: Verify
```bash
curl https://yantrax-backend.onrender.com/health
```

Expected response: `{"status": "healthy", ...}`

---

## Frontend Deployment (Vercel)

### Step 1: Connect to Vercel
1. Go to [Vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select your GitHub repository
4. Choose `frontend` directory as root
5. Click Import

### Step 2: Configure Environment
In Vercel Project Settings → Environment Variables:
```
VITE_API_URL=https://yantrax-backend.onrender.com
```

### Step 3: Deploy
Vercel auto-deploys on push to `main` branch.

Verify:
```bash
curl https://yantrax-frontend.vercel.app
```

---

## Database Migration (Production)

### PostgreSQL Setup
```bash
# Create database
createdb yantrax_prod
```

### Apply Migrations
```bash
# Via Render CLI
render exec --service yantrax-backend -- alembic upgrade head

# Or via SSH
ssh render-instance
cd /var/app/backend
alembic upgrade head
```

### Verify Migrations
```bash
render exec --service yantrax-backend -- \
  python -c "from models import *; print('Models loaded')"
```

---

## CI/CD Pipeline

### GitHub Actions (Already Configured)

The `.github/workflows/ci.yml` automatically:
1. Runs backend tests (pytest)
2. Applies Alembic migrations
3. Runs frontend tests (Vitest)
4. Builds frontend (Vite)

On successful CI run:
- Backend deploys to Render (via webhook)
- Frontend deploys to Vercel (auto-connected)

---

## Monitoring & Logs

### Backend Logs
```bash
render logs --service yantrax-backend --tail 100
```

### Frontend Logs
```bash
# Vercel
vercel logs
```

### Database Health
```bash
render exec --service yantrax-backend -- \
  python -c "from db import get_session; s = get_session(); print('DB OK')"
```

---

## Health Checks

### Backend Health
**Endpoint**: `GET /health`

```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "market_data": "operational"
  }
}
```

### Status Page
Monitor at: `https://status.yantrax.app` (optional, recommend Status.io or Uptime Robot)

---

## Scaling

### Backend Scaling
In Render dashboard:
- Increase **Max CPU %**: 100 → 200
- Increase **Max Memory**: 512MB → 2GB
- Enable **Auto-scaling** with min/max instances

### Database Scaling
For PostgreSQL:
- Upgrade to larger plan as needed
- Enable automated backups
- Set up read replicas for high load

### CDN for Frontend
Vercel automatically provides:
- Global edge network
- Automatic caching
- Image optimization

---

## Backup & Recovery

### Database Backups
```bash
# Render auto-backups (daily)
# Manual backup:
pg_dump postgresql://user:pw@host/db > backup.sql
```

### Restore from Backup
```bash
psql postgresql://user:pw@host/db < backup.sql
```

### Code Backups
GitHub handles version control and rollbacks via branches.

---

## Security Considerations

1. **Enable HTTPS**: Both Render and Vercel auto-enable
2. **Secret Management**: Use Render/Vercel environment variables, not .env
3. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Restrict IP access
4. **API Keys**: Store securely, rotate regularly
5. **CORS**: Configure in `backend/main.py`:
   ```python
   CORS(app, origins=['https://yantrax-frontend.vercel.app'])
   ```

---

## Troubleshooting

### 502 Bad Gateway
```bash
# Check backend logs
render logs --service yantrax-backend
# Common: Missing env vars, DB connection issue
```

### Database Connection Failed
```bash
# Verify connection string
render exec --service yantrax-backend -- \
  python -c "from db import init_db; init_db(); print('Connected')"
```

### Frontend Not Loading API Data
```bash
# Check VITE_API_URL in Vercel environment
# Verify CORS settings in backend
```

### Migrations Failing
```bash
# Re-apply with skip on existing:
alembic upgrade heads

# If conflicted, check version table:
alembic current
```

---

## Rollback Procedure

### Backend Rollback
```bash
# Render: Use "Deploy Hooks" → select previous deployment
# Manual: git revert <commit-hash> && git push
```

### Database Rollback
```bash
# Get current revision
alembic current

# Downgrade one revision
alembic downgrade -1

# Or downgrade to specific revision
alembic downgrade <revision-hash>
```

### Frontend Rollback
```bash
# Vercel: Dashboard → Deployments → Redeploy
```

---

## Performance Optimization

### Backend
- Enable gzip compression (gunicorn)
- Cache strategy metadata
- Use connection pooling (SQLAlchemy)
- Implement rate limiting (future)

### Frontend
- Tree-shaking in Vite build
- Code splitting per route
- Lazy-load components
- Compress assets (Vercel auto)

### Database
- Add indexes on frequently queried fields
- Partition large tables (future)
- Archive old backtest results

---

## Maintenance Schedule

- **Daily**: Monitor logs and health checks
- **Weekly**: Review error rates, user feedback
- **Monthly**: Performance analysis, dependency updates
- **Quarterly**: Security audit, capacity planning

---

## Support & Escalation

- **Render Support**: https://support.render.com
- **Vercel Support**: https://vercel.com/support
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Post-Deployment Checklist

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and loads
- [ ] API endpoints responding
- [ ] Database migrations applied
- [ ] Environment variables set correctly
- [ ] CORS configured
- [ ] Health checks passing
- [ ] Logs being collected
- [ ] Monitoring configured
- [ ] Backups enabled

---

**Last Updated**: February 1, 2026
**Version**: 1.0

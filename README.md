# AI-WAF — AI-Powered Web Application Firewall

[![CI](https://github.com/YOUR_USERNAME/ai-waf/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/ai-waf/actions)

A full-stack security dashboard that inspects every HTTP request with a fine-tuned DistilBERT classifier (with keyword fallback), blocks high-confidence attacks (SQLi, XSS, path traversal, command injection), logs everything to a database, and streams live traffic to a React dashboard over WebSockets.

**Live demo:** [Frontend on Vercel](https://your-app.vercel.app) · [API on Render](https://your-api.onrender.com)

---

## Architecture

```
Browser → WAFMiddleware (FastAPI)
             ├─ AttackDetector.predict(path+query)
             │      ├─ torch installed + model trained? → DistilBERT (label, conf, "ml")
             │      └─ fallback                         → keyword scan (label, conf, "keyword")
             ├─ SQLite / PostgreSQL log entry
             ├─ WebSocket broadcast → React dashboard
             └─ ATTACK? → 403 JSON  /  SAFE? → call_next handler
```

```
ai-waf/
├── backend/              FastAPI app
│   ├── app/
│   │   ├── main.py            App entrypoint, CORS, routes
│   │   ├── config.py          Env-driven settings (pydantic-settings)
│   │   ├── database.py        SQLAlchemy engine — SQLite / PostgreSQL auto-detect
│   │   ├── models.py          ORM: request_logs table
│   │   ├── schemas.py         Pydantic I/O models
│   │   ├── security.py        JWT auth helpers
│   │   ├── websocket_manager.py  Connection pool for live feed
│   │   ├── middleware/
│   │   │   └── waf_middleware.py  ← intercepts every request
│   │   ├── ml/
│   │   │   ├── detector.py    Loads model or falls back to keywords
│   │   │   └── train.py       Fine-tunes DistilBERT on ml_data/dataset.json
│   │   └── api/
│   │       ├── routes_auth.py     POST /api/auth/login
│   │       ├── routes_logs.py     GET /api/logs, GET /api/logs/stats
│   │       ├── routes_simulate.py POST /api/simulate
│   │       └── routes_ws.py       WS /ws/live
│   ├── requirements.txt          Full deps (includes torch for ML)
│   ├── requirements-deploy.txt   Lightweight deps (no torch — for Render free tier)
│   └── Dockerfile
├── frontend/             React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx        Root — auth, WS connection, layout
│   │   ├── api.js         All fetch/WS calls
│   │   ├── styles.css     Dark SOC-style theme
│   │   └── components/
│   │       ├── Header.jsx         Top bar + connection status
│   │       ├── StatCards.jsx      5 KPI cards (total/safe/attack/blocked/confidence)
│   │       ├── LiveFeed.jsx       Scrolling terminal of live events
│   │       ├── Charts.jsx         Pie + live bar chart (recharts)
│   │       ├── SimulatePanel.jsx  Payload scanner
│   │       ├── LogsTable.jsx      Filterable request log (IP, Method, Label…)
│   │       └── Login.jsx          JWT login form
│   ├── vercel.json        Vercel SPA config
│   └── Dockerfile
├── ml_data/dataset.json  Training data (406 SAFE/ATTACK samples)
├── scripts/
│   └── attack_simulator.py  Generates demo traffic
├── render.yaml            Render.com deploy config
├── docker-compose.yml     Local full-stack with Postgres
└── .github/workflows/ci.yml  CI — import check + frontend build
```

---

## 🚀 Quick Start — Local (No Docker)

### Backend

```bash
cd backend

# Create virtual env
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install deps (full, including torch for ML)
pip install -r requirements.txt

# Configure
cp ../. env.example .env
# Edit .env — at minimum set SECRET_KEY and ADMIN_PASSWORD

# Run
uvicorn app.main:app --reload
# → API: http://localhost:8000
# → Docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install

# Create a .env.local with the API URL (defaults to localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
# → Dashboard: http://localhost:5173
```

**Login** with `ADMIN_USERNAME` / `ADMIN_PASSWORD` from `backend/.env` (default: `admin` / `change-me`).

---

## 🐳 Quick Start — Docker Compose (Recommended)

```bash
cd ai-waf
cp .env.example backend/.env   # edit SECRET_KEY and ADMIN_PASSWORD
docker compose up --build
```

| Service   | URL                          |
|-----------|------------------------------|
| Dashboard | http://localhost:5173        |
| API       | http://localhost:8000        |
| API Docs  | http://localhost:8000/docs   |
| Postgres  | localhost:5432               |

### Train the ML model (optional)

```bash
docker compose exec backend python -m app.ml.train
docker compose restart backend
```

---

## 📡 Generate Demo Traffic

```bash
pip install requests
python scripts/attack_simulator.py --url http://localhost:8000 --count 40
```

Watch the live dashboard feed light up with SAFE / ATTACK events in real time.

---

## ☁️ Deploy to Vercel + Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ai-waf.git
git push -u origin main
```

### 2. Deploy Backend → Render

1. Go to [render.com](https://render.com) → **New** → **Blueprint**
2. Connect your GitHub repo
3. Render will read `render.yaml` and create:
   - `waf-db` — free PostgreSQL
   - `waf-backend` — Python web service
4. In the Render dashboard, set these **Environment Variables** manually:
   | Variable | Value |
   |---|---|
   | `ADMIN_PASSWORD` | your strong password |
   | `ALLOWED_ORIGINS` | `https://your-app.vercel.app` *(set after Vercel deploy)* |
5. Note your backend URL: `https://waf-backend.onrender.com`

### 3. Deploy Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project** → Import from GitHub
2. Set **Root Directory** to `frontend`
3. Add **Environment Variables**:
   | Variable | Value |
   |---|---|
   | `VITE_API_URL` | `https://waf-backend.onrender.com` |
4. Deploy — Vercel auto-detects Vite.

### 4. Update CORS on Render

Once you have your Vercel URL (e.g. `https://ai-waf.vercel.app`), go back to Render and set:
```
ALLOWED_ORIGINS=https://ai-waf.vercel.app,http://localhost:5173
```

---

## 🔒 API Reference

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/login` | ❌ | Get JWT token |
| `GET` | `/api/logs` | ✅ | List request logs (filter by label/search) |
| `GET` | `/api/logs/stats` | ✅ | Aggregate stats |
| `POST` | `/api/simulate` | ✅ | Scan a payload without logging |
| `WS` | `/ws/live?token=` | JWT | Live traffic stream |
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/docs` | ❌ | Swagger UI |

---

## ⚙️ Environment Variables

All backend config is via environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | JWT signing key — use a long random string |
| `ADMIN_USERNAME` | `admin` | Dashboard login username |
| `ADMIN_PASSWORD` | `change-me` | Dashboard login password |
| `DATABASE_URL` | `sqlite:///./ai_waf.db` | SQLite (local) or `postgresql+psycopg2://...` |
| `MODEL_DIR` | `./model/final` | Path to trained DistilBERT model |
| `ATTACK_CONFIDENCE_THRESHOLD` | `0.75` | ML confidence threshold to trigger a block |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated CORS origins |

---

## 🧠 ML Model

The WAF has two detection modes:

| Mode | When | How |
|---|---|---|
| **ML** (`type=ml`) | torch + model trained | DistilBERT classifies the path+query |
| **Keyword** (`type=keyword`) | ML uncertain or no model | Checks against ~24 known attack patterns |

To train or retrain the ML model:
```bash
cd backend
python -m app.ml.train   # reads ml_data/dataset.json
# → saves model to backend/model/final/
```

The keyword fallback is used on Render free tier (no torch installed) but is production-capable against known attack signatures.

---

## 🔐 Security Notes for Production

- Change `SECRET_KEY` to a cryptographically random 64-char string
- Change `ADMIN_PASSWORD` to a strong password
- Set `DEBUG=false` and `ENV=production`  
- Add your frontend URL to `ALLOWED_ORIGINS`
- Put the backend behind a reverse proxy with TLS
- Consider adding rate limiting (`slowapi`) in front of the WAF
- Swap SQLite for PostgreSQL for any real traffic volume

---

## 📈 Extending

- **Better model**: Add more samples to `ml_data/dataset.json` and retrain
- **Multiple users**: Add a `users` table with bcrypt-hashed passwords
- **Alembic migrations**: Replace `Base.metadata.create_all` for versioned schema changes
- **Rate limiting**: Add `slowapi` middleware
- **Alerts**: Hook WebSocket events to Slack/email on high-confidence attacks

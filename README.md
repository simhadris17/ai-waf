# AI-WAF

AI-WAF is a full-stack web application firewall and analytics dashboard built with FastAPI and React. It inspects incoming HTTP requests, detects suspicious payloads and malformed URLs, blocks high-confidence attacks before they reach app logic, and surfaces activity through a live monitoring dashboard.

The project combines deterministic attack checks with optional ML-based inference, giving a practical security layer for demo, testing, and production-like deployment environments.

---

## Features

- Middleware-level request inspection for inbound traffic
- Detection of SQL injection, XSS, path traversal, command injection, malformed schemes, and typo-squatting domains
- Confidence-based blocking and logging
- JWT-based admin authentication
- Live dashboard updates over WebSockets
- Request history and analytics storage
- Vercel + Render deployment configuration

---

## Architecture

```text
Browser → Frontend (React + Vite)
            ↓
       FastAPI backend
            ↓
      WAF middleware
      ├─ URL normalization + heuristic checks
      ├─ payload pattern detection
      ├─ optional ML model classification
      ├─ logging to SQLite/PostgreSQL
      ├─ WebSocket broadcast to dashboard
      └─ block malicious requests with 403 responses
```

---

## Repository Structure

```text
ai-waf/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_auth.py
│   │   │   ├── routes_logs.py
│   │   │   ├── routes_simulate.py
│   │   │   └── routes_ws.py
│   │   ├── middleware/
│   │   │   └── waf_middleware.py
│   │   ├── ml/
│   │   │   ├── detector.py
│   │   │   └── train.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   └── websocket_manager.py
│   ├── requirements.txt
│   ├── requirements-deploy.txt
│   ├── .python-version
│   └── model/
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vercel.json
│   └── vite.config.js
├── ml_data/
│   └── dataset.json
├── render.yaml
├── vercel.json
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- PostgreSQL optional for production deployment
- Render and Vercel accounts for cloud deployment

---

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

Create environment settings:

```bash
copy ..\.env.example .env
```

Update the values in `backend/.env` or your environment, especially:
- `SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `DATABASE_URL`
- `ALLOWED_ORIGINS`

Run the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at:
- http://localhost:8000
- http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard is available at:
- http://localhost:5173

Default admin credentials:
- Username: `admin`
- Password: `change-me`

---

## Deployment

### Render

The repo includes `render.yaml` for a Render Blueprint deployment that provisions:
- a PostgreSQL database
- a backend web service
- health checks and environment configuration

### Vercel

Use the `frontend` directory as the Vercel project root and set:
- `VITE_API_URL` to your deployed backend URL

---

## API Overview

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate dashboard admin |
| `GET` | `/api/logs` | Fetch recent requests |
| `GET` | `/api/logs/stats` | Fetch aggregated WAF metrics |
| `POST` | `/api/simulate` | Test a payload manually |
| `GET` | `/health` | Health check |
| `WS` | `/ws/live?token=` | Live traffic stream |

---

## Model and Detection Strategy

AI-WAF uses a layered approach:

1. Deterministic checks for malicious patterns and URL anomalies
2. Detection of malformed protocols and typo-squatting domains
3. Optional ML classification using a trained model when available
4. Confidence-based decision-making before a request is treated as safe or harmful

This gives better resilience against common attack payloads without relying solely on ML inference.

---

## Training the Model

To train or refresh the bundled ML model:

```bash
cd backend
python -m app.ml.train
```

This reads sample data from `ml_data/dataset.json` and writes the resulting model to the configured model directory.

---

## Security Notes

- Change `SECRET_KEY` to a strong random value in production
- Replace the default admin password before exposing the dashboard
- Restrict `ALLOWED_ORIGINS` to trusted frontend domains
- Ensure HTTPS is enabled in production
- Use a managed PostgreSQL service for real workloads
- Consider adding rate limiting and external threat intelligence feeds for broader coverage

---

## License

This project is intended for learning, testing, and security research scenarios. Review and harden before using it in production environments exposed to untrusted traffic.

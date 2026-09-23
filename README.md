# 🛡️ AI-WAF — AI-Powered Web Application Firewall

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![Machine Learning](https://img.shields.io/badge/ML-DistilBERT-green)
![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-blue)
![Deployment](https://img.shields.io/badge/Deployment-Render%20%7C%20Vercel-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

AI-WAF is a full-stack **Web Application Firewall (WAF)** and security monitoring dashboard built with **FastAPI, React, machine learning, and deterministic threat detection rules**.

The application inspects incoming HTTP requests, identifies malicious payloads and suspicious URLs, blocks high-confidence attacks, stores request history, and displays security events through a real-time dashboard.

> AI-WAF is intended for learning, testing, security research, and production-like demonstrations. It should be reviewed and hardened before being exposed to untrusted internet traffic.

---

## 📌 Project Overview

Modern web applications receive requests containing both legitimate user input and malicious payloads. A WAF helps identify suspicious traffic before it reaches application logic.

AI-WAF uses a layered detection pipeline:

1. Normalize and decode incoming request paths and query strings.
2. Detect known attack signatures with deterministic rules.
3. Identify malformed schemes and common typo-squatting domains.
4. Use optional ML inference when a trained model is available.
5. Log the request and broadcast the event to the dashboard.
6. Block high-confidence attacks with an HTTP `403` response.

---

## 🎯 Project Objectives

- Build a practical Web Application Firewall.
- Detect common web attacks and malicious URL patterns.
- Combine machine learning with reliable security rules.
- Provide a real-time security operations dashboard.
- Store request logs and aggregate security statistics.
- Support local development and cloud deployment.
- Demonstrate secure API authentication and WebSocket monitoring.

---

## ✨ Features

✅ SQL injection detection
✅ Cross-site scripting (XSS) detection
✅ Path traversal detection
✅ Command injection detection
✅ Server-side template injection detection
✅ Malformed URL scheme detection
✅ Brand typo-squatting detection
✅ URL and payload normalization
✅ Optional DistilBERT ML classification
✅ JWT-based admin authentication
✅ Request history and statistics
✅ Real-time WebSocket traffic feed
✅ Manual payload simulation scanner
✅ PostgreSQL and SQLite support
✅ Render Blueprint deployment configuration
✅ Vercel frontend deployment configuration
✅ Automatic stale-token recovery in the frontend

---

## 🛠️ Technology Stack

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic Settings
- PostgreSQL / SQLite
- JWT authentication
- WebSockets

### Frontend

- React
- Vite
- JavaScript
- Recharts
- Responsive security dashboard UI

### Machine Learning and Detection

- DistilBERT
- PyTorch and Transformers
- Rule-based threat detection
- URL normalization
- Pattern matching and confidence scoring

### Deployment

- Render
- Vercel
- Docker Compose
- GitHub

---

## 🧠 Detection Coverage

### SQL Injection

Examples detected by the WAF:

```text
' OR '1'='1
UNION SELECT username, password FROM users
DROP TABLE users
```

### Cross-Site Scripting

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
javascript:alert(document.cookie)
```

### Path Traversal

```text
../../etc/passwd
..%2F..%2Fetc%2Fpasswd
```

### Command Injection

```text
; whoami
| curl https://example.com
&& rm -rf /
```

### Suspicious URLs

```text
https://githu2b.com
https://rp3achallenge.com
ht4tps://www.google.com
```

Legitimate URLs such as the following are treated as safe when no malicious payload is present:

```text
https://www.google.com
https://github.com
https://rpachallenge.com
```

Detection accuracy depends on the quality of the labeled dataset and the availability of external threat-intelligence feeds. No local classifier can guarantee correct classification for every arbitrary internet URL.

---

## 📂 Project Structure

```text
ai-waf/
│
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
│   └── .python-version
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── styles.css
│   ├── package.json
│   ├── vercel.json
│   └── vite.config.js
│
├── ml_data/
│   └── dataset.json
│
├── scripts/
│   └── attack_simulator.py
│
├── docker-compose.yml
├── render.yaml
├── vercel.json
├── .env.example
├── LICENSE
└── README.md
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/simhadris17/ai-waf.git
cd ai-waf
```

### 2. Create a Python Virtual Environment

```bash
cd backend
python -m venv .venv
```

### 3. Activate the Environment

#### Windows

```powershell
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### 4. Install Backend Dependencies

For local development with the full ML stack:

```bash
pip install -r requirements.txt
```

For a lightweight deployment installation:

```bash
pip install -r requirements-deploy.txt
```

### 5. Configure Environment Variables

Copy the example environment file:

```powershell
# Windows PowerShell
Copy-Item .env.example backend\.env
```

Configure at least:

```env
SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-strong-password
DATABASE_URL=sqlite:///./ai_waf.db
ALLOWED_ORIGINS=http://localhost:5173
```

### 6. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

```text
API:       http://localhost:8000
Swagger:   http://localhost:8000/docs
ReDoc:     http://localhost:8000/redoc
Health:    http://localhost:8000/health
```

### 7. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Dashboard URL:

```text
http://localhost:5173
```

Use the `ADMIN_USERNAME` and `ADMIN_PASSWORD` values configured for the backend.

---

## 🐳 Run with Docker Compose

```bash
docker compose up --build
```

Services:

| Service | URL |
|---|---|
| Dashboard | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

Stop the services:

```bash
docker compose down
```

---

## 🧪 Test the WAF

### Manual Scanner

Log in to the dashboard and use the simulation panel to test examples such as:

```text
https://www.google.com
https://githu2b.com
<script>alert(1)</script>
' OR '1'='1
../../etc/passwd
```

### Generate Demo Traffic

```bash
pip install requests
python scripts/attack_simulator.py --url http://localhost:8000 --count 40
```

### Run Tests

```bash
pytest
```

---

## 🔄 Application Workflow

```text
Incoming HTTP Request
          ↓
Request Path and Query Extraction
          ↓
URL and Payload Normalization
          ↓
Deterministic Threat Rules
          ↓
Optional ML Inference
          ↓
SAFE or ATTACK Decision
       ↙           ↘
   Continue       Block with 403
       ↓
Persist Log + Broadcast Live Event
```

---

## 🔌 API Reference

| Method | Endpoint | Authentication | Description |
|---|---|---|---|
| `POST` | `/api/auth/login` | No | Authenticate and receive a JWT |
| `GET` | `/api/auth/me` | Yes | Return the authenticated admin |
| `GET` | `/api/logs` | Yes | Retrieve request history |
| `GET` | `/api/logs/stats` | Yes | Retrieve aggregate security metrics |
| `POST` | `/api/simulate` | Yes | Classify a payload without sending live traffic |
| `GET` | `/health` | No | Service health check |
| `WS` | `/ws/live?token=<jwt>` | JWT | Receive live WAF events |

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | Required | JWT signing secret |
| `ADMIN_USERNAME` | `admin` | Dashboard login username |
| `ADMIN_PASSWORD` | `change-me` | Dashboard login password |
| `DATABASE_URL` | SQLite | Database connection URL |
| `MODEL_DIR` | `./model/final` | Trained model directory |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated CORS origins |
| `ATTACK_CONFIDENCE_THRESHOLD` | `0.75` | ML confidence threshold |
| `GOOGLE_SAFE_BROWSING_API_KEY` | Optional | External URL reputation checks |

Never commit real secrets, API keys, or production credentials to GitHub.

---

## 🤖 Training the ML Model

The training data is stored in `ml_data/dataset.json`.

To train or retrain the model:

```bash
cd backend
python -m app.ml.train
```

The trained model is saved to the configured model directory. On lightweight Render deployments without PyTorch, the deterministic keyword and URL detection fallback remains active.

---

## ☁️ Deployment

### Render Backend

The repository includes `render.yaml` for Blueprint deployment:

1. Open Render and create a new Blueprint.
2. Connect the GitHub repository.
3. Render provisions the PostgreSQL database and backend service.
4. Set `ADMIN_PASSWORD`, `SECRET_KEY`, and `ALLOWED_ORIGINS`.
5. Verify the health endpoint:

```text
https://waf-backend-tc4u.onrender.com/health
```

### Vercel Frontend

1. Import the GitHub repository into Vercel.
2. Set the project root to `frontend`.
3. Configure:

```env
VITE_API_URL=https://waf-backend-tc4u.onrender.com
```

4. Deploy the frontend.
5. Add the final Vercel origin to Render's `ALLOWED_ORIGINS`.

---

## 🔐 Production Security Checklist

- [ ] Replace the default admin password.
- [ ] Generate a unique `SECRET_KEY`.
- [ ] Set `DEBUG=false`.
- [ ] Restrict CORS to trusted frontend origins.
- [ ] Use HTTPS for frontend, backend, and WebSocket traffic.
- [ ] Use PostgreSQL for persistent production data.
- [ ] Enable rate limiting before exposing the service publicly.
- [ ] Configure external threat intelligence where required.
- [ ] Rotate credentials if they were ever exposed.
- [ ] Monitor logs and review blocked requests regularly.

---

## 🚀 Future Enhancements

- Hybrid recommendation-style risk scoring for security events
- Larger real-world labeled threat dataset
- VirusTotal and Google Safe Browsing integrations
- Role-based access control
- Email, Slack, and webhook alerts
- Advanced request-rate limiting
- Model evaluation reports and confusion matrices
- Container image scanning in CI/CD
- Dedicated admin audit logs

---

## 🌐 Project Links

- GitHub: https://github.com/simhadris17/ai-waf
- Backend health check: https://waf-backend-tc4u.onrender.com/health
- Render: https://render.com
- Vercel: https://vercel.com
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev

---

## 👨‍💻 Author

**Simhadri Bhukya**
B.Tech — Computer Science Engineering
Machine Learning and AI Enthusiast

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- FastAPI Community
- React Community
- Scikit-learn and PyTorch Communities
- Render
- Vercel
- PostgreSQL

⭐ If you found this project useful, consider giving it a star on GitHub!

# GreenPulse AI - Production Deployment & Operations Guide

## 1. System Requirements & Prerequisites

### 1.1 Operating Environment
- **Operating System**: Linux (Ubuntu 22.04 LTS / RHEL 9 recommended) or Windows Server 2022.
- **Python Runtime**: Python 3.12+ or 3.13.
- **RAM**: Minimum 8 GB (16 GB recommended for concurrent batch inference and SHAP computations).
- **CPU**: 4+ Cores (AVX2 instructions recommended for XGBoost histogram tree compilation).
- **Storage**: Minimum 20 GB SSD.

### 1.2 Core Python Dependencies
- `fastapi >= 0.115.0`
- `uvicorn[standard] >= 0.32.0`
- `gunicorn >= 23.0.0`
- `xgboost >= 2.1.0`
- `shap >= 0.46.0`
- `joblib >= 1.4.0`
- `scikit-learn >= 1.5.0`
- `sqlalchemy[asyncio] >= 2.0.36`
- `aiosqlite >= 0.20.0` (or `asyncpg >= 0.30.0` for PostgreSQL)

---

## 2. Environment Configuration

Create a production `.env` file in `backend/`:

```env
# Application Settings
PROJECT_NAME="GreenPulse AI"
APP_ENV=production
DEBUG=false
API_V1_PREFIX=/api/v1
SECRET_KEY="generate-a-secure-256-bit-random-key"

# Database Configuration (PostgreSQL in production)
DATABASE_URL=postgresql+asyncpg://greenpulse_admin:SuperSecurePass123!@127.0.0.1:5432/greenpulse_db

# CORS Allowed Origins
BACKEND_CORS_ORIGINS=["https://greenpulse.plant.company.com", "https://app.greenpulse-ai.internal"]

# Industrial ML Model Settings
MODEL_REGISTRY_DIR=./trained_models
DEFAULT_GRID_EMISSION_FACTOR=0.82
CONTRACTED_MAX_DEMAND_KW=250.0

# Enterprise Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/greenpulse_ai.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

---

## 3. End-to-End Runtime Flows

### 3.1 Model Loading Flow (FastAPI Lifespan)
1. Process starts and triggers `lifespan(app)`.
2. Database connections and tables are initialized/verified.
3. `ModelRegistry.get_instance().initialize()` loads:
   - `scaler.joblib` and `encoder.joblib`
   - 4 XGBoost Multi-Target Regressors
   - Isolation Forest Anomaly Detector
   - 6 Industrial Intelligence Engines
4. Computes SHA-256 hashes for all model binaries and writes `model_registry.json`.
5. Models remain resident in memory across all worker threads.

### 3.2 Real-Time Inference & SHAP Flow
```
Client Request (GET /api/v1/forecast?horizon=24)
                       |
                       v
         FastAPI HTTP Middleware (log_requests)
                       |
                       v
         ForecastService.get_forecast()
                       |
                       +---> Checks In-Memory Cache (LRU + TTL)
                       |     (Returns instantly if query repeated)
                       v
         IndustrialPipelineService.predict_forecast()
                       |
                       +---> Vectorizes features (34-dim aligned)
                       +---> Invokes XGBoost Hist Regressors (< 5ms)
                       v
         ShapExplainabilityEngine.explain_prediction()
                       |
                       +---> Computes TreeExplainer SHAP values
                       +---> Ranks Top Contributing Features
                       +---> Synthesizes Natural Language Narrative
                       v
         AdaptiveThresholdEngine.evaluate_metric_threshold()
                       |
                       +---> Checks peak load vs Contract Limit (CMD)
                       v
         Enriched ForecastResponse JSON Envelope (200 OK)
```

---

## 4. Production Deployment Methods

### Method 1: Systemd Service + Gunicorn / Uvicorn Workers (Bare Metal / VM)

Create `/etc/systemd/system/greenpulse-ai.service`:

```ini
[Unit]
Description=GreenPulse AI Enterprise Industrial Backend
After=network.target postgresql.service

[Service]
Type=simple
User=greenpulse
Group=greenpulse
WorkingDirectory=/opt/greenpulse-ai/backend
Environment="PATH=/opt/greenpulse-ai/backend/.venv/bin"
EnvironmentFile=/opt/greenpulse-ai/backend/.env

ExecStart=/opt/greenpulse-ai/backend/.venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile /opt/greenpulse-ai/backend/logs/gunicorn_error.log

Restart=always
RestartSec=5s
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable greenpulse-ai
sudo systemctl start greenpulse-ai
sudo systemctl status greenpulse-ai
```

---

### Method 2: Docker Containerization

Create `Dockerfile` in `backend/`:

```dockerfile
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system build dependencies for C/C++ extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and trained models
COPY . .

# Expose API port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
docker build -t greenpulse-ai-backend:1.2.0 .
docker run -d -p 8000:8000 --env-file .env --name greenpulse-backend greenpulse-ai-backend:1.2.0
```

---

## 5. Enterprise Logging & Rotation Policies

Logs are managed by Python's `RotatingFileHandler` writing to `backend/logs/greenpulse_ai.log`:
- **Max File Size**: 10 MB per file.
- **Backup Retention**: 5 historical archives (`greenpulse_ai.log.1` through `.5`).
- **Domain Channels**:
  - `greenpulse.predictions`: Logs model inferences, input signatures, and latency ms.
  - `greenpulse.alerts`: Logs generated emergency, critical, and warning operational alerts.
  - `greenpulse.thresholds`: Logs upper/lower parameter excursions.
  - `greenpulse.recommendations`: Logs computed financial ROI and ECM rankings.
  - `greenpulse.rules`: Logs deterministic rule evaluations and trigger conditions.

---

## 6. Health Checks & Continuous Validation

Verify the live deployment:
```bash
# Basic Liveness probe
curl http://localhost:8000/health

# End-to-End Validation Suite
python scripts/generate_validation_report.py
```
Expected output: `Validation Outcome: PASSED (8 / 8 components passed)`.

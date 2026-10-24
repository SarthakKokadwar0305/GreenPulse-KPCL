# GreenPulse AI - Enterprise Industrial Energy Intelligence Platform Backend

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![ORM](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Architecture](https://img.shields.io/badge/architecture-Clean%20Architecture-brightgreen.svg)]()
[![Compliance](https://img.shields.io/badge/compliance-GHG%20Scope%201%20%26%202-orange.svg)]()

GreenPulse AI is an enterprise-grade backend for industrial manufacturing energy management, predictive maintenance, and sustainability accounting. Designed following patterns established by top industrial automation platforms (Siemens Simatic Energy Manager, Schneider Electric EcoStruxure, Honeywell Forge, and ABB Ability™).

---

## 1. Architectural Highlights

### Clean Architecture Separation
The system strictly enforces Clean Architecture principles. **Zero business logic resides inside API controllers.**

```
┌────────────────────────────────────────────────────────┐
│                      Client Apps                       │
│       (Existing Next.js Dashboard & Mobile Scanners)   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────▼────────────────────────────┐
│                  API Layer (app/api/)                  │
│   • Request parsing & Pydantic validation              │
│   • Dependency injection of database sessions          │
│   • Uniform ApiResponse[T] envelope serialization      │
└───────────────────────────┬────────────────────────────┘
                            │ Service Invocation
┌───────────────────────────▼────────────────────────────┐
│               Service Layer (app/services/)            │
│   • Domain orchestration & business logic              │
│   • Coordinates repositories and ML pipelines          │
│   • Counterfactual calculations & ROI evaluation       │
└─────────────┬────────────────────────────┬─────────────┘
              │ Repositories               │ Inferences
┌─────────────▼──────────────┐   ┌─────────▼─────────────┐
│    Repository Layer        │   │    ML Service Layer   │
│   (app/repositories/)      │   │       (app/ml/)       │
│ • Async queries & filters  │   │ • TFT Forecaster      │
│ • Unit of work commits     │   │ • Autoencoder Anomaly │
│ • Idempotent data seeding  │   │ • ECM Recommendation  │
└─────────────┬──────────────┘   │ • What-if Simulator   │
              │ ORM Sessions     │ • Model Artifact Reg. │
┌─────────────▼──────────────┐   └───────────────────────┘
│       Database Layer       │
│       (app/models/)        │
│ • PostgreSQL (Production)  │
│ • SQLite (Dev/Test)        │
└────────────────────────────┘
```

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── api/                     # Layer 1: FastAPI Route Controllers
│   │   ├── __init__.py          # Root APIRouter aggregator
│   │   ├── dashboard.py         # Real-time plant KPIs & executive summary
│   │   ├── plant.py             # Digital twin, department loads, shift telemetry
│   │   ├── machines.py          # 3-Phase electrical & thermal asset telemetry
│   │   ├── energy.py            # Hourly, daily, weekly, monthly & heatmaps
│   │   ├── carbon.py            # Scope 1 & 2 GHG Protocol carbon accounting
│   │   ├── forecast.py          # Multi-horizon TFT load forecasting & XAI
│   │   ├── anomaly.py           # Anomaly incident triage & work order dispatch
│   │   ├── recommendations.py   # Prescriptive Energy Conservation Measures
│   │   ├── simulator.py         # Parametric what-if counterfactual simulations
│   │   └── reports.py           # Compliance audit exports & scheduled jobs
│   │
│   ├── core/                    # Core Infrastructure
│   │   ├── config.py            # Pydantic BaseSettings & environment variables
│   │   ├── database.py          # Async SQLAlchemy engine & session factory
│   │   ├── logging.py           # Structured JSON enterprise logging
│   │   └── security.py          # PBKDF2 hashing, JWT & audit verification
│   │
│   ├── models/                  # Layer 4: SQLAlchemy ORM Entities
│   │   ├── base.py              # Declarative Base & TimestampMixin
│   │   ├── user.py              # User authentication & roles
│   │   ├── machine.py           # Asset registry, ratings, coordinates
│   │   ├── energy.py            # High-frequency electrical telemetry
│   │   ├── production.py        # Shift output, scrap rates & OEE metrics
│   │   ├── carbon.py            # Emission factors, grid intensity, solar offset
│   │   ├── forecast.py          # Quantile predictions & confidence bounds
│   │   ├── anomaly.py           # Incident evidence, root causes, severity
│   │   ├── recommendation.py    # Prescriptive measures, payback, status
│   │   ├── simulation.py        # Simulation audit log
│   │   ├── report.py            # Generated compliance documents
│   │   └── maintenance.py       # PM records, technician logs, downtime
│   │
│   ├── schemas/                 # Pydantic v2 DTO Contracts
│   │   ├── common.py            # Standard ApiResponse[T] envelope
│   │   ├── dashboard.py         # Dashboard schemas
│   │   ├── plant.py             # Plant digital twin schemas
│   │   ├── machine.py           # Electrical & thermal detail schemas
│   │   ├── energy.py            # Time-series & heatmap schemas
│   │   ├── carbon.py            # Scope 1/2 GHG accounting schemas
│   │   ├── forecast.py          # TFT forecast schemas & XAI schemas
│   │   ├── anomaly.py           # Incident card & work order schemas
│   │   ├── recommendation.py    # Prescriptive ECM schemas
│   │   ├── simulation.py        # Parametric what-if schemas
│   │   └── report.py            # Compliance report schemas
│   │
│   ├── repositories/            # Layer 3: Database Query Layer
│   │   ├── base.py              # Generic CRUD repository
│   │   ├── machine_repository.py
│   │   ├── energy_repository.py
│   │   ├── anomaly_repository.py
│   │   ├── recommendation_repository.py
│   │   └── report_repository.py
│   │
│   ├── services/                # Layer 2: Business & Orchestration Layer
│   │   ├── dashboard_service.py
│   │   ├── plant_service.py
│   │   ├── machine_service.py
│   │   ├── energy_service.py
│   │   ├── carbon_service.py
│   │   ├── forecast_service.py
│   │   ├── anomaly_service.py
│   │   ├── recommendation_service.py
│   │   ├── simulator_service.py
│   │   └── report_service.py
│   │
│   ├── ml/                      # Machine Learning Service Interfaces
│   │   ├── model_loader.py      # Artifact registry & model loader
│   │   ├── forecasting.py       # Multi-horizon load, cost & carbon inference
│   │   ├── anomaly_detection.py # Autoencoder & SPC risk scoring
│   │   ├── recommendation_engine.py # Prescriptive ECM generator & ROI estimator
│   │   └── simulator.py         # Parametric counterfactual engine
│   │
│   ├── utils/                   # System Utilities
│   │   └── seed_data.py         # Idempotent master data seeding
│   │
│   └── main.py                  # FastAPI Application Entrypoint & Middleware
│
├── datasets/                    # Pre-generated synthetic CSV datasets
├── trained_models/              # Phase 2 trained Joblib / ONNX model artifacts
├── requirements.txt             # Locked Python dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # System documentation
```

---

## 3. Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| **Language** | Python 3.12+ | High-throughput asynchronous IO and mature data engineering ecosystem |
| **API Framework** | FastAPI | Native async performance, automatic OpenAPI v3 documentation, standard dependency injection |
| **Data Validation** | Pydantic v2 | High-speed C-based JSON serialization and strict type enforcement |
| **ORM** | SQLAlchemy 2.0 (Async) | Enterprise-grade query builder with support for SQLite and PostgreSQL |
| **Database Engines** | PostgreSQL / SQLite | SQLite for frictionless local dev; PostgreSQL via `asyncpg` for production |
| **Migration Engine**| Alembic | Production-ready schema migration tracking |
| **Data Processing** | Pandas & NumPy | Vectorized industrial telemetry aggregations |
| **Model Serving** | Joblib | Low-latency serialization for scikit-learn, XGBoost, and PyTorch exports |

---

## 4. API Endpoints Reference

All endpoints are mounted under `/api/v1` and return standard `ApiResponse[T]` envelopes:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed",
  "error_code": null,
  "timestamp": "2026-10-24T16:00:00Z"
}
```

### Module Route Map

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Dashboard** | `GET` | `/api/v1/dashboard/overview` | Plant KPIs, active machines, demand, costs, carbon footprint, priority alerts |
| **Plant** | `GET` | `/api/v1/plant/overview` | Production summary, department telemetry, shift schedules, factory timeline |
| **Machines** | `GET` | `/api/v1/machines` | Fleet asset listing with operational health indices and power draw |
| **Machines** | `GET` | `/api/v1/machines/{id}` | Detailed digital twin: 3-phase currents, voltages, harmonics, thermal logs |
| **Energy** | `GET` | `/api/v1/energy/analytics` | Hourly, daily, weekly, monthly load profiles, machine comparisons, 7x24 heatmap |
| **Carbon** | `GET` | `/api/v1/carbon/accounting` | Scope 1 & Scope 2 breakdowns, machine emissions, sustainability score |
| **Forecast** | `GET` | `/api/v1/forecast` | Multi-horizon TFT load forecast, 80%/95% confidence bounds, XAI drivers |
| **Anomalies** | `GET` | `/api/v1/anomaly` | Active equipment anomalies with sensor evidence and z-score diagnostics |
| **Anomalies** | `POST`| `/api/v1/anomaly/{id}/acknowledge` | Engineer acknowledgment of incident |
| **Anomalies** | `POST`| `/api/v1/anomaly/{id}/work-order` | Dispatch maintenance work order ticket |
| **Recommendations** | `GET` | `/api/v1/recommendations` | Prescriptive Energy Conservation Measures (ECMs) with payback & ROI |
| **Recommendations** | `POST`| `/api/v1/recommendations/{id}/apply` | Apply recommendation and dispatch setpoints |
| **Simulator** | `POST`| `/api/v1/simulator/simulate` | Parametric what-if counterfactual simulation |
| **Simulator** | `POST`| `/api/v1/simulator/compare` | Multi-scenario side-by-side comparison |
| **Reports** | `GET` | `/api/v1/reports` | List compliance audits across Energy, Carbon, Forecast, and Anomaly |
| **Reports** | `POST`| `/api/v1/reports/generate` | On-demand compliance audit report compilation (PDF, CSV, Excel) |
| **System** | `GET` | `/health` | System health check and database connectivity |
| **Docs** | `GET` | `/docs` | Interactive Swagger UI API Documentation |

---

## 5. Machine Learning Integration Roadmap (Phase 2)

The architecture is deliberately built with strict separation between API contracts and model execution:

1. **Service Interfaces**:
   - `app/ml/forecasting.py`: Implements `predict_energy()`, `predict_cost()`, `predict_carbon()`.
   - `app/ml/anomaly_detection.py`: Implements `detect_anomaly()`, `calculate_risk_score()`.
   - `app/ml/recommendation_engine.py`: Implements `generate_recommendations()`, `estimate_savings()`, `estimate_roi()`.
   - `app/ml/simulator.py`: Implements `simulate()`, `compare_scenarios()`.
   - `app/ml/model_loader.py`: Implements singleton `ModelArtifactRegistry`.

2. **Phase 2 Drop-in Process**:
   - Drop trained Joblib model weights into `backend/trained_models/`.
   - Set `MODEL_STORAGE_PATH=trained_models/` in `.env`.
   - The `load_models()` lifecycle hook automatically loads and caches serialized models in memory on startup.
   - **No modifications to API routes or Pydantic contracts are required.**

---

## 6. Quick Start & Execution

### 1. Environment Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration (.env)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default SQLite database connection (`sqlite+aiosqlite:///./greenpulse.db`) is preconfigured for zero-setup local execution. For production PostgreSQL, set:
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/greenpulse_db
```

### 3. Launch Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The database tables and seed data will be automatically verified on first boot.

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Running Integration Tests
```bash
python test_routes.py
```

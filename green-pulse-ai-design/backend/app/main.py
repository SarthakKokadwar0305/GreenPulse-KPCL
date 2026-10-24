"""
GreenPulse AI - Industrial Energy Intelligence Platform Backend
Main FastAPI Application Entrypoint

Follows Clean Architecture & Enterprise Industrial Software Design:
- Layer 1: FastAPI API Routes (app/api/)
- Layer 2: Domain Services (app/services/)
- Layer 3: Database Repositories (app/repositories/)
- Layer 4: SQLAlchemy ORM Models (app/models/)
- ML Layer: Extensible AI Model Interfaces (app/ml/)
"""
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_router
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal, get_db
from app.core.logging import logger
from app.ml.model_loader import load_models
from app.schemas.common import ApiResponse
from app.utils.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle manager:
    Initializes database tables, runs seed routines, and pre-loads ML models.
    """
    logger.info("=================================================================")
    logger.info("Initializing GreenPulse AI Industrial Platform Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    logger.info("=================================================================")

    # 1. Initialize schema tables
    try:
        await init_db()
        logger.info("SQLAlchemy database schema successfully verified / created.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # 2. Seed initial master data
    try:
        async with AsyncSessionLocal() as session:
            await seed_database(session)
    except Exception as e:
        logger.error(f"Database seeding error: {e}")

    # 3. Pre-load Production AI Model Artifacts & Engines
    try:
        from app.ml.model_registry import get_model_registry
        registry = get_model_registry()
        logger.info(
            f"Production ModelRegistry initialized: {len(registry._models)} Joblib models, "
            f"{len(registry._preprocessors)} preprocessors, and {len(registry._engines)} Industrial Engines loaded."
        )
    except Exception as e:
        logger.error(f"Error initializing ModelRegistry: {e}")

    # 4. Initialize AI Copilot Knowledge Vector Store (RAG)
    try:
        from pathlib import Path
        from app.copilot.vector_store import VectorStoreService
        from app.copilot.embeddings import EmbeddingService
        from app.copilot.ingestion import DocumentIngestionPipeline
        emb = EmbeddingService(model_name=settings.EMBEDDING_MODEL_NAME)
        vstore = VectorStoreService(storage_path=settings.QDRANT_PATH, vector_dim=emb.vector_dim)
        vstore.update_vector_dim(emb.vector_dim)
        pipeline = DocumentIngestionPipeline(vector_store=vstore, embedding_service=emb)
        docs_dir = Path(settings.DOCUMENTS_DIR)
        res = pipeline.ingest_knowledge_directory(docs_dir)
        total_chunks = sum(res.values())
        logger.info(f"AI Copilot RAG Knowledge Store initialized: {total_chunks} chunks indexed across {len(res)} collections.")
    except Exception as e:
        logger.warning(f"Note on AI Copilot RAG init: {e}")

    logger.info("GreenPulse AI Backend is ready to accept requests.")
    yield

    # Teardown logic
    logger.info("GreenPulse AI Backend shutting down...")


OPENAPI_TAGS = [
    {
        "name": "Authentication & RBAC",
        "description": "Enterprise JWT authentication, OAuth2 password flow, refresh token rotation, role-based authorization, and compliance audit trail.",
    },
    {
        "name": "Forecast",
        "description": "Multi-horizon industrial energy demand, financial expenditure, and carbon emissions forecasting powered by XGBoost with TreeExplainer SHAP explainability.",
    },
    {
        "name": "Anomalies",
        "description": "Real-time unsupervised operational anomaly detection powered by Isolation Forest, severity scoring, root-cause attribution, and automated ticket dispatch.",
    },
    {
        "name": "Recommendations",
        "description": "Prescriptive Energy Conservation Measures (ECMs) prioritized via Multi-Criteria Decision Analysis (MCDA), financial ROI, and dynamic domain rules.",
    },
    {
        "name": "Simulator",
        "description": "What-If parametric scenario modeling, tariff optimization, shift schedule balancing, and renewable integration counterfactual simulations.",
    },
    {
        "name": "Dashboard",
        "description": "Executive KPI aggregation, real-time demand meters, load distribution, and operational metrics.",
    },
    {
        "name": "Energy",
        "description": "High-resolution telemetry analytics, peak demand profiles, and departmental load breakdown.",
    },
    {
        "name": "Carbon",
        "description": "GHG Protocol Scope 1 & Scope 2 carbon accounting, emission intensity metrics, and reduction tracking.",
    },
    {
        "name": "Machines",
        "description": "Digital twin telemetry, machine status monitoring, and component health analytics.",
    },
    {
        "name": "Reports",
        "description": "Compliance reporting, periodic energy audit export, and PDF/CSV synthesis.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.2.0-prod",
    description="""
# GreenPulse AI - Enterprise Industrial AI & Energy Intelligence Platform API

An enterprise-grade platform powering real-time industrial telemetry, digital twins, 
carbon accounting (GHG Protocol Scope 1 & 2), predictive AI load forecasting, 
unsupervised anomaly diagnostics, prescriptive recommendations, and parametric what-if simulations.

### Enterprise AI & MLOps Architecture:
- **Model Registry Singleton**: Zero per-request reloading; 5 Joblib models & 6 industrial engines cached in memory.
- **SHAP Explainability**: XGBoost `TreeExplainer` delivers per-prediction local feature attributions and natural-language narratives.
- **Dynamic Industrial Reasoning**: 60 deterministic domain rules & adaptive thresholds for equipment telemetry.
- **Enterprise Response Architecture**: Consistent structured JSON with confidence, rules triggered, threshold status, and model metadata.
    """,
    openapi_tags=OPENAPI_TAGS,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# CORS Middleware
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Structured Request Logging Middleware
# -----------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} ({duration_ms} ms)"
    )
    return response


# -----------------------------------------------------------------------------
# Global Exception Handlers
# -----------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.fail(message=str(exc.detail)).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = [f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()]
    combined_msg = "Validation failed: " + "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse.fail(message=combined_msg).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.fail(message="Internal industrial server error. Please consult logs.").model_dump(),
    )


# -----------------------------------------------------------------------------
# System & Health Check Endpoints
# -----------------------------------------------------------------------------
@app.get("/", tags=["System"])
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "api_v1_base": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["System"])
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "greenpulse-ai-backend",
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "timestamp": time.time(),
    }


# -----------------------------------------------------------------------------
# Mount Clean Architecture API Router (/api/v1 and root alias)
# -----------------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_router, prefix="", include_in_schema=False)


# Direct top-level aliases for enterprise validation compliance
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.schemas.machine import MachineDetailSchema
from app.services.simulator_service import SimulatorService
from app.services.machine_service import MachineService
from app.core.dependencies import get_current_user, require_permissions, verify_machine_authorization
from app.models.user import User
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


@app.post("/simulate", response_model=ApiResponse[SimulationResponse], include_in_schema=False)
@app.post(f"{settings.API_V1_PREFIX}/simulate", response_model=ApiResponse[SimulationResponse], include_in_schema=False)
async def direct_simulate(
    request: SimulationRequest,
    current_user: User = Depends(require_permissions("VIEW_SIMULATOR", "RUN_SIMULATION")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SimulationResponse]:
    service = SimulatorService(db)
    result = await service.run_simulation(request)
    return ApiResponse.ok(data=result, message="Simulation computed successfully")


@app.get("/machine/{machine_id}", response_model=ApiResponse[MachineDetailSchema], include_in_schema=False)
@app.get(settings.API_V1_PREFIX + "/machine/{machine_id}", response_model=ApiResponse[MachineDetailSchema], include_in_schema=False)
async def direct_get_machine(
    machine_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MachineDetailSchema]:
    verify_machine_authorization(machine_id, current_user)
    service = MachineService(db)
    machine = await service.get_machine_by_id(machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID '{machine_id}' was not found in plant registry."
        )
    return ApiResponse.ok(data=machine, message=f"Machine '{machine_id}' telemetry fetched")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

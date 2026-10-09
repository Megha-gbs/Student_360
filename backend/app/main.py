"""
Student360 FastAPI Backend Application.
Entry point for ML inference, explainability, trajectory, and cohort insights APIs.
"""

from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path so ml.* modules are resolvable
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Canonical NumPy 2.x compatibility shim for SHAP
import numpy as np

if not hasattr(np, "obj2sctype"):
    def _obj2sctype(obj):
        try:
            return np.dtype(obj).type
        except TypeError:
            return obj if isinstance(obj, type) and issubclass(obj, np.generic) else None

    np.obj2sctype = _obj2sctype

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import (
    ALLOWED_ORIGINS,
    PROJECT_NAME,
)
from backend.app.routes import (
    auth_router,
    cohort_router,
    college_router,
    data_import_router,
    intervention_router,
    scoring_router,
    simulation_router,
    students_router,
)
from backend.app.schemas import HealthResponse
from backend.app.services.college_service import college_service
from backend.app.services.model_service import model_service
from backend.app.services.student_service import student_service

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("student360.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up cached artifacts and demo students during startup."""
    logger.info("Initializing Student360 ML backend...")
    try:
        model_service.load_artifacts()
        student_service._ensure_loaded()
        college_service.generate_daily_schedule_notifications()
        logger.info("Artifacts, demo students, and daily schedule notifications successfully preloaded.")
    except Exception as exc:
        logger.error("Error preloading artifacts on startup: %s", exc)
    yield
    logger.info("Shutting down Student360 ML backend.")


app = FastAPI(
    title=PROJECT_NAME,
    version="1.0.0",
    description=(
        "Production-ready FastAPI backend and API orchestration layer for the Student360 platform. "
        "Provides real XGBoost risk inference, SHAP explanations, Sem1->Sem2 trajectories, "
        "and cohort-wide analytics."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/", include_in_schema=False)
@app.get("/login", include_in_schema=False)
def root_info():
    """Friendly information response when hitting backend root or /login in browser."""
    return {
        "service": "Student360 API Gateway",
        "status": "online",
        "documentation": "/docs",
        "health": "/health",
        "notice": "This port (8000) is the FastAPI backend REST API. The Student360 Institutional Web Portal is hosted on the frontend server (http://localhost:3000 or http://localhost:3001). Please access the web application through your frontend URL.",
    }



# Exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled server exception at %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An internal server error occurred: {str(exc)}"},
    )


# Root Health Endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Service Health Check",
    description="Returns the operational status of the Student360 API service.",
)
def health_check() -> HealthResponse:
    """Check service health."""
    return HealthResponse(status="ok")


# Register Routers
app.include_router(auth_router)
app.include_router(college_router)
app.include_router(students_router)
app.include_router(simulation_router)
app.include_router(intervention_router)
app.include_router(cohort_router)
app.include_router(scoring_router)
app.include_router(data_import_router)



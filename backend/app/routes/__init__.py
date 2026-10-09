"""
API Route Handlers for Student360.
"""

from backend.app.routes.students import router as students_router
from backend.app.routes.simulation import router as simulation_router
from backend.app.routes.intervention import router as intervention_router
from backend.app.routes.cohort import router as cohort_router
from backend.app.routes.auth import router as auth_router
from backend.app.routes.college import router as college_router
from backend.app.routes.scoring import router as scoring_router
from backend.app.routes.data_import import router as data_import_router

__all__ = [
    "students_router",
    "simulation_router",
    "intervention_router",
    "cohort_router",
    "auth_router",
    "college_router",
    "scoring_router",
    "data_import_router",
]



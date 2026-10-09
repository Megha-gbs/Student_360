"""
Cohort insights routes for aggregate analytics and global SHAP drivers.
"""

from typing import Dict
from fastapi import APIRouter, Depends

from backend.app.schemas import CohortInsightsResponse
from backend.app.services.cohort_service import cohort_service
from backend.app.security import get_authenticated_user, require_roles

router = APIRouter(tags=["Cohort Analytics"])


@router.get(
    "/cohort/insights",
    response_model=CohortInsightsResponse,
    summary="Get cohort-wide aggregate risk insights and global SHAP feature importance",
    description=(
        "Calculates real aggregate distributions (High, Medium, Low risk counts) "
        "and cohort-wide mean absolute SHAP feature importances across all verified demo students."
    ),
)
def get_cohort_insights(
    current_user: Dict = Depends(require_roles(["admin", "faculty"]))
) -> CohortInsightsResponse:
    """Return live aggregate metrics and global SHAP drivers."""
    data = cohort_service.get_cohort_insights()
    return CohortInsightsResponse(**data)


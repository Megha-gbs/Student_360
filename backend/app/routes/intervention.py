"""backend/app/routes/intervention.py

Intervention and simulated outcome routes with RBAC.
Supports both POST /intervention and POST /intervene with human-in-the-loop review.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas import (
    InterventionRequest,
    InterventionResponse,
    SimulatedOutcomeResponse,
)
from backend.app.security import check_student_access, get_authenticated_user
from backend.app.services.intervention_service import intervention_service
from backend.app.services.student_service import student_service

router = APIRouter(tags=["Interventions"])


@router.post(
    "/intervention",
    response_model=InterventionResponse,
    summary="Draft or approve student intervention strategy",
    description="Drafts recommended intervention strategies tailored to real risk factors and captures human approval.",
)
@router.post(
    "/intervene",
    response_model=InterventionResponse,
    summary="Alias for /intervention",
    description="Maintains backward compatibility with /intervene.",
)
def create_intervention(
    request: InterventionRequest,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
) -> InterventionResponse:
    """Execute intervention workflow with human-in-the-loop governance."""
    # Only faculty and administrators can draft/approve interventions
    if current_user.get("role") == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Students cannot draft or authorize interventions.",
        )

    if request.student_id:
        check_student_access(request.student_id, current_user)

    result = intervention_service.process_intervention(
        student_id=request.student_id,
        intervention_type=request.intervention_type,
        parameters=request.parameters,
        approved=request.approved,
        notes=request.notes,
    )
    return InterventionResponse(**result)


@router.post(
    "/students/{student_id}/simulate-outcome",
    response_model=SimulatedOutcomeResponse,
    summary="Simulate follow-up outcome of student intervention",
    description=(
        "Simulates impact of an intervention on student risk trajectory. "
        "Explicitly labelled with SIMULATED DEMONSTRATION OUTCOME badge."
    ),
    responses={
        403: {"description": "Access denied for unauthorized student/faculty"},
        404: {
            "description": "Student not found",
            "content": {"application/json": {"example": {"detail": "Student S9999 not found"}}},
        },
    },
)
def simulate_student_intervention_outcome(
    student_id: str,
    request: Optional[InterventionRequest] = None,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
) -> SimulatedOutcomeResponse:
    """Simulate intervention outcome for a specific student."""
    check_student_access(student_id, current_user)

    student = student_service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found",
        )

    features = student.get("features", {})
    interv_params = request.model_dump() if request else None

    result = intervention_service.simulate_outcome(
        student_id=student_id,
        student_features=features,
        intervention_data=interv_params,
    )
    return SimulatedOutcomeResponse(**result)

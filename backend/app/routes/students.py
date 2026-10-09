"""backend/app/routes/students.py

Student routes for querying student cohort list, priority queue, and detailed profiles.
Enforces Role-Based Access Control (RBAC):
- Administrator: All institution students
- Faculty: Assigned students only
- Student: Own profile only (403 for priority queue or other students)
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status

from backend.app.schemas import (
    PredictionResult,
    StudentListItem,
    StudentListResponse,
    StudentResponse,
    TrajectoryData,
)
from backend.app.security import check_student_access, get_authenticated_user
from backend.app.services.college_service import college_service
from backend.app.services.model_service import model_service
from backend.app.services.scoring_service import scoring_service
from backend.app.services.shap_service import shap_service
from backend.app.services.student_service import student_service
from backend.app.services.trajectory_service import trajectory_service

COURSE_NAMES = {
    171: "Animation and Multimedia Design (171)",
    9254: "Agronomy (9254)",
    9070: "Communication Design (9070)",
    9773: "Veterinary Nursing (9773)",
    9238: "Basic Education (9238)",
    9147: "Management (9147)",
    9003: "Social Service (9003)",
    9119: "Informatics Engineering (9119)",
    9500: "Nursing (9500)",
    9085: "Journalism and Communication (9085)",
    9239: "Tourism (9239)",
}


def get_course_name(course_id: Any) -> str:
    try:
        cid = int(course_id)
        return COURSE_NAMES.get(cid, f"Degree Program ({cid})")
    except (ValueError, TypeError):
        return str(course_id) if course_id else "Degree Program"


router = APIRouter(tags=["Students"])


@router.get(
    "/students",
    response_model=StudentListResponse,
    summary="List all students with dynamic risk predictions",
    description="Loads verified students permitted for the authenticated role, runs real inference, and calculates trend.",
)
@router.get(
    "/students/priority-queue",
    response_model=StudentListResponse,
    summary="Priority Queue: List students ranked by risk and urgency",
    description="Ranks students descending by risk score for early warning intervention triage.",
)
def list_students(
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
) -> StudentListResponse:
    """Fetch students permitted for current role, ranked by risk score."""
    user_role = current_user.get("role")
    if user_role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Priority Queue is restricted to Faculty and Administrators.",
        )

    raw_students = student_service.get_all_students()
    items = []

    # Faculty sees assigned students only
    assigned_ids = None
    if user_role == "faculty":
        fac_info = college_service.get_faculty_by_id(current_user.get("id")) or current_user
        assigned_ids = fac_info.get("assigned_student_ids")

    for raw in raw_students:
        sid = str(raw.get("demo_id") or raw.get("student_id", "UNKNOWN"))

        if assigned_ids is not None and sid not in assigned_ids:
            continue

        features = raw.get("features", {})

        # Predict dynamically
        pred = model_service.predict(features=features, student_id=sid)
        risk_score = pred["risk_score"]
        risk_level = pred["risk_level"]
        dropout_prob = pred["dropout_probability"]
        model_version = pred["model_version"]

        # Trajectory trend calculation via Smruthi's trajectory engine
        trend = trajectory_service.get_trend(features, risk_score_sem2=risk_score)

        # Operational priority: High risk -> High, Medium -> Medium, Low -> Low
        priority = risk_level
        course_name = get_course_name(features.get("Course"))

        # Holistic scoring indicators
        success_info = scoring_service.get_student_success_score(sid)
        placement_info = scoring_service.get_student_placement_readiness(sid)

        items.append(
            StudentListItem(
                student_id=sid,
                risk_score=risk_score,
                risk_level=risk_level,
                dropout_probability=dropout_prob,
                model_version=model_version,
                trend=trend,
                priority=priority,
                course_name=course_name,
                success_score=success_info.get("success_score"),
                placement_readiness=placement_info.get("readiness_score"),
            )
        )

    # Sort descending by risk_score so highest risk students appear first in priority queue
    items.sort(key=lambda s: s.risk_score, reverse=True)

    return StudentListResponse(total=len(items), students=items)


@router.get(
    "/students/{student_id}",
    response_model=StudentResponse,
    summary="Get individual student risk details, SHAP reasons, and trajectory",
    description="Retrieves a verified student by ID, enforces RBAC, evaluates live ML model risk, and attaches explainability.",
    responses={
        403: {"description": "Access denied for unauthorized student/faculty"},
        404: {
            "description": "Student not found",
            "content": {"application/json": {"example": {"detail": "Student S9999 not found"}}},
        },
    },
)
def get_student(
    student_id: str,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
) -> StudentResponse:
    """Fetch individual student profile with dynamic predictions, SHAP, and trajectory."""
    # Enforce RBAC (student own profile, faculty assigned, admin institution)
    check_student_access(student_id, current_user)

    raw = student_service.get_student_by_id(student_id)
    if raw is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found",
        )

    sid = str(raw.get("demo_id") or raw.get("student_id", student_id))
    features = raw.get("features", {})
    row_index = raw.get("dataset_row_index")
    actual_outcome = raw.get("actual_outcome_reference")

    # Live model prediction
    pred_data = model_service.predict(features=features, student_id=sid)
    risk_score = pred_data["risk_score"]
    risk_level = pred_data["risk_level"]
    dropout_prob = pred_data["dropout_probability"]
    model_version = pred_data["model_version"]

    prediction = PredictionResult(
        student_id=pred_data["student_id"],
        risk_score=risk_score,
        risk_level=risk_level,
        dropout_probability=dropout_prob,
        model_version=model_version,
    )

    # Explainability: Top SHAP reasons from Smruthi's engine (grouped to original UCI features)
    top_reasons = shap_service.explain_student(student_features=features, top_k=5)

    # Trajectory: Real Sem1 -> Sem2 journey from Smruthi's engine
    trajectory_raw = trajectory_service.get_trajectory(
        student_features=features,
        risk_score_sem2=risk_score,
    )
    trajectory_data: Optional[TrajectoryData] = None
    if trajectory_raw is not None:
        trajectory_data = TrajectoryData(**trajectory_raw)

    # Trend calculation
    trend = trajectory_service.get_trend(trajectory_raw or features, risk_score_sem2=risk_score)

    # Holistic scoring calculation
    success_info = scoring_service.get_student_success_score(sid)
    placement_info = scoring_service.get_student_placement_readiness(sid)

    return StudentResponse(
        student_id=sid,
        risk_score=risk_score,
        risk_level=risk_level,
        dropout_probability=dropout_prob,
        model_version=model_version,
        trend=trend,
        top_reasons=top_reasons,
        trajectory_data=trajectory_data,
        dataset_row_index=row_index,
        features=features,
        prediction=prediction,
        actual_outcome_reference=actual_outcome,
        course_name=get_course_name(features.get("Course")),
        success_score=success_info.get("success_score"),
        success_tier=success_info.get("standing_tier"),
        placement_readiness=placement_info.get("readiness_score"),
        placement_tier=placement_info.get("readiness_tier"),
    )

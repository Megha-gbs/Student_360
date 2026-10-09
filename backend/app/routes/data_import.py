"""backend/app/routes/data_import.py

Data Import and CSV Validation Route.
Provides endpoints for validating institutional academic dataset uploads
strictly against the frozen 36 UCI features schema with RBAC protection.
Accepts raw CSV body directly via FastAPI Request body, avoiding forced python-multipart dependency.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.app.schemas import CSVValidationResponse
from backend.app.security import get_authenticated_user, require_roles
from backend.app.services.csv_service import csv_service
from backend.app.services.student_service import student_service

router = APIRouter(tags=["Data Import"])


@router.post(
    "/data/validate-csv",
    response_model=CSVValidationResponse,
    summary="Validate academic dataset CSV data",
    description="Inspects CSV against the 36 UCI feature schema, checks ranges, detects duplicates, and provides row-level validation.",
)
async def validate_academic_csv(
    request: Request,
    filename: Optional[str] = Query("academic_data.csv", description="Filename or descriptor"),
    preview_only: bool = Query(True, description="When true, performs validation and preview without persisting"),
) -> CSVValidationResponse:
    """Validates an uploaded CSV dataset for schema and data integrity."""
    content = await request.body()
    if not content or len(content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is empty. Please provide raw CSV content in request body.",
        )

    fname = filename or "academic_data.csv"
    if not fname.lower().endswith(".csv"):
        fname += ".csv"

    result = csv_service.validate_csv(
        file_content=content,
        filename=fname,
        preview_only=preview_only,
    )
    return CSVValidationResponse(**result)


@router.post(
    "/data/import-csv",
    response_model=CSVValidationResponse,
    summary="Import validated academic dataset CSV",
    description="Restricted to Admin/Faculty. Validates and stages records if valid.",
)
async def import_academic_csv(
    request: Request,
    filename: Optional[str] = Query("academic_data.csv", description="Filename or descriptor"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "faculty"])),
) -> CSVValidationResponse:
    """Imports academic data after full validation enforcing RBAC."""
    content = await request.body()
    if not content or len(content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is empty. Please provide raw CSV content in request body.",
        )

    fname = filename or "academic_data.csv"
    if not fname.lower().endswith(".csv"):
        fname += ".csv"

    result = csv_service.validate_csv(
        file_content=content,
        filename=fname,
        preview_only=False,
    )

    if not result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "CSV validation failed; import aborted to protect database integrity.",
                "total_rows": result["total_rows"],
                "rejected_rows": result["rejected_rows"],
                "errors_sample": [e.model_dump() for e in result["errors"][:10]],
            },
        )

    parsed_students = result.get("parsed_records", [])
    added_count = 0
    if parsed_students:
        added_count = student_service.add_students(parsed_students)

    result["message"] = f"Successfully validated and ingested {added_count} student record(s) into active registry."
    return CSVValidationResponse(**result)

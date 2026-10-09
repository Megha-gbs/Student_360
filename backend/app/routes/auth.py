"""backend/app/routes/auth.py

Authentication, User Identity, and Administrative User Management Endpoints for Student360.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.schemas_college import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    UserProfile,
)
from backend.app.security import (
    extract_token_from_header,
    get_authenticated_user,
    require_roles,
    session_store,
)
from backend.app.services.college_service import college_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: Optional[str] = "Student@360"
    name: str
    role: str = "student"
    department: Optional[str] = "General Studies"
    designation: Optional[str] = None
    semester: Optional[int] = 1
    program: Optional[str] = None
    phone: Optional[str] = None
    assigned_student_ids: Optional[List[str]] = None


class UserStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(Active|Deactivated)$")


class AssignStudentsRequest(BaseModel):
    student_ids: List[str]


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user and return session token and profile",
)
def login(request: LoginRequest) -> LoginResponse:
    target_username = request.username or request.username_or_email or request.email or ""
    auth_result = college_service.authenticate_user(
        username=target_username,
        password=request.password,
        role_hint=request.role,
    )
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = auth_result["user"]
    profile = UserProfile(
        id=user_data["id"],
        username=user_data["username"],
        name=user_data["name"],
        email=user_data["email"],
        role=user_data["role"],
        avatar=user_data.get("avatar"),
        department=user_data.get("department"),
        semester=user_data.get("semester"),
        program=user_data.get("program"),
        designation=user_data.get("designation"),
        phone=user_data.get("phone"),
    )
    return LoginResponse(
        token=auth_result["token"],
        user=profile,
        message=f"Welcome back, {profile.name}!",
    )


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current authenticated user profile",
)
def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
) -> UserProfile:
    return UserProfile(
        id=current_user["id"],
        username=current_user["username"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
        avatar=current_user.get("avatar"),
        department=current_user.get("department"),
        semester=current_user.get("semester"),
        program=current_user.get("program"),
        designation=current_user.get("designation"),
        phone=current_user.get("phone"),
    )


@router.post(
    "/logout",
    summary="Logout user session and invalidate token",
)
def logout(authorization: Optional[str] = Header(None)):
    token = extract_token_from_header(authorization)
    if token:
        session_store.revoke_session(token)
    return {"status": "success", "message": "Successfully logged out"}


@router.post(
    "/change-password",
    summary="Update current user password",
)
def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
):
    success, message = college_service.change_password(
        user_id=current_user["id"],
        old_password=request.old_password,
        new_password=request.new_password,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    return {"status": "success", "message": message}


# ---------------------------------------------------------------------------
# Admin User & Role Management Endpoints
# ---------------------------------------------------------------------------
@router.get(
    "/users",
    summary="List all user accounts in institution (Administrator Only)",
)
def list_users(
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can view user accounts.",
        )
    return college_service.get_all_users(institution_id=current_user.get("institution_id"))


@router.post(
    "/users",
    summary="Create a new user account (Administrator Only)",
)
def create_user(
    request: UserCreateRequest,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can create accounts.",
        )
    try:
        new_account = college_service.create_user_account(
            user_data=request.model_dump(),
            actor=current_user.get("username", "admin"),
        )
        return new_account
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.patch(
    "/users/{user_id}/status",
    summary="Activate or deactivate a user account (Administrator Only)",
)
@router.put(
    "/users/{user_id}/status",
    summary="Activate or deactivate a user account (Administrator Only)",
)
def update_user_status(
    user_id: str,
    request: UserStatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can change account status.",
        )

    updated = college_service.update_user_status(
        user_id=user_id,
        new_status=request.status,
        actor=current_user.get("username", "admin"),
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return updated


@router.post(
    "/faculty/{faculty_id}/assign-students",
    summary="Assign student cohort to a faculty member (Administrator Only)",
)
def assign_students(
    faculty_id: str,
    request: AssignStudentsRequest,
    current_user: Dict[str, Any] = Depends(get_authenticated_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can assign students.",
        )
    updated_fac = college_service.assign_students_to_faculty(
        faculty_id=faculty_id,
        student_ids=request.student_ids,
        actor=current_user.get("username", "admin"),
    )
    if not updated_fac:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty {faculty_id} not found",
        )
    return {"status": "success", "faculty_id": faculty_id, "assigned_students": request.student_ids}

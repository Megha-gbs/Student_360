"""backend/app/routes/college.py

Comprehensive college management router covering:
- Timetable & Class Schedule
- Attendance Management & Reports
- Marks & Academic Results
- Assignments & Grading
- Announcements & Notices
- Examination Scheduling
- Fees & Payment Receipts
- Daily Schedule In-App Notifications
- Faculty & Student Administrative Operations
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.schemas_college import (
    AdminStudentCreate,
    AdminStudentItem,
    AnnouncementCreateRequest,
    AnnouncementItem,
    AssignmentCreateRequest,
    AssignmentGradeRequest,
    AssignmentItem,
    AssignmentSubmission,
    AssignmentSubmitRequest,
    AttendanceReportItem,
    BulkAttendanceSubmit,
    ConflictCheckResponse,
    CsvImportResult,
    DailyScheduleNotificationResult,
    ExaminationCreateRequest,
    ExaminationItem,
    FeePaymentRequest,
    InstitutionFeeSummary,
    MarksUpdateRequest,
    NotificationItem,
    StudentAcademicResults,
    StudentAttendanceSummary,
    StudentFeeDetails,
    TimelineEntry,
    TimelineEntryCreate,
    TimelineEntryUpdate,
    AchievementVerificationRequest,
    ImportHistoryItem,
    TimetableCreateRequest,
    TimetableEntry,
)
from backend.app.services.college_service import college_service
from backend.app.security import (
    get_authenticated_user,
    require_roles,
    check_student_access,
)

router = APIRouter(tags=["College Management"])


# ===========================================================================
# 1. TIMETABLE
# ===========================================================================
@router.get(
    "/timetable",
    response_model=List[TimetableEntry],
    summary="Get timetable schedule with filters",
)
def get_timetable(
    student_id: Optional[str] = None,
    faculty_id: Optional[str] = None,
    day: Optional[str] = None,
    semester: Optional[int] = None,
    current_user: Dict = Depends(get_authenticated_user),
):
    # If student requests, ensure student_id matches their own
    if current_user["role"] == "student" and not student_id:
        student_id = current_user.get("student_id")
    entries = college_service.get_timetable(
        student_id=student_id,
        faculty_id=faculty_id,
        day=day,
        semester=semester,
    )
    return [TimetableEntry(**e) for e in entries]


@router.post(
    "/timetable",
    response_model=TimetableEntry,
    summary="Add class schedule entry with conflict validation",
)
def add_timetable_entry(
    request: TimetableCreateRequest,
    current_user: Dict = Depends(require_roles(["admin"])),
):
    try:
        new_entry = college_service.add_timetable_entry(request.model_dump())
        return TimetableEntry(**new_entry)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(ve),
        )


@router.delete(
    "/timetable/{entry_id}",
    summary="Delete class schedule entry",
)
def delete_timetable_entry(
    entry_id: str,
    current_user: Dict = Depends(require_roles(["admin"])),
):
    success = college_service.delete_timetable_entry(entry_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timetable slot {entry_id} not found",
        )
    return {"status": "success", "message": f"Deleted slot {entry_id}"}


# ===========================================================================
# 2. ATTENDANCE
# ===========================================================================
@router.get(
    "/attendance/student/{student_id}",
    response_model=StudentAttendanceSummary,
    summary="Get subject-wise attendance summary for student",
)
def get_student_attendance(
    student_id: str,
    target_student: Dict = Depends(check_student_access),
):
    res = college_service.get_student_attendance(student_id)
    return StudentAttendanceSummary(**res)


@router.get(
    "/attendance/class",
    summary="Get student roster for class attendance marking",
)
def get_class_attendance_sheet(
    class_id: str = "CS-Sem2",
    subject_code: str = "CS301",
    date: str = "2026-10-09",
    current_user: Dict = Depends(require_roles(["faculty", "admin"])),
):
    sheet = college_service.get_class_attendance_sheet(class_id, subject_code, date)
    return sheet


@router.post(
    "/attendance/submit",
    summary="Submit bulk attendance marks for class session",
)
def submit_attendance(
    request: BulkAttendanceSubmit,
    current_user: Dict = Depends(require_roles(["faculty", "admin"])),
):
    res = college_service.submit_class_attendance(request.model_dump())
    return res


@router.get(
    "/attendance/report",
    response_model=List[AttendanceReportItem],
    summary="Institutional attendance report by department",
)
def get_attendance_reports(
    current_user: Dict = Depends(require_roles(["admin"])),
):
    reports = college_service.get_attendance_reports()
    return [AttendanceReportItem(**r) for r in reports]


# ===========================================================================
# 3. MARKS & RESULTS
# ===========================================================================
@router.get(
    "/marks/student/{student_id}",
    response_model=StudentAcademicResults,
    summary="Get marks, internals, grades and CGPA history for student",
)
def get_student_marks(
    student_id: str,
    target_student: Dict = Depends(check_student_access),
):
    res = college_service.get_student_marks(student_id)
    return StudentAcademicResults(**res)


@router.post(
    "/marks/update",
    summary="Update student marks and recalculate grade",
)
def update_marks(
    request: MarksUpdateRequest,
    current_user: Dict = Depends(require_roles(["faculty", "admin"])),
):
    res = college_service.update_student_marks(request.model_dump())
    return res


# ===========================================================================
# 4. ASSIGNMENTS
# ===========================================================================
@router.get(
    "/assignments",
    response_model=List[AssignmentItem],
    summary="Get assignments list filtered by student or faculty",
)
def list_assignments(
    student_id: Optional[str] = None,
    faculty_id: Optional[str] = None,
    current_user: Dict = Depends(get_authenticated_user),
):
    if current_user["role"] == "student" and not student_id:
        student_id = current_user.get("student_id")
    items = college_service.get_assignments(student_id=student_id, faculty_id=faculty_id)
    return [AssignmentItem(**i) for i in items]


@router.post(
    "/assignments",
    response_model=AssignmentItem,
    summary="Create new assignment for a class",
)
def create_assignment(
    request: AssignmentCreateRequest,
    current_user: Dict = Depends(require_roles(["faculty", "admin"])),
):
    new_asn = college_service.create_assignment(request.model_dump())
    return AssignmentItem(**new_asn)


@router.post(
    "/assignments/{assignment_id}/submit",
    response_model=AssignmentSubmission,
    summary="Submit student work for assignment",
)
def submit_assignment(
    assignment_id: str,
    request: AssignmentSubmitRequest,
    current_user: Dict = Depends(get_authenticated_user),
):
    # Enforce student can only submit for themselves
    if current_user["role"] == "student" and request.student_id != current_user.get("student_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students may only submit assignments for their own account",
        )
    try:
        sub = college_service.submit_assignment(
            assignment_id=assignment_id,
            student_id=request.student_id,
            content=request.content,
            file_name=request.file_name,
        )
        return AssignmentSubmission(**sub)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.post(
    "/assignments/{assignment_id}/grade",
    summary="Grade a student assignment submission",
)
def grade_assignment(
    assignment_id: str,
    student_id: str,
    request: AssignmentGradeRequest,
    current_user: Dict = Depends(require_roles(["faculty", "admin"])),
):
    try:
        graded = college_service.grade_assignment(
            assignment_id=assignment_id,
            student_id=student_id,
            grade=request.grade,
            feedback=request.feedback,
        )
        return graded
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


# ===========================================================================
# 5. ANNOUNCEMENTS
# ===========================================================================
@router.get(
    "/announcements",
    response_model=List[AnnouncementItem],
    summary="List institutional and class announcements",
)
def list_announcements(
    audience: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: Dict = Depends(get_authenticated_user),
):
    items = college_service.get_announcements(audience=audience, user_id=user_id or current_user.get("id"))
    return [AnnouncementItem(**i) for i in items]


@router.post(
    "/announcements",
    response_model=AnnouncementItem,
    summary="Publish new college announcement",
)
def create_announcement(
    request: AnnouncementCreateRequest,
    current_user: Dict = Depends(require_roles(["faculty", "admin"])),
):
    item = college_service.create_announcement(request.model_dump())
    return AnnouncementItem(**item)


@router.post(
    "/announcements/{announcement_id}/read",
    summary="Mark announcement as read by user",
)
def mark_announcement_read(
    announcement_id: str,
    user_id: str,
    current_user: Dict = Depends(get_authenticated_user),
):
    success = college_service.mark_announcement_read(announcement_id, user_id)
    return {"status": "success", "read": success}


@router.delete(
    "/announcements/{announcement_id}",
    summary="Archive or delete announcement",
)
def delete_announcement(
    announcement_id: str,
    current_user: Dict = Depends(require_roles(["admin"])),
):
    success = college_service.delete_announcement(announcement_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
    return {"status": "success", "message": "Announcement deleted"}


# ===========================================================================
# 6. EXAMINATIONS
# ===========================================================================
@router.get(
    "/examinations",
    response_model=List[ExaminationItem],
    summary="Get upcoming examinations schedule",
)
def list_examinations(
    department: Optional[str] = None,
    semester: Optional[int] = None,
    current_user: Dict = Depends(get_authenticated_user),
):
    items = college_service.get_examinations(department=department, semester=semester)
    return [ExaminationItem(**i) for i in items]


@router.post(
    "/examinations",
    response_model=ExaminationItem,
    summary="Schedule new examination",
)
def create_examination(
    request: ExaminationCreateRequest,
    current_user: Dict = Depends(require_roles(["admin"])),
):
    item = college_service.create_examination(request.model_dump())
    return ExaminationItem(**item)


@router.put(
    "/examinations/{exam_id}",
    summary="Update examination venue or publish status",
)
def update_examination(
    exam_id: str,
    updates: Dict[str, Any],
    current_user: Dict = Depends(require_roles(["admin"])),
):
    item = college_service.update_examination(exam_id, updates)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return item


# ===========================================================================
# 7. FEES
# ===========================================================================
@router.get(
    "/fees/student/{student_id}",
    response_model=StudentFeeDetails,
    summary="Get student fee status, outstanding balance and payment history",
)
def get_student_fees(
    student_id: str,
    target_student: Dict = Depends(check_student_access),
):
    fees = college_service.get_student_fees(student_id)
    return StudentFeeDetails(**fees)


@router.post(
    "/fees/pay",
    response_model=StudentFeeDetails,
    summary="Record fee installment payment and issue receipt",
)
def pay_student_fees(
    request: FeePaymentRequest,
    current_user: Dict = Depends(get_authenticated_user),
):
    if current_user["role"] == "student" and request.student_id != current_user.get("student_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students may only pay fees for their own account",
        )
    try:
        updated = college_service.pay_student_fees(
            student_id=request.student_id,
            amount=request.amount,
            method=request.payment_method,
        )
        return StudentFeeDetails(**updated)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get(
    "/fees/summary",
    response_model=InstitutionFeeSummary,
    summary="Institution fee billing and collections summary",
)
def get_fee_summary(
    current_user: Dict = Depends(require_roles(["admin"])),
):
    summary = college_service.get_institution_fee_summary()
    return InstitutionFeeSummary(**summary)


# ===========================================================================
# 8. NOTIFICATIONS & DAILY TIMETABLE NOTIFICATION ENGINE
# ===========================================================================
@router.get(
    "/notifications",
    response_model=List[NotificationItem],
    summary="List in-app notifications for a user",
)
def get_notifications(
    user_id: Optional[str] = None,
    current_user: Dict = Depends(get_authenticated_user),
):
    target_user_id = current_user.get("id", "S1001")
    if current_user["role"] in ["admin"] and user_id:
        target_user_id = user_id
    items = college_service.get_notifications(user_id=target_user_id)
    return [NotificationItem(**i) for i in items]


@router.post(
    "/notifications/{notification_id}/read",
    summary="Mark specific notification as read",
)
def mark_notification_read(
    notification_id: str,
    current_user: Dict = Depends(get_authenticated_user),
):
    success = college_service.mark_notification_read(notification_id)
    return {"status": "success", "read": success}


@router.post(
    "/notifications/read-all",
    summary="Mark all notifications as read for a user",
)
def mark_all_notifications_read(
    user_id: Optional[str] = None,
    current_user: Dict = Depends(get_authenticated_user),
):
    target_user_id = current_user.get("id", "S1001")
    if current_user["role"] in ["admin"] and user_id:
        target_user_id = user_id
    count = college_service.mark_all_notifications_read(target_user_id)
    return {"status": "success", "updated_count": count}


@router.post(
    "/notifications/trigger-daily-schedule",
    response_model=DailyScheduleNotificationResult,
    summary="Trigger daily timetable schedule notification engine",
    description=(
        "Retrieves the day's timetable for students, avoids duplicates for the target date, "
        "respects quiet hours, and delivers concise in-app daily schedule notifications."
    ),
)
def trigger_daily_schedule_notifications(
    target_date: Optional[str] = Query(None, description="Target date YYYY-MM-DD (defaults to today)"),
    check_quiet_hours: bool = Query(False, description="Whether to enforce institutional quiet hours"),
    current_user: Dict = Depends(require_roles(["admin"])),
):
    result = college_service.generate_daily_schedule_notifications(
        target_date=target_date,
        check_quiet_hours=check_quiet_hours,
    )
    return DailyScheduleNotificationResult(**result)


# ===========================================================================
# 9. FACULTY, ADMIN ROSTERS & CSV IMPORT
# ===========================================================================
@router.get(
    "/faculty",
    summary="List all faculty members and assigned subjects",
)
def list_faculty(
    current_user: Dict = Depends(get_authenticated_user),
):
    return college_service.get_faculty_list()


@router.post(
    "/faculty",
    summary="Create or register faculty member",
)
def create_faculty(
    data: Dict[str, Any],
    current_user: Dict = Depends(require_roles(["admin"])),
):
    return college_service.create_faculty(data)


@router.put(
    "/faculty/{faculty_id}",
    summary="Update faculty profile or assignments",
)
def update_faculty(
    faculty_id: str,
    updates: Dict[str, Any],
    current_user: Dict = Depends(require_roles(["admin"])),
):
    res = college_service.update_faculty(faculty_id, updates)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    return res


@router.get(
    "/admin/students",
    response_model=List[AdminStudentItem],
    summary="Admin directory of all registered students",
)
def get_admin_students(
    current_user: Dict = Depends(require_roles(["admin"])),
):
    students = college_service.get_admin_students()
    return [AdminStudentItem(**s) for s in students]


@router.post(
    "/admin/students",
    response_model=AdminStudentItem,
    summary="Enroll new student record",
)
def create_student(
    request: AdminStudentCreate,
    current_user: Dict = Depends(require_roles(["admin"])),
):
    try:
        new_s = college_service.create_student(request.model_dump())
        return AdminStudentItem(**new_s)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.put(
    "/admin/students/{student_id}",
    summary="Update student record or status",
)
def update_student(
    student_id: str,
    updates: Dict[str, Any],
    current_user: Dict = Depends(require_roles(["admin"])),
):
    res = college_service.update_student(student_id, updates)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return res


@router.post(
    "/admin/students/import-csv",
    response_model=CsvImportResult,
    summary="Import batch student records from CSV rows with row-level validation",
)
def import_students_csv(
    rows: List[Dict[str, Any]],
    current_user: Dict = Depends(require_roles(["admin"])),
):
    result = college_service.import_students_csv(rows)
    return CsvImportResult(**result)


@router.get(
    "/admin/audit-logs",
    summary="Retrieve platform administrative audit trail",
)
def get_audit_logs(
    limit: int = 50,
    current_user: Dict = Depends(require_roles(["admin"])),
):
    return college_service.get_audit_logs(limit=limit)


@router.get(
    "/departments",
    summary="List university departments and academic divisions",
)
def list_departments(
    current_user: Dict = Depends(get_authenticated_user),
):
    return college_service.get_departments()


# ---------------------------------------------------------------------------
# Student Education & Career Timeline Routes
# ---------------------------------------------------------------------------
@router.get(
    "/students/{student_id}/timeline",
    response_model=List[TimelineEntry],
    summary="Retrieve student chronological education and career milestones",
)
def get_student_timeline(
    student_id: str,
    category: Optional[str] = Query(None, description="Filter by category (Education, Projects, Hackathons, etc.)"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    status: Optional[str] = Query(None, description="Filter by verification status"),
    current_user: Dict = Depends(check_student_access),
):
    entries = college_service.get_student_timeline(
        student_id=student_id,
        category=category,
        academic_year=academic_year,
        status=status,
    )
    return [TimelineEntry(**e) for e in entries]


@router.post(
    "/students/{student_id}/timeline",
    response_model=TimelineEntry,
    summary="Create a new milestone or achievement entry for student timeline",
)
def create_timeline_entry(
    student_id: str,
    payload: TimelineEntryCreate,
    current_user: Dict = Depends(check_student_access),
):
    entry = college_service.create_timeline_entry(
        student_id=student_id,
        data=payload.model_dump(),
        actor_role=current_user.get("role", "student"),
        actor_id=current_user.get("id", "S1001"),
        actor_name=current_user.get("name", "Student"),
    )
    return TimelineEntry(**entry)


@router.put(
    "/students/{student_id}/timeline/{entry_id}",
    response_model=TimelineEntry,
    summary="Update an existing timeline entry",
)
def update_timeline_entry(
    student_id: str,
    entry_id: str,
    payload: TimelineEntryUpdate,
    current_user: Dict = Depends(check_student_access),
):
    updated = college_service.update_timeline_entry(
        student_id=student_id,
        entry_id=entry_id,
        updates=payload.model_dump(exclude_unset=True),
        actor_role=current_user.get("role", "student"),
        actor_name=current_user.get("name", "Student"),
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline entry {entry_id} not found for student {student_id}",
        )
    return TimelineEntry(**updated)


@router.delete(
    "/students/{student_id}/timeline/{entry_id}",
    summary="Delete a student timeline milestone",
)
def delete_timeline_entry(
    student_id: str,
    entry_id: str,
    current_user: Dict = Depends(check_student_access),
):
    success = college_service.delete_timeline_entry(
        student_id=student_id,
        entry_id=entry_id,
        actor_role=current_user.get("role", "student"),
        actor_name=current_user.get("name", "Student"),
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline entry {entry_id} not found for student {student_id}",
        )
    return {"status": "success", "message": f"Timeline entry {entry_id} deleted successfully"}


# ---------------------------------------------------------------------------
# Achievement Verification Workflow Routes (Faculty & Admin)
# ---------------------------------------------------------------------------
@router.get(
    "/achievements/pending-verification",
    response_model=List[TimelineEntry],
    summary="Retrieve pending student self-reported achievement verification queue",
)
def get_pending_verifications(
    current_user: Dict = Depends(require_roles(["admin", "faculty"])),
):
    faculty_assigned = None
    if current_user.get("role") == "faculty":
        faculty_assigned = current_user.get("assigned_student_ids", [])
    
    pending = college_service.get_pending_verifications(faculty_assigned_students=faculty_assigned)
    return [TimelineEntry(**e) for e in pending]


@router.post(
    "/achievements/{entry_id}/verify",
    response_model=TimelineEntry,
    summary="Review and verify or reject a student achievement submission",
)
def verify_achievement(
    entry_id: str,
    payload: AchievementVerificationRequest,
    current_user: Dict = Depends(require_roles(["admin", "faculty"])),
):
    updated = college_service.verify_achievement(
        entry_id=entry_id,
        status=payload.status,
        reviewer_id=current_user.get("id", "FAC001"),
        reviewer_name=current_user.get("name", "Faculty Reviewer"),
        rejection_reason=payload.rejection_reason,
        remarks=payload.remarks,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Achievement entry {entry_id} not found",
        )
    return TimelineEntry(**updated)


# ---------------------------------------------------------------------------
# Data Import History Route (Admin Only)
# ---------------------------------------------------------------------------
@router.get(
    "/admin/import-history",
    response_model=List[ImportHistoryItem],
    summary="Retrieve history of batch CSV data imports",
)
def get_import_history(
    current_user: Dict = Depends(require_roles(["admin"])),
):
    history = college_service.get_import_history()
    return [ImportHistoryItem(**item) for item in history]


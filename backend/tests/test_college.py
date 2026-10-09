"""backend/tests/test_college.py

Comprehensive tests for College Management endpoints:
- Authentication & profile
- Timetable & conflict detection
- Attendance marking & subject calculations
- Marks & results
- Assignments creation & submissions
- Fees & payment receipts
- Admin rosters & CSV import validation
- Daily schedule notifications & duplicate prevention
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app

client = TestClient(app)
ADMIN_AUTH = {"Authorization": "Bearer student360_jwt_ADM001_test"}



def test_auth_login_student():
    """Verify student login returns token and student profile."""
    res = client.post("/auth/login", json={"username": "student", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["id"] == "S1001"


def test_auth_login_faculty():
    """Verify faculty login returns faculty profile."""
    res = client.post("/auth/login", json={"username": "faculty", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "faculty"
    assert data["user"]["id"] == "FAC-CS101"


def test_auth_login_admin():
    """Verify admin login returns admin profile."""
    res = client.post("/auth/login", json={"username": "admin", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "admin"
    assert data["user"]["id"] == "ADM001"


def test_auth_invalid_credentials():
    """Verify wrong password returns 401."""
    res = client.post("/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401


def test_timetable_listing_and_filtering():
    """Verify timetable listing returns schedule entries."""
    res = client.get("/timetable?day=Monday", headers=ADMIN_AUTH)
    assert res.status_code == 200
    entries = res.json()
    assert isinstance(entries, list)
    assert len(entries) > 0
    assert all(e["day"].lower() == "monday" for e in entries)


def test_timetable_conflict_detection():
    """Verify conflict detection prevents double booking room."""
    # Attempt to book Lecture Hall 301 on Monday at 09:30 (overlaps with TT-101 09:00-10:15)
    conflict_payload = {
        "day": "Monday",
        "subject_code": "CS999",
        "subject_name": "Quantum Computing",
        "faculty_id": "FAC-ENG301",
        "faculty_name": "Dr. Grace Hopper",
        "room": "Lecture Hall 301",
        "start_time": "09:30",
        "end_time": "10:30",
        "semester": 2,
        "department": "Animation & Multimedia Design",
        "class_id": "CS-Sem2",
    }
    res = client.post("/timetable", json=conflict_payload, headers=ADMIN_AUTH)
    assert res.status_code == 409
    assert "already booked" in res.json()["detail"]


def test_student_attendance():
    """Verify student attendance calculates subject percentages and warning status."""
    res = client.get("/attendance/student/S1001", headers=ADMIN_AUTH)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "S1001"
    assert "overall_percentage" in data
    assert "subjects" in data
    assert len(data["subjects"]) > 0


def test_submit_class_attendance():
    """Verify bulk attendance submission updates records."""
    submit_payload = {
        "class_id": "CS-Sem2",
        "subject_code": "CS301",
        "date": "2026-10-09",
        "session": "Morning",
        "faculty_id": "FAC-CS101",
        "records": [
            {"student_id": "S1001", "student_name": "Sarah Connor", "roll_number": "2024-AMD-001", "status": "Present"},
            {"student_id": "S1002", "student_name": "Marcus Wright", "roll_number": "2024-AGR-002", "status": "Absent"},
        ],
    }
    res = client.post("/attendance/submit", json=submit_payload, headers=ADMIN_AUTH)
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_student_marks_and_update():
    """Verify student marks retrieval and updating."""
    res = client.get("/marks/student/S1001", headers=ADMIN_AUTH)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "S1001"
    assert "current_gpa" in data
    assert len(data["subjects"]) > 0

    # Update mark
    update_res = client.post(
        "/marks/update",
        json={"student_id": "S1001", "subject_code": "CS301", "internal_assessment": 35.0},
        headers=ADMIN_AUTH,
    )
    assert update_res.status_code == 200
    assert update_res.json()["internal_assessment"] == 35.0


def test_assignments_lifecycle():
    """Verify assignment creation, submission, and grading."""
    # List
    res = client.get("/assignments?student_id=S1001", headers=ADMIN_AUTH)
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    first_id = items[0]["id"]

    # Submit
    sub_res = client.post(
        f"/assignments/{first_id}/submit",
        json={"student_id": "S1001", "content": "Updated code archive uploaded", "file_name": "code.zip"},
        headers=ADMIN_AUTH,
    )
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "Submitted"

    # Grade
    grade_res = client.post(
        f"/assignments/{first_id}/grade?student_id=S1001",
        json={"grade": 48.0, "feedback": "Excellent data structure performance benchmarks."},
        headers=ADMIN_AUTH,
    )
    assert grade_res.status_code == 200
    assert grade_res.json()["grade"] == 48.0
    assert grade_res.json()["status"] == "Graded"


def test_fees_and_payment():
    """Verify student fees calculation and mock installment payment."""
    res = client.get("/fees/student/S1001", headers=ADMIN_AUTH)
    assert res.status_code == 200
    fee_data = res.json()
    assert fee_data["total_fees"] == 4500.0
    assert fee_data["scholarship_discount"] == 500.0
    initial_paid = fee_data["paid_amount"]
    initial_balance = fee_data["outstanding_balance"]
    assert initial_balance == fee_data["total_fees"] - fee_data["scholarship_discount"] - initial_paid

    # Pay partial installment
    pay_res = client.post(
        "/fees/pay",
        json={"student_id": "S1001", "amount": 500.0, "payment_method": "Online NetBanking (HDFC)"},
        headers=ADMIN_AUTH,
    )
    assert pay_res.status_code == 200
    updated = pay_res.json()
    assert updated["paid_amount"] == initial_paid + 500.0
    assert updated["outstanding_balance"] == max(0.0, initial_balance - 500.0)
    assert updated["status"] in ["Paid", "Partially Paid"]

    # Verify transaction added
    txns = updated["transactions"]
    assert len(txns) >= 2
    assert txns[-1]["amount"] == 500.0
    assert txns[-1]["payment_method"] == "Online NetBanking (HDFC)"


def test_fee_summary_and_defaulters():
    """Verify institutional fee billing and collection summary calculations."""
    summary_res = client.get("/fees/summary", headers=ADMIN_AUTH)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_billed"] > 0
    assert summary["total_collected"] > 0
    assert summary["collection_rate_percent"] >= 0.0
    assert summary["total_students_billed"] >= 10
    assert isinstance(summary["defaulters_count"], int)


def test_fee_invalid_payment():
    """Verify that zero or negative payment amounts are rejected."""
    bad_res = client.post(
        "/fees/pay",
        json={"student_id": "S1001", "amount": -100.0, "payment_method": "UPI"},
        headers=ADMIN_AUTH,
    )
    assert bad_res.status_code == 400



def test_daily_schedule_notifications():
    """Verify daily schedule notification engine creates non-duplicate notifications."""
    trigger_res = client.post("/notifications/trigger-daily-schedule?target_date=2026-10-12", headers=ADMIN_AUTH)
    assert trigger_res.status_code == 200
    result = trigger_res.json()
    assert result["total_students_processed"] >= 10
    assert result["notifications_created"] >= 10

    # Triggering again for same date should skip duplicates!
    trigger_again = client.post("/notifications/trigger-daily-schedule?target_date=2026-10-12", headers=ADMIN_AUTH)
    assert trigger_again.status_code == 200
    again_res = trigger_again.json()
    assert again_res["skipped_duplicates"] >= 10
    assert again_res["notifications_created"] == 0


def test_admin_csv_import():
    """Verify admin CSV import validates rows and rejects invalid ones."""
    rows = [
        {"student_id": "S9901", "name": "John Connor", "department": "Computer Science", "semester": 1},
        {"student_id": "", "name": "Nameless", "department": "Science", "semester": 1},  # Invalid: missing sid
        {"student_id": "S1001", "name": "Duplicate Sarah", "department": "Design", "semester": 2},  # Invalid: duplicate
    ]
    res = client.post("/admin/students/import-csv", json=rows, headers=ADMIN_AUTH)
    assert res.status_code == 200
    data = res.json()
    assert data["accepted_rows"] == 1
    assert data["rejected_rows"] == 2
    assert len(data["errors"]) == 2


def test_student_timeline_and_self_reporting():
    """Verify student can retrieve timeline and submit self-reported achievement."""
    STUDENT_AUTH = {"Authorization": "Bearer student360_jwt_S1001_test"}
    res = client.get("/students/S1001/timeline", headers=STUDENT_AUTH)
    assert res.status_code == 200
    timeline = res.json()
    assert isinstance(timeline, list)
    assert len(timeline) > 0

    # Student submits new milestone
    new_entry = {
        "title": "AWS Certified Cloud Practitioner",
        "category": "Certifications",
        "date": "2026-09-15",
        "academic_year": "2026-2027",
        "organization": "Amazon Web Services",
        "description": "Demonstrated foundational cloud architecture skills.",
        "skills": ["AWS", "Cloud Computing", "Security"],
        "evidence_url": "https://aws.amazon.com/verify/mock-cert-123",
    }
    create_res = client.post("/students/S1001/timeline", json=new_entry, headers=STUDENT_AUTH)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["title"] == "AWS Certified Cloud Practitioner"
    assert created["verification_status"] == "Self-Reported"
    assert created["is_verified"] is False
    assert created["source"] == "student"


def test_faculty_achievement_verification_workflow():
    """Verify faculty can inspect pending achievements and approve/reject them."""
    FACULTY_AUTH = {"Authorization": "Bearer student360_jwt_FAC-CS101_test"}

    # Fetch pending verifications for assigned students
    pending_res = client.get("/achievements/pending-verification", headers=FACULTY_AUTH)
    assert pending_res.status_code == 200
    pending_list = pending_res.json()
    assert isinstance(pending_list, list)

    # Find the newly created milestone or any pending entry
    if len(pending_list) > 0:
        target_entry = pending_list[0]
        entry_id = target_entry["id"]

        # Approve the achievement
        verify_res = client.post(
            f"/achievements/{entry_id}/verify",
            json={"status": "Institution-Verified", "remarks": "Credential verified via AWS Credly badge"},
            headers=FACULTY_AUTH,
        )
        assert verify_res.status_code == 200
        verified_data = verify_res.json()
        assert verified_data["verification_status"] == "Institution-Verified"
        assert verified_data["is_verified"] is True
        assert verified_data["verified_by"] == "FAC-CS101"
        assert verified_data["verified_at"] is not None


def test_admin_import_history():
    """Verify administrator can retrieve the batch import audit history."""
    res = client.get("/admin/import-history", headers=ADMIN_AUTH)
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert "accepted_rows" in history[0]
    assert "filename" in history[0]


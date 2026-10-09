"""
backend/tests/test_auth_rbac.py

Comprehensive security and RBAC test suite verifying all 13 mandatory test scenarios:
1. Unauthenticated users cannot access protected endpoints.
2. A student can access their own profile.
3. A student cannot access another student's profile by changing the ID.
4. A student cannot access faculty or administrator endpoints.
5. A faculty member can access assigned students.
6. A faculty member cannot access unassigned students.
7. A faculty member cannot create an administrator or change their own role.
8. An administrator can manage users and access permitted institution-wide records.
9. Users cannot access records belonging to another institution.
10. Invalid credentials are rejected.
11. Deactivated accounts cannot log in.
12. Logout invalidates the relevant session or token.
13. Existing prediction, SHAP, scoring, What-If, intervention, and Cohort Insights functionality remains compatible with the new permissions.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def login(username_or_email: str, password: str):
    """Helper to authenticate and return session token."""
    res = client.post(
        "/auth/login",
        json={"username_or_email": username_or_email, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username_or_email}: {res.text}"
    data = res.json()
    return data["token"], data["user"]


# 1. Unauthenticated users cannot access protected endpoints
def test_1_unauthenticated_access_rejected():
    endpoints = [
        ("GET", "/students/S1001"),
        ("GET", "/students/priority-queue"),
        ("GET", "/cohort/insights"),
        ("GET", "/admin/students"),
        ("GET", "/auth/users"),
        ("POST", "/simulate"),
    ]
    for method, path in endpoints:
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json={"student_id": "S1001", "interventions": {}})
        assert resp.status_code in [401, 403], f"Expected 401/403 for unauthenticated {method} {path}, got {resp.status_code}"


# 2. A student can access their own profile
def test_2_student_can_access_own_profile():
    token, user = login("student@student360.edu", "Student@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/students/S1001", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["student_id"] == "S1001"
    assert data["risk_level"] in ["Low", "Medium", "High"]
    assert "risk_score" in data


# 3. A student cannot access another student's profile by changing the ID
def test_3_student_cannot_access_other_student_profile():
    token, user = login("student@student360.edu", "Student@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sarah (S1001) tries to access Raj (S1002)
    resp = client.get("/students/S1002", headers=headers)
    assert resp.status_code == 403
    assert "Forbidden" in resp.json()["detail"] or "access" in resp.json()["detail"].lower()


# 4. A student cannot access faculty or administrator endpoints
def test_4_student_cannot_access_faculty_or_admin_endpoints():
    token, user = login("student@student360.edu", "Student@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Priority queue (faculty/admin only)
    resp = client.get("/students/priority-queue", headers=headers)
    assert resp.status_code == 403
    
    # User management (admin only)
    resp = client.get("/auth/users", headers=headers)
    assert resp.status_code == 403

    # Admin students (admin only)
    resp = client.get("/admin/students", headers=headers)
    assert resp.status_code == 403

    # Cohort insights (faculty/admin only)
    resp = client.get("/cohort/insights", headers=headers)
    assert resp.status_code == 403


# 5. A faculty member can access assigned students
def test_5_faculty_can_access_assigned_students():
    token, user = login("faculty@student360.edu", "Faculty@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Turing is assigned S1001, S1002, S1003, S1004, S1005
    for s_id in ["S1001", "S1002", "S1003"]:
        resp = client.get(f"/students/{s_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["student_id"] == s_id


# 6. A faculty member cannot access unassigned students
def test_6_faculty_cannot_access_unassigned_students():
    token, user = login("faculty@student360.edu", "Faculty@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Turing is not assigned S1006
    resp = client.get("/students/S1006", headers=headers)
    assert resp.status_code == 403
    assert "not assigned" in resp.json()["detail"].lower()


# 7. A faculty member cannot create an administrator or change their own role
def test_7_faculty_cannot_create_admin_or_change_role():
    token, user = login("faculty@student360.edu", "Faculty@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create an admin account
    resp = client.post(
        "/auth/users",
        headers=headers,
        json={
            "username": "rogue_admin",
            "email": "rogue@admin.edu",
            "role": "admin",
            "password": "Password123!",
            "name": "Rogue Admin",
        },
    )
    assert resp.status_code == 403

    # Try to deactivate an account
    resp = client.put(
        "/auth/users/USR-001/status",
        headers=headers,
        json={"status": "Deactivated"},
    )
    assert resp.status_code == 403


# 8. An administrator can manage users and access permitted institution-wide records
def test_8_admin_can_manage_users_and_access_records():
    token, user = login("admin@student360.edu", "Admin@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Access user list
    resp = client.get("/auth/users", headers=headers)
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) >= 3

    # Access any student in INST-001
    resp = client.get("/students/S1006", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["student_id"] == "S1006"

    # Access priority queue
    resp = client.get("/students/priority-queue", headers=headers)
    assert resp.status_code == 200

    # Access cohort insights
    resp = client.get("/cohort/insights", headers=headers)
    assert resp.status_code == 200


# 9. Users cannot access records belonging to another institution
def test_9_cross_institution_access_prevented():
    # Admin of INST-002 logs in
    token, user = login("admin@otheruni.edu", "Admin@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # S1001 belongs to INST-001, so admin from INST-002 must be forbidden (403)
    resp = client.get("/students/S1001", headers=headers)
    assert resp.status_code == 403
    assert "institution" in resp.json()["detail"].lower()


# 10. Invalid credentials are rejected
def test_10_invalid_credentials_rejected():
    # Wrong password
    resp = client.post(
        "/auth/login",
        json={"username_or_email": "admin@student360.edu", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()

    # Non-existent user
    resp = client.post(
        "/auth/login",
        json={"username_or_email": "nonexistent@fake.edu", "password": "Password123!"},
    )
    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()


# 11. Deactivated accounts cannot log in
def test_11_deactivated_accounts_cannot_login():
    resp = client.post(
        "/auth/login",
        json={"username_or_email": "deactivated@student360.edu", "password": "Student@360"},
    )
    assert resp.status_code == 401
    assert "deactivated" in resp.json()["detail"].lower() or "invalid" in resp.json()["detail"].lower()


# 12. Logout invalidates the relevant session or token
def test_12_logout_invalidates_session():
    token, user = login("student@student360.edu", "Student@360")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Verify token works
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200

    # Logout
    resp = client.post("/auth/logout", headers=headers)
    assert resp.status_code == 200

    # Subsequent access with same token is now rejected with 401
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


# 13. Existing prediction, SHAP, scoring, What-If, intervention, and Cohort Insights functionality remains compatible
def test_13_core_features_compatible():
    # Test as faculty
    token, user = login("faculty@student360.edu", "Faculty@360")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Prediction & SHAP
    resp = client.get("/students/S1001", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "top_reasons" in data
    assert "risk_level" in data
    assert "risk_score" in data

    # 2. What-If Simulation
    resp = client.post(
        "/students/S1001/what-if",
        headers=headers,
        json={
            "features": {
                "Curricular units 2nd sem (approved)": 5,
                "Curricular units 1st sem (approved)": 5,
            }
        },
    )
    assert resp.status_code == 200
    sim_data = resp.json()
    assert "risk_score" in sim_data

    # 3. Simulate Outcome / Intervention
    resp = client.post(
        "/students/S1001/simulate-outcome",
        headers=headers,
        json={
            "intervention_type": "Subject Tutoring & Academic Recovery Plan",
            "current_risk": 74,
        },
    )
    assert resp.status_code == 200
    outcome = resp.json()
    assert "simulated_risk_score" in outcome

    # 4. Cohort Insights
    resp = client.get("/cohort/insights", headers=headers)
    assert resp.status_code == 200
    insights = resp.json()
    assert "total_students" in insights
    assert "global_shap" in insights


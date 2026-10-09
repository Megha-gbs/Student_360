"""backend/tests/test_e2e_workflow.py

Comprehensive End-to-End integration test covering the complete 10-step Student360 workflow:
1. Health check
2. Priority Queue retrieval with holistic scores
3. Student profile with SHAP explanations & Sem 1 to Sem 2 trajectory
4. Counterfactual What-If simulation
5. Human-in-the-loop intervention review & approval
6. Simulated demonstration outcome
7. Cohort Insights with aggregate risk distribution & global SHAP drivers
8. Student Education & Career Timeline CRUD
9. Multi-dimensional Success Score & Placement Readiness
10. Frozen 36-feature CSV validation & authenticated import
"""

import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.student_service import student_service
from ml.explainability.uci_schema import UCI_ALL_FEATURES

client = TestClient(app)

ADMIN_HEADERS = {"Authorization": "Bearer student360_jwt_ADM001_test"}
STUDENT_HEADERS = {"Authorization": "Bearer student360_jwt_S1001_test"}
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_complete_e2e_workflow():
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # 2. Priority Queue retrieval
    res = client.get("/students?page=1&per_page=10", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    q_data = res.json()
    assert "students" in q_data
    assert len(q_data["students"]) > 0
    s0 = q_data["students"][0]
    assert "risk_score" in s0
    assert "success_score" in s0
    assert "placement_readiness" in s0

    # 3. Student profile with SHAP & Trajectory
    res = client.get("/students/S1001", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    p_data = res.json()
    assert p_data["student_id"] == "S1001"
    assert "top_reasons" in p_data
    assert len(p_data["top_reasons"]) > 0
    assert "trajectory_data" in p_data
    assert p_data["trajectory_data"]["trajectory_type"] == "real_sem1_to_sem2"
    assert len(p_data["trajectory_data"]["points"]) == 2
    assert p_data["trajectory_data"]["points"][0]["semester"] == "Sem 1"
    assert p_data["trajectory_data"]["points"][1]["semester"] == "Sem 2"
    assert "success_score" in p_data
    assert "placement_readiness" in p_data

    # 4. What-If counterfactual simulation
    sim_payload = {
        "student_id": "S1001",
        "changes": {
            "Curricular units 2nd sem (approved)": 5,
            "Curricular units 2nd sem (grade)": 14.0,
        },
    }
    res = client.post("/simulate", json=sim_payload, headers=ADMIN_HEADERS)
    assert res.status_code == 200
    sim_data = res.json()
    assert "original_risk" in sim_data
    assert "simulated_risk" in sim_data
    assert sim_data["simulation_type"] == "model_based_counterfactual"

    # 5. Human-in-the-loop Intervention Review & Approval
    intv_payload = {
        "student_id": "S1001",
        "intervention_type": "Academic Tutoring",
        "parameters": {"frequency": "weekly", "subject": "Math"},
        "notes": "Assigned to mathematics peer tutoring sessions twice weekly",
        "approved": True,
    }
    res = client.post("/intervention", json=intv_payload, headers=ADMIN_HEADERS)
    assert res.status_code == 200
    intv_data = res.json()
    assert intv_data["student_id"] == "S1001"
    assert intv_data["status"] == "approved"
    assert intv_data["human_approved"] is True
    assert len(intv_data["recommended_actions"]) > 0

    # 6. Simulated demonstration outcome
    outcome_payload = {
        "student_id": "S1001",
        "intervention_type": "Academic Tutoring",
        "approved": True,
    }
    res = client.post("/students/S1001/simulate-outcome", json=outcome_payload, headers=ADMIN_HEADERS)
    assert res.status_code == 200
    out_data = res.json()
    assert out_data["status"] == "simulated"
    assert out_data["badge"] == "SIMULATED DEMONSTRATION OUTCOME"
    assert "simulated_risk_score" in out_data

    # 7. Cohort Insights & Global SHAP
    res = client.get("/cohort/insights", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    cohort_data = res.json()
    assert "total_students" in cohort_data
    assert "global_shap" in cohort_data
    assert len(cohort_data["global_shap"]) > 0

    # 8. Student Timeline CRUD & Faculty verification
    tl_payload = {
        "title": "Advisor Mid-Term Check-in",
        "category": "Education",
        "academic_year": "2024-2025",
        "date": "2024-10-15",
        "description": "Reviewed academic progress and recommended tutoring.",
        "skills": ["Academic Planning"],
    }
    res = client.post("/students/S1001/timeline", json=tl_payload, headers=ADMIN_HEADERS)
    assert res.status_code == 200
    tl_event = res.json()
    assert "id" in tl_event

    res = client.get("/students/S1001/timeline", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    events = res.json()
    assert any(e["title"] == "Advisor Mid-Term Check-in" for e in events)

    # 9. Multi-dimensional Success Score and Placement Readiness endpoints
    res = client.get("/students/S1001/success-score", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    ss_data = res.json()
    assert "success_score" in ss_data
    assert "standing_tier" in ss_data
    assert "components" in ss_data

    res = client.get("/students/S1001/placement-readiness", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    pr_data = res.json()
    assert "readiness_score" in pr_data
    assert "readiness_tier" in pr_data
    assert "components" in pr_data

    # 10. CSV Validation and Import
    demo_file = PROJECT_ROOT / "docs" / "DEMO_STUDENTS.json"
    with open(demo_file, "r", encoding="utf-8") as f:
        demo_students = json.load(f)

    headers_list = ["student_id"] + list(UCI_ALL_FEATURES)
    lines = [",".join(headers_list)]
    s = demo_students[0]
    sid = "E2E_FINAL_01"
    row_vals = [sid]
    for feat in UCI_ALL_FEATURES:
        row_vals.append(str(s["features"].get(feat, 0)))
    lines.append(",".join(row_vals))
    csv_text = "\n".join(lines)

    # Validate CSV
    res = client.post(
        "/data/validate-csv?filename=e2e_final.csv&preview_only=true",
        content=csv_text.encode("utf-8"),
        headers={"Content-Type": "text/csv"},
    )
    assert res.status_code == 200
    val_data = res.json()
    assert val_data["is_valid"] is True
    assert val_data["total_rows"] == 1
    assert val_data["accepted_rows"] == 1

    # Import CSV
    res = client.post(
        "/data/import-csv",
        content=csv_text.encode("utf-8"),
        headers={**ADMIN_HEADERS, "Content-Type": "text/csv"},
    )
    assert res.status_code == 200
    imp_data = res.json()
    assert imp_data["is_valid"] is True

    # Verify imported student exists
    res = client.get(f"/students/{sid}", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    assert res.json()["student_id"] == sid

    # Reset test ingestion state
    student_service.reset()

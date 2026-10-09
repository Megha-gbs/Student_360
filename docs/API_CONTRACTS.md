# STUDENT360 — API CONTRACTS SPECIFICATION
**Author / Integration Coordinator:** Meghana  
**Version:** 1.0.0 (Unified Specification)

---

## 1. System & Authentication Endpoints

### 1.1 `GET /health`
- **Description:** Service health check.
- **Access:** Public
- **Response `200 OK`:**
  ```json
  { "status": "ok" }
  ```

### 1.2 `POST /auth/login`
- **Description:** Authenticate user and issue bearer token session.
- **Access:** Public
- **Request Body:**
  ```json
  {
    "username": "faculty",
    "password": "faculty123"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "access_token": "token_faculty_12345678",
    "token_type": "bearer",
    "user": {
      "id": "FAC-CS101",
      "username": "faculty",
      "role": "faculty",
      "name": "Dr. Alan Turing",
      "email": "faculty@student360.edu",
      "department": "Computer Science & Engineering"
    }
  }
  ```

### 1.3 `GET /auth/me`
- **Description:** Get profile and permissions of authenticated caller.
- **Access:** Authenticated (Bearer Token)
- **Response `200 OK`:**
  ```json
  {
    "user_id": "FAC-CS101",
    "role": "faculty",
    "name": "Dr. Alan Turing",
    "email": "faculty@student360.edu",
    "assigned_students": ["S1001", "S1002", "S1003", "S1004", "S1005"]
  }
  ```

---

## 2. ML Core Workflow Endpoints

### 2.1 `GET /students` or `GET /students/priority-queue`
- **Description:** Returns triage priority queue ranked by risk score descending.
- **Access:** Faculty, Administrator
- **Response `200 OK`:**
  ```json
  {
    "total": 10,
    "students": [
      {
        "student_id": "S1001",
        "risk_score": 74.5,
        "risk_level": "High",
        "dropout_probability": 0.745,
        "model_version": "xgboost_v1.0.0",
        "trend": "Stable",
        "priority": "High",
        "course_name": "Informatics Engineering",
        "success_score": 58,
        "placement_readiness": 45
      }
    ]
  }
  ```

### 2.2 `GET /students/{student_id}`
- **Description:** Detailed Student360 profile with dynamic XGBoost inference, top SHAP reasons, Sem 1 → Sem 2 trajectory, and holistic scores.
- **Access:** Enforces RBAC (Student sees own profile only; Faculty sees assigned students; Admin sees all).
- **Response `200 OK`:**
  ```json
  {
    "student_id": "S1001",
    "risk_score": 74.5,
    "risk_level": "High",
    "dropout_probability": 0.745,
    "model_version": "xgboost_v1.0.0",
    "trend": "Stable",
    "shap_reasons": [
      {
        "feature": "Course",
        "value": 171,
        "impact": "high",
        "direction": "increases_risk"
      },
      {
        "feature": "Curricular units 1st sem (grade)",
        "value": 0.0,
        "impact": "high",
        "direction": "increases_risk"
      }
    ],
    "trajectory": {
      "trajectory_type": "real_sem1_to_sem2",
      "points": [
        { "semester": "Sem 1", "risk_score": 71, "approved_units": 0, "grade": 0.0 },
        { "semester": "Sem 2", "risk_score": 74, "approved_units": 0, "grade": 0.0 }
      ],
      "note": "Based on actual 1st vs 2nd semester curricular units from the dataset"
    },
    "success_score": 58,
    "success_tier": "Developing",
    "placement_readiness": 45,
    "placement_tier": "Needs Attention",
    "course_name": "Informatics Engineering"
  }
  ```

### 2.3 `POST /simulate` or `POST /students/{student_id}/what-if`
- **Description:** Counterfactual What-If scenario evaluation against the frozen 36 UCI features.
- **Access:** Authenticated
- **Request Body:**
  ```json
  {
    "student_id": "S1001",
    "original_risk": 74.5,
    "features": {
      "Tuition fees up to date": 1,
      "Debtor": 0,
      "Scholarship holder": 1,
      "Curricular units 2nd sem (approved)": 5,
      "Curricular units 2nd sem (grade)": 13.5
    }
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "student_id": "S1001",
    "original_risk": 74.5,
    "simulated_risk": 32.1,
    "risk_difference": -42.4,
    "original_risk_level": "High",
    "simulated_risk_level": "Low",
    "model_version": "xgboost_v1.0.0",
    "changed_features": {
      "Curricular units 2nd sem (approved)": { "before": 0, "after": 5 },
      "Curricular units 2nd sem (grade)": { "before": 0.0, "after": 13.5 }
    },
    "disclaimer": "Model-based What-If simulation — not a causal guarantee."
  }
  ```

### 2.4 `POST /intervention` or `POST /intervene`
- **Description:** Human-in-the-loop intervention authorization. Requires human advisor sign-off.
- **Access:** Faculty, Administrator
- **Request Body:**
  ```json
  {
    "student_id": "S1001",
    "action_type": "Academic Tutoring & Financial Support Plan",
    "advisor": "Dr. Elena Rostova",
    "notes": "Assigned 1-on-1 peer tutor for unapproved units and scheduled bursar appointment."
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "id": "INT-101",
    "student_id": "S1001",
    "action_type": "Academic Tutoring & Financial Support Plan",
    "advisor": "Dr. Elena Rostova",
    "notes": "Assigned 1-on-1 peer tutor for unapproved units and scheduled bursar appointment.",
    "status": "Authorized by Advisor",
    "timestamp": "2026-10-09T18:00:00Z"
  }
  ```

### 2.5 `POST /students/{student_id}/simulate-outcome`
- **Description:** Projects hypothetical risk reduction post-intervention.
- **Access:** Faculty, Administrator
- **Response `200 OK`:**
  ```json
  {
    "student_id": "S1001",
    "current_risk": 74.5,
    "projected_dropout_risk": 38.0,
    "projected_retention_probability": 0.62,
    "risk_reduction_points": 36.5,
    "demonstration_label": "Simulated demonstration outcome post-intervention; not real student improvement."
  }
  ```

### 2.6 `GET /cohort/insights`
- **Description:** Institutional aggregate metrics and global SHAP drivers across the cohort.
- **Access:** Faculty, Administrator
- **Response `200 OK`:**
  ```json
  {
    "total_students": 10,
    "high_risk_count": 3,
    "medium_risk_count": 4,
    "low_risk_count": 3,
    "average_risk_score": 52.3,
    "global_shap": [
      { "feature": "Curricular units 2nd sem (approved)", "mean_abs_shap": 0.1842 },
      { "feature": "Curricular units 1st sem (approved)", "mean_abs_shap": 0.1510 },
      { "feature": "Tuition fees up to date", "mean_abs_shap": 0.1123 }
    ],
    "by_course": [
      { "course": "Informatics Engineering", "average_risk": 64.2, "count": 4 }
    ]
  }
  ```

---

## 3. Integrated Scoring & CSV Import Endpoints

### 3.1 `POST /scoring/success-score` & `GET /students/{student_id}/success-score`
- **Description:** Evaluates multi-dimensional Student Success Score using provisional institutional weights.
- **Provisional Weights:** Academic (0.35), Attendance (0.25), LMS (0.15), Engagement (0.10), Placement (0.15).
- **Missing Data Policy:** Renormalizes over available component weights. Requires >= 0.35 coverage.
- **Response `200 OK`:**
  ```json
  {
    "student_id": "S1001",
    "status": "calculated",
    "success_score": 58,
    "standing_tier": "Developing",
    "weight_coverage": 0.70,
    "components": {
      "academic": { "score": 42.0, "weight": 0.35, "source": "UCI Curricular Units" },
      "attendance": { "score": 85.0, "weight": 0.25, "source": "Class Attendance" },
      "lms": { "score": null, "weight": 0.15, "source": "Not configured" },
      "engagement": { "score": 60.0, "weight": 0.10, "source": "Clubs/Events" },
      "placement_readiness": { "score": 45.0, "weight": 0.15, "source": "Mock Assessments" }
    },
    "notice": "Provisional institutional formula. Excluded components are dynamically renormalized."
  }
  ```

### 3.2 `POST /data/validate-csv` & `POST /data/import-csv`
- **Description:** Validates uploaded academic/attendance CSV with required column checks, duplicate detection, and row-level error reporting.
- **Request:** `multipart/form-data` file upload.
- **Response `200 OK`:**
  ```json
  {
    "filename": "academic_records_sem1.csv",
    "total_rows": 50,
    "accepted_rows": 48,
    "rejected_rows": 2,
    "is_valid": true,
    "preview_only": true,
    "duplicate_ids": ["S1014"],
    "missing_columns": [],
    "errors": [
      { "row": 12, "student_id": "S1012", "field": "Curricular units 1st sem (grade)", "error": "Value 25.0 exceeds max scale of 20.0" }
    ],
    "message": "CSV validated successfully. 48 rows accepted, 2 rejected."
  }
  ```

---

## 4. Student Timeline Endpoints

### 4.1 `GET /students/{student_id}/timeline`
- **Description:** Chronological education & career timeline.
- **Response `200 OK`:**
  ```json
  [
    {
      "id": "TL-101",
      "student_id": "S1001",
      "category": "Projects",
      "title": "Smart Campus IoT Energy Monitor",
      "academic_year": "2024-2025",
      "date": "2024-11-15",
      "description": "Led a 4-person team building low-power energy monitors.",
      "organization": "Department Hackathon",
      "evidence_url": "https://github.com/campus/iot-monitor",
      "verification_status": "Institution Verified",
      "verified_by": "Dr. Alan Turing"
    }
  ]
  ```

### 4.2 `POST /students/{student_id}/timeline`
- **Description:** Student submits new milestone/achievement. Status set to `Student Submitted` (pending faculty verification).
- **Request Body:**
  ```json
  {
    "category": "Certifications",
    "title": "AWS Certified Cloud Practitioner",
    "academic_year": "2024-2025",
    "date": "2025-01-10",
    "description": "Completed certification examination.",
    "organization": "Amazon Web Services",
    "evidence_url": "https://aws.amazon.com/verify/12345"
  }
  ```

### 4.3 `POST /achievements/{entry_id}/verify`
- **Description:** Faculty reviews evidence link and records approval or rejection.
- **Access:** Faculty, Administrator
- **Request Body:**
  ```json
  {
    "action": "APPROVE",
    "notes": "Verified official credential ID."
  }
  ```

# STUDENT360 — INTEGRATION PLAN
**Author / Integration Coordinator:** Meghana  
**Target Integrated Workspace:** `Student360_Integration/Student360_Final_Integrated/`  
**Foundation Baseline:** Build_2 (Student360_Final)  
**Enhancement Source:** Build_1 (student360)  
**Status:** Pending Approval Gate

---

## 1. Target Integrated Architecture & Folder Layout

The final integrated application will be created at `Student360_Integration/Student360_Final_Integrated/`:

```
Student360_Final_Integrated/
├── backend/
│   ├── app/
│   │   ├── main.py                     # Unified FastAPI entry point with all routers & lifespan
│   │   ├── config.py                   # Centralized configuration & environment variables
│   │   ├── security.py                 # RBAC authentication, session store, password hashing
│   │   ├── schemas.py                  # ML, scoring, CSV validation & core Pydantic schemas
│   │   ├── schemas_college.py          # Institutional college ERP Pydantic schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # User login, logout, profile & permissions
│   │   │   ├── college.py              # College ERP, timeline CRUD, achievement verification
│   │   │   ├── students.py             # Priority queue & student profiles with ML & scoring
│   │   │   ├── simulation.py           # What-If scenario counterfactual predictions
│   │   │   ├── intervention.py         # Human-in-the-loop intervention approval & outcome projection
│   │   │   ├── cohort.py               # Aggregated analytics & global SHAP drivers
│   │   │   ├── scoring.py              # [From Build_1] Student Success Score & Placement Readiness
│   │   │   └── data_import.py          # [From Build_1] CSV validation & import preview
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── college_service.py      # Institutional campus data, timeline, notification engine
│   │       ├── student_service.py      # Demo students repository & dynamic feature retrieval
│   │       ├── model_service.py        # XGBoost inference & artifact caching
│   │       ├── shap_service.py         # Adapter to Smruthi's SHAP explainer
│   │       ├── trajectory_service.py   # Adapter to Smruthi's Sem1->Sem2 trajectory engine
│   │       ├── intervention_service.py # Intervention cases & outcome simulation
│   │       ├── cohort_service.py       # Aggregate metrics calculation
│   │       ├── scoring_service.py      # [From Build_1] Scoring engine adapter
│   │       └── csv_service.py          # [From Build_1] CSV validation engine with row-level error reporting
│   ├── ml/
│   │   ├── __init__.py                 # NumPy 2.x SHAP compatibility shim
│   │   ├── explainability/             # SHAP explainer, schemas, UCI schema validation
│   │   ├── trajectory/                 # Real Sem1 -> Sem2 curricular units trajectory generator
│   │   ├── prediction/                 # Inference with whitespace/tab sanitization
│   │   ├── scoring/                    # Success Score & Placement Readiness rules
│   │   └── training/                   # Model training and preprocessing scripts
│   ├── models/
│   │   ├── xgboost_model_v1.joblib     # Preserved frozen XGBoost model artifact (1.36 MB)
│   │   └── preprocessor.joblib         # Preserved frozen ColumnTransformer artifact (9.0 KB)
│   ├── data/
│   │   └── data.csv                    # Preserved UCI dataset (533 KB)
│   ├── tests/                          # Unified backend & ML test suite (>100 tests)
│   │   ├── test_auth_rbac.py
│   │   ├── test_college.py
│   │   ├── test_cohort.py
│   │   ├── test_end_to_end_integration.py
│   │   ├── test_frontend_integration.py
│   │   ├── test_health.py
│   │   ├── test_intervention.py
│   │   ├── test_model_integration.py
│   │   ├── test_simulation.py
│   │   ├── test_students.py
│   │   ├── test_scoring_api.py         # [From Build_1]
│   │   ├── test_csv_import.py          # [From Build_1]
│   │   ├── test_demo_students.py
│   │   ├── test_model.py
│   │   ├── test_prediction.py
│   │   └── test_preprocessing.py
│   ├── requirements.txt                # Unified Python dependencies
│   ├── .env.example                    # Sanitized backend environment template
│   └── pytest.ini                      # Unified test runner configuration
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── context/
│   │   │   ├── AuthContext.jsx         # User identity, token storage & role management
│   │   │   └── ThemeContext.jsx        # Light/dark mode state
│   │   ├── components/                 # Reusable UI primitives, cards, and ML panels
│   │   │   ├── WhatIfPanel.jsx         # Counterfactual simulation with scientific disclaimer
│   │   │   ├── InterventionPanel.jsx   # Human-in-the-loop advisor approval
│   │   │   ├── OutcomePanel.jsx        # Explicitly labelled simulated outcome
│   │   │   ├── ShapReasons.jsx         # Top contributing SHAP risk factors
│   │   │   ├── RiskTrajectory.jsx      # Sem 1 -> Sem 2 trajectory chart
│   │   │   ├── GlobalShap.jsx          # Cohort-wide SHAP drivers
│   │   │   ├── AppHeader.jsx, AppSidebar.jsx, NotificationCenter.jsx, DashboardLayout.jsx
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── Login.jsx               # Role-based credentials login
│   │   │   ├── PriorityQueue.jsx       # Triage queue with dynamic inference
│   │   │   ├── Student360.jsx          # Unified student profile
│   │   │   ├── CohortInsights.jsx      # Aggregated cohort analytics
│   │   │   ├── admin/                  # 12 Administrative management screens
│   │   │   ├── faculty/                # 9 Faculty course, student & verification screens
│   │   │   └── student/                # 10 Student dashboard, timeline & analytics screens
│   │   ├── services/
│   │   │   └── api.js                  # Unified API client covering all endpoints
│   │   ├── App.jsx                     # Application router with role guards
│   │   ├── main.jsx                    # Root React mounting
│   │   └── index.css                   # Tailwind CSS root stylesheet
│   ├── package.json                    # Frontend dependencies
│   ├── package-lock.json               # Compatible lockfile
│   ├── vite.config.js                  # Vite configuration
│   ├── tailwind.config.js              # Theme color tokens & styling rules
│   └── .env.example                    # Sanitized frontend environment template
├── docs/                               # Integration, methodology, and verification reports
│   ├── INTEGRATION_AUDIT.md
│   ├── FEATURE_COMPARISON.md
│   ├── INTEGRATION_PLAN.md
│   ├── KNOWN_GAPS.md
│   ├── API_CONTRACTS.md
│   ├── MODEL_BASELINE.md
│   ├── MODEL_METHODOLOGY.md
│   └── DEMO_STUDENTS.json
├── scripts/
│   ├── start_backend.ps1               # Automated Windows startup for FastAPI
│   ├── start_frontend.ps1              # Automated Windows startup for Vite
│   └── run_all_tests.ps1               # Complete test verification script
├── .gitignore                          # Clean repository ignores (node_modules, pycache, .env)
└── README.md                           # Comprehensive setup, run, and demo instructions
```

---

## 2. Step-by-Step Execution Sequence

### Stage 1: Baseline Preservation & Project Setup
1. Verify that `Build_1` and `Build_2` remain strictly unmodified.
2. Create the destination directory `Student360_Final_Integrated/`.
3. Copy the complete, tested foundation of `Build_2` into `Student360_Final_Integrated/`.

### Stage 2: Integrate Missing Backend Services & Schemas from Build_1
1. **Pydantic Schemas:**
   - Merge `SuccessScoreRequest`, `SuccessScoreResponse`, `PlacementReadinessRequest`, `PlacementReadinessResponse`, `CSVRowError`, and `CSVValidationResponse` from Build_1 into `backend/app/schemas.py`.
   - Update `StudentResponse` and `StudentListItem` to include optional fields for `success_score`, `success_tier`, `placement_readiness`, and `placement_tier`.
2. **Services Integration:**
   - Copy `backend/app/services/scoring_service.py` and `backend/app/services/csv_service.py` into `backend/app/services/`.
   - Ensure `student_service.py` has `add_students` to allow CSV uploads to update the live registry.
3. **Routes Integration:**
   - Copy `backend/app/routes/scoring.py` and `backend/app/routes/data_import.py` into `backend/app/routes/`.
   - Wire both routers into `backend/app/main.py`.
   - In `backend/app/routes/students.py`, attach `success_score` and `placement_readiness` calculations to student responses while preserving Build_2's RBAC checks.
4. **ML Input Sanitization:**
   - Update `ml/prediction/predict.py` to normalize `Daytime/evening attendance\t` vs `Daytime/evening attendance`.

### Stage 3: NumPy 2.x SHAP Compatibility Shim
- Insert the compatibility shim into `ml/__init__.py` and `backend/app/main.py`:
  ```python
  import numpy as np
  def _obj2sctype(obj):
      try:
          return np.dtype(obj).type
      except TypeError:
          return obj if isinstance(obj, type) and issubclass(obj, np.generic) else None
  if not hasattr(np, "obj2sctype"):
      np.obj2sctype = _obj2sctype
  ```

### Stage 4: Frontend API & UI Wiring
1. In `frontend/src/services/api.js`, add `scoringApi` and `importApi` to complement existing `timelineApi`, `adminApi`, and ML endpoints.
2. In `PriorityQueue.jsx` and `Student360.jsx`, ensure the separate `success_score` and `placement_readiness` badges render alongside the existing XGBoost dropout risk.
3. In `AdminStudents.jsx`, connect the CSV import workflow to `POST /data/validate-csv` and `POST /data/import-csv` with row error preview.

### Stage 5: Unified Testing & Verification
1. Run complete backend test suite (target: >100 tests passing).
2. Run frontend production build (`npm run build`).
3. Execute end-to-end integration smoke script verifying all 10 core workflow steps:
   - Priority Queue → Student360 → SHAP → Trajectory → What-If → Intervention Approval → Simulated Outcome → Cohort Insights → Timeline → CSV Validation.

### Stage 6: Documentation & Windows Startup Scripts
1. Create `README.md` with exact Windows PowerShell setup and run instructions.
2. Add `MODEL_METHODOLOGY.md` documenting the XGBoost model and composite Success Score formula.
3. Provide `.env.example` templates and Windows helper scripts (`scripts/start_backend.ps1`, `scripts/start_frontend.ps1`, `scripts/run_all_tests.ps1`).

# STUDENT360 — FEATURE COMPARISON REPORT
**Author / Integration Coordinator:** Meghana  
**Primary Baseline:** Build_2 (Student360_Final)  
**Secondary / Enhancement Source:** Build_1 (student360)

---

## Evaluation Status Labels
- **Implemented and verified:** Verified in code and tests pass.
- **Implemented but not fully verified:** Code exists, manual or partial automated tests pass.
- **Implemented but failing:** Code exists but fails tests or execution.
- **Partially implemented:** Feature partially coded or missing connecting layer.
- **UI-only or mock-backed:** UI exists without real backend backing.
- **Missing:** Feature absent from codebase.
- **Blocked by credentials or external infrastructure:** External dependency requires credentials.

---

## Feature-by-Feature Comparison Table

| Feature Category | Build_1 (`student360`) | Build_2 (`Student360_Final`) | Recommended Source | Rationale |
|---|---|---|---|---|
| **Priority Queue** | Implemented and verified (`PriorityQueue.jsx`, `GET /students/priority-queue`). Dynamic inference. | Implemented and verified (`PriorityQueue.jsx`). Integrated with `AuthContext`, `ThemeContext`, RBAC. | **Build_2** | Retains full RBAC integration and theme styling; connected to dynamic inference. |
| **Student360 Profile** | Implemented and verified (`Student360.jsx`, `GET /students/{id}`). Real predictions, SHAP, trajectory. | Implemented and verified (`Student360.jsx`). Upgraded layout with theme & role context. | **Build_2** | Stronger UI shell, accurate student routing, connected to backend services. |
| **SHAP Individual Explanation** | Implemented and verified (`ml/explainability/explainer.py`, `ShapReasons.jsx`). | Implemented and verified (`ShapReasons.jsx`). Same ML code, improved dark mode styling. | **Build_2** | Preserves identical ML logic while using Build_2 component styling. |
| **Global SHAP / Cohort Drivers** | Implemented and verified (`GlobalShap.jsx`, `GET /cohort/insights`). | Implemented and verified (`GlobalShap.jsx`). Real cohort calculation, RBAC restricted. | **Build_2** | Preserves aggregate calculation and protects endpoint with RBAC. |
| **Semester Trajectory (Sem1→Sem2)** | Implemented and verified (`ml/trajectory/generator.py`, `RiskTrajectory.jsx`). | Implemented and verified (`RiskTrajectory.jsx`). Strict 2-point trajectory using real curricular units. | **Build_2** | Follows non-fictional trajectory specification using real curricular units. |
| **What-If Simulation** | Implemented and verified (`WhatIfPanel.jsx`, `POST /simulate`). | Implemented and verified (`WhatIfPanel.jsx`). Includes scientific non-causal disclaimer banner. | **Build_2** | Meghana's core workflow: tested, validated against 36 frozen features, clear UI labels. |
| **Intervention Review & Approval** | Implemented and verified (`InterventionPanel.jsx`, `POST /intervention`, `/intervene`). | Implemented and verified (`InterventionPanel.jsx`). Requires human advisor approval before action. | **Build_2** | Meghana's core workflow: Human-in-the-loop review, persistence, advisor directives. |
| **Simulated Outcome Projection** | Implemented and verified (`OutcomePanel.jsx`, `POST /students/{id}/simulate-outcome`). | Implemented and verified (`OutcomePanel.jsx`). Prominent "Simulated demonstration outcome" label. | **Build_2** | Explicitly labels results as simulated rather than actual improvement. |
| **Cohort Insights** | Implemented and verified (`CohortInsights.jsx`, `GET /cohort/insights`). | Implemented and verified (`CohortInsights.jsx`). Recharts visualization, RBAC protected. | **Build_2** | Fully connected to backend response; supports course and risk distributions. |
| **Role-Based Portals (Admin/Faculty/Student)** | Partially implemented (basic role enum in schemas). No separate portals. | Implemented and verified (31 pages & components, backend RBAC in `security.py`, `auth.py`). | **Build_2** | Complete institutional portals for all 3 personas. Build_1 lacked portal UI. |
| **Student Education & Career Timeline** | Missing from Build_1. | Implemented and verified (`StudentTimeline.jsx`, `college.py`, `college_service.py`). | **Build_2** | Supports 8 categories, evidence URLs, status lifecycle (`Student Submitted`, `Institution Verified`). |
| **Faculty Achievement Verification Queue** | Missing from Build_1. | Implemented and verified (`FacultyStudents.jsx`, `GET /achievements/pending-verification`). | **Build_2** | Closes the loop for faculty review and verification of student timeline entries. |
| **Student Success Score Engine** | Implemented and verified (`ml/scoring/success_score.py`, `scoring_service.py`, `scoring.py`). | Partially implemented (`ml/scoring/success_score.py` exists, but not wired to routes). | **Integrate Build_1 into Build_2** | Build_1 has the exact formula `0.35 Academic + 0.25 Attendance + 0.15 LMS + 0.10 Engagement + 0.15 Placement Readiness` with dynamic missing component renormalization. Wire into Build_2. |
| **Placement Readiness Engine** | Implemented and verified (`ml/scoring/placement_readiness.py`, `scoring_service.py`). | Partially implemented (file exists in `ml/scoring/`, but not connected to routes). | **Integrate Build_1 into Build_2** | Build_1 provides full multi-criteria rules-based evaluation and tier assignment. Wire into Build_2. |
| **CSV Import & Row-Level Validation** | Implemented and verified (`backend/app/services/csv_service.py`, `data_import.py`). | Partially implemented (`college_service.py` has basic student import without row error preview). | **Integrate Build_1 into Build_2** | Build_1 provides detailed row-level error breakdown, preview mode, and accepted/rejected counts. |
| **Feature Sanitization (`predict.py`)** | Implemented (`Daytime/evening attendance\t` whitespace handling). | Missing in Build_2 (could fail if trailing tab is stripped by client). | **Integrate Build_1 into Build_2** | Protects the frozen 36 UCI features against tab/whitespace mismatches. |
| **Institutional ERP Modules** | Missing from Build_1. | Implemented and verified (Timetable, Attendance, Marks, Assignments, Exams, Fees, Notifications). | **Build_2** | Provides rich smart campus capabilities for institutional readiness. |
| **NumPy 2.x SHAP Compatibility** | Missing (fails test collection without shim). | Missing (fails test collection without shim). | **Antigravity Fix** | Add lightweight SHAP compatibility shim to ensure reliable execution in modern Python. |

---

## Summary of Integration Selection
1. **Retain as Foundation:** Entire **Build_2** architecture, frontend pages, components, routers (`auth`, `college`, `students`, `simulation`, `intervention`, `cohort`), services, test suite, and ML artifacts.
2. **Cherry-Pick from Build_1:**
   - Multi-dimensional **Student Success Score** and **Placement Readiness** routes and service adapter.
   - Comprehensive **CSV Import Validation** service (`csv_service.py` and `data_import.py`) with preview mode and row-level errors.
   - Input sanitization logic in `predict.py`.
   - Comprehensive test files (`test_csv_import.py`, `test_scoring_api.py`, `test_scoring.py`, `test_explainability.py`, `test_trajectory.py`).

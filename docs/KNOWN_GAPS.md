# STUDENT360 — KNOWN GAPS & DEFECTS AUDIT
**Author / Integration Coordinator:** Meghana  
**Status:** Audit Findings

---

## 1. Confirmed Defects & Technical Blockers

### Defect 1: NumPy 2.x Compatibility Failure with SHAP
- **Severity:** High (Crash / Blocker on modern environments)
- **Component:** `ml/explainability/explainer.py` via `shap.plots.colors._colorconv.py`
- **Root Cause:** NumPy 2.0 removed `np.obj2sctype`. When `shap 0.45.1` is imported under NumPy >= 2.0, an `AttributeError` is thrown, halting test collection and API startup.
- **Fix:** Add a lightweight monkeypatch shim:
  ```python
  import numpy as np
  if not hasattr(np, "obj2sctype"):
      def _obj2sctype(obj):
          try:
              return np.dtype(obj).type
          except TypeError:
              return obj if isinstance(obj, type) and issubclass(obj, np.generic) else None
      np.obj2sctype = _obj2sctype
  ```
  Apply in `ml/__init__.py`, `conftest.py`, and `backend/app/main.py`.

### Defect 2: Feature Name Whitespace Discrepancy in `predict.py`
- **Severity:** Medium (Potential inference crash on raw client payload)
- **Component:** `ml/prediction/predict.py`
- **Root Cause:** The original UCI dataset feature is named `"Daytime/evening attendance\t"` with a literal trailing tab character. If a frontend client passes `"Daytime/evening attendance"` without the tab, validation in Build_2 rejects the input with an unexpected feature error.
- **Fix:** Port Build_1's normalization logic into `predict.py` to transparently map `"Daytime/evening attendance"` to `"Daytime/evening attendance\t"`.

### Defect 3: Disconnected Scoring Engine in Build_2
- **Severity:** Medium (Requirements Gap)
- **Component:** `backend/app/routes/students.py` & `main.py`
- **Root Cause:** Build_2 contains `ml/scoring/success_score.py` and `placement_readiness.py`, but commented out or excluded the API routes (`/scoring/*`) and student response fields (`success_score`, `placement_readiness`).
- **Fix:** Integrate Build_1's `scoring_service.py` and `scoring.py` router into Build_2.

### Defect 4: Simplified CSV Import in Build_2
- **Severity:** Medium (Requirements Gap)
- **Component:** `backend/app/routes/college.py` (`/admin/students/import-csv`)
- **Root Cause:** Build_2's student CSV import accepts simple text lines but does not provide a preview endpoint, required-column schema validation, or row-level error reasons.
- **Fix:** Integrate Build_1's `csv_service.py` and `data_import.py` router (`/data/validate-csv`, `/data/import-csv`) to deliver full preview, duplicate detection, and row-level error reporting.

---

## 2. External Services & Credential Dependencies

| Service / Integration | Status | Credential Required | Fallback / Production Recommendation |
|---|---|---|---|
| **LinkedIn Integration** | Manual URL entry | None required for MVP | LinkedIn API requires approved Developer Partner scopes. Scraping is strictly prohibited by terms of service. Students paste their profile URL and manually record achievements. |
| **GitHub Integration** | Public URL entry | Optional Personal Access Token | Public profiles and repository links are recorded. Live activity fetching is supplementary and rate-limited. |
| **LeetCode Integration** | Manual URL entry | None | LeetCode has no official public OAuth API. Records are student-submitted with proof URLs. |
| **AI LLM Intervention Drafting** | Deterministic fallback | Optional (`OPENAI_API_KEY` or `GEMINI_API_KEY`) | The application uses deterministic, rules-based clinical templates when external LLM keys are unset, ensuring the complete workflow operates without external blockers. |
| **Database Persistence** | In-memory + JSON | None required for demo | PostgreSQL with SQLAlchemy and Alembic is documented for production enterprise deployment. The demo uses in-memory thread-safe state to allow instant setup on any clean workstation. |

---

## 3. Deliberately Deferred Scope (Out of Scope for Hackathon MVP)

To preserve reliability and focus on the core connected workflow, the following complex enterprise integrations are explicitly deferred:
1. **Live Scraping of Third-Party Profiles:** Strictly avoided due to privacy and platform terms of service.
2. **Direct LMS/SIS Database Connectors:** Live Moodle/Banner connectors are deferred in favor of the validated CSV import workflow.
3. **Enterprise Keycloak / OIDC:** In-memory secure RBAC session authentication is used instead of heavyweight external SSO infrastructure.
4. **Celery / Redis / Kafka / Kubernetes:** All background operations use native FastAPI tasks to ensure simple, single-command Windows execution.

# Student360 ML & Scoring Methodology

## 1. Executive Summary & Objective

Student360 is an enterprise educational analytics platform providing actionable, interpretable, and scientifically grounded insights to higher-education faculty, administrators, and students. The platform synthesizes machine learning risk classification with multi-dimensional academic/career readiness scoring while strictly preserving scientific integrity.

---

## 2. Machine Learning Architecture

### 2.1 Frozen 36 UCI Feature Schema
The ML pipeline operates on the canonical 36-feature dataset derived from the Higher Education Students dataset (UCI Machine Learning Repository):
- **Demographics:** Marital status, Nationality, Displaced, Educational special needs, Debtor, Tuition fees up to date, Gender, Scholarship holder, Age at enrollment, International.
- **Socioeconomic:** Mother's qualification, Father's qualification, Mother's occupation, Father's occupation.
- **Prior Academic:** Application mode, Application order, Course, Daytime/evening attendance, Previous qualification, Previous qualification (grade), Admission grade.
- **Academic Progression (Semesters 1 & 2):**
  - Curricular units 1st sem (credited, enrolled, evaluations, approved, grade, without evaluations)
  - Curricular units 2nd sem (credited, enrolled, evaluations, approved, grade, without evaluations)
- **Macroeconomic:** Unemployment rate, Inflation rate, GDP.

> **Zero Target Leakage:** The target variable (`Target`) is strictly excluded from feature inputs. The prediction pipeline raises a validation error if target fields are present.

### 2.2 Model Artifacts & Determinism
- **Classifier:** `xgboost_model_v1.joblib` (1.36 MB, XGBClassifier with 100 estimators, max depth 6).
- **Preprocessor:** `preprocessor.joblib` (9.0 KB, ColumnTransformer with standard scaling for continuous features and one-hot encoding for categorical variables).
- **Inference Guarantee:** Models are cached as immutable singletons upon startup (`test_artifact_caching_and_zero_retraining`). Zero dynamic retraining occurs during request cycles, guaranteeing sub-50ms deterministic inference.

### 2.3 Risk Calibration & Threshold Logic
The model predicts class probabilities for student retention and attrition:
- **Class 0:** Dropout / At-Risk
- **Class 1:** Enrolled / Intermediate
- **Class 2:** Graduate / Thriving

The Dropout Probability ($P(\text{Dropout})$) is mapped to an intuitive 0–100 integer Risk Score:
$$\text{Risk Score} = \text{round}(P(\text{Dropout}) \times 100)$$

**Risk Tier Cutoffs:**
- **High Risk:** Risk Score $\ge 70$ (Urgent intervention recommended)
- **Medium Risk:** $30 \le \text{Risk Score} < 70$ (Proactive monitoring recommended)
- **Low Risk:** Risk Score $< 30$ (Normal academic progression)

---

## 3. Explainability & Trajectory Analysis

### 3.1 Local and Global SHAP (SHapley Additive exPlanations)
- **Local Attribution:** Per-student feature importance is computed using TreeSHAP on the calibrated booster model. For every individual prediction, positive drivers (factors elevating risk) and protective factors (factors mitigating risk) are extracted and ordered by absolute magnitude.
- **Global Importance:** Aggregate cohort analytics (`GET /cohort/insights`) compute mean absolute SHAP values across all verified student records to identify institutional-wide retention barriers.
- **NumPy 2.x Compatibility:** Transparent runtime compatibility shim preserves native tree explainer and linear fallback routines without deprecated scalar types.

### 3.2 Real Semester Trajectory
- Rather than synthesizing fictional weekly time-series, Student360 maps the actual progression from **Semester 1 to Semester 2** based on real curricular units:
  - Unit approval delta: $\Delta \text{Approved} = \text{Approved}_{sem2} - \text{Approved}_{sem1}$
  - Grade delta: $\Delta \text{Grade} = \text{Grade}_{sem2} - \text{Grade}_{sem1}$
  - Trend direction: Categorized as `improving`, `declining`, or `stable`.

---

## 4. Holistic Success Score & Placement Readiness

To avoid reductionist single-metric risk views, Student360 complements ML risk classification with composite scoring modules:

### 4.1 Holistic Success Score
Synthesizes 5 key institutional pillars:
1. **Academic Performance (35% default):** Normalization of curricular unit grades and credit completion.
2. **Attendance Rate (25% default):** Class attendance percentage.
3. **LMS Engagement (15% default):** Virtual learning environment participation and submissions.
4. **Campus Engagement (10% default):** Extracurricular, clubs, and institutional events.
5. **Placement Readiness (15% default):** Career and pre-placement competency.

**Standing Tiers:**
- $\ge 85$: Exemplary
- $70 - 84$: Good Standing
- $50 - 69$: Developing
- $< 50$: At Risk

### 4.2 Placement Readiness Index
Evaluates graduation and employability indicators across 4 core competencies:
1. **Aptitude (25% default)**
2. **Coding Assessment (30% default)**
3. **Mock Interviews (25% default)**
4. **Technical Skills (20% default)**

**Readiness Tiers:**
- $\ge 75$: High
- $50 - 74$: Moderate
- $< 50$: Needs Attention

**Partial Weight Renormalization:** When certain optional indicators are not yet recorded for early-semester students, weights are dynamically renormalized across available data to avoid penalizing students for unadministered assessments.

---

## 5. Counterfactual What-If Simulation & Scientific Disclaimers

### 5.1 What-If Analysis
Users can modify student feature parameters (e.g., simulating 2 additional approved units in Semester 2) to evaluate model sensitivity.

### 5.2 Scientific Honesty Disclaimers
1. **Association vs. Causation:** What-If simulations are strictly **model-based counterfactual evaluations**. They represent model sensitivity to altered feature inputs and do **not** claim causal guarantees or invent automatic intervention outcomes.
2. **Simulated Demonstration Outcome Badge:** Any post-intervention simulated projection carries an explicit **`SIMULATED DEMONSTRATION OUTCOME`** badge and disclaimer notice across both API responses and UI presentation.
3. **Human-in-the-Loop Governance:** AI suggestions for tutoring or counseling remain in `drafted` status until explicitly reviewed, modified, and authorized by a faculty advisor or administrator.

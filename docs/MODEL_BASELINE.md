# STUDENT360 — MACHINE LEARNING BASELINE AUDIT
**Author / Integration Coordinator:** Meghana  
**Status:** Verified ML Foundation

---

## 1. Preserved Model Artifacts

Both `Build_1` and `Build_2` contain identical pre-trained model artifacts:

| Artifact | Filepath | Size | Type / Description |
|---|---|---|---|
| **XGBoost Model** | `models/xgboost_model_v1.joblib` | 1,363,287 bytes (1.30 MB) | `xgboost.sklearn.XGBClassifier` (Multi-class: 0 Dropout, 1 Enrolled, 2 Graduate) |
| **Preprocessor** | `models/preprocessor.joblib` | 9,019 bytes (8.8 KB) | `sklearn.compose.ColumnTransformer` (One-hot encoder + StandardScaler, maps 36 raw features to 233 transformed features) |
| **UCI Source Dataset** | `data/data.csv` | 533,230 bytes (520 KB) | 4,424 student records with 36 original features and 1 target column |
| **Verified Demo Students** | `docs/DEMO_STUDENTS.json` | 17,160 bytes | 10 verified student records covering diverse risk tiers and academic disciplines |

---

## 2. Frozen 36-Feature Schema & Order

The model input schema is strictly frozen to the 36 UCI features. No newly added campus fields (such as attendance, extracurriculars, or career timeline items) are ever fed into this model.

### Exact Feature Names (in preprocessing order):
1. `Marital status`
2. `Application mode`
3. `Application order`
4. `Course`
5. `Daytime/evening attendance\t` *(Special note: contains trailing tab in dataset)*
6. `Previous qualification`
7. `Previous qualification (grade)`
8. `Nacionality`
9. `Mother's qualification`
10. `Father's qualification`
11. `Mother's occupation`
12. `Father's occupation`
13. `Admission grade`
14. `Displaced`
15. `Educational special needs`
16. `Debtor`
17. `Tuition fees up to date`
18. `Gender`
19. `Scholarship holder`
20. `Age at enrollment`
21. `International`
22. `Curricular units 1st sem (credited)`
23. `Curricular units 1st sem (enrolled)`
24. `Curricular units 1st sem (evaluations)`
25. `Curricular units 1st sem (approved)`
26. `Curricular units 1st sem (grade)`
27. `Curricular units 1st sem (without evaluations)`
28. `Curricular units 2nd sem (credited)`
29. `Curricular units 2nd sem (enrolled)`
30. `Curricular units 2nd sem (evaluations)`
31. `Curricular units 2nd sem (approved)`
32. `Curricular units 2nd sem (grade)`
33. `Curricular units 2nd sem (without evaluations)`
34. `Unemployment rate`
35. `Inflation rate`
36. `GDP`

---

## 3. Target Class Mapping & Risk Score Semantics

### Target Encoding:
- **`0` = Dropout** (Primary positive class for early warning risk)
- **`1` = Enrolled**
- **`2` = Graduate**

### Risk Score Calculation:
- **`dropout_probability`:** Raw predicted probability for Class 0 (`model.predict_proba(X)[0][0]`).
- **`risk_score`:** Scaled integer representation: `round(dropout_probability * 100, 1)`.
- **`risk_level` Thresholds:**
  - `High`: Risk Score >= 65.0 (or dropout probability >= 0.65)
  - `Medium`: 35.0 <= Risk Score < 65.0
  - `Low`: Risk Score < 35.0

---

## 4. Documented Baseline Metrics vs. Audit Verification

### Reported Baseline Metrics (from `docs/MODEL_EVALUATION.md`):
- **Accuracy:** 80.27%
- **Dropout Class F1-Score:** 81.46%
- **Macro ROC-AUC:** 91.46%
- **Test Set Evaluation:** Evaluated on held-out test split of the 4,424 UCI records.

### Audit Test Execution:
We executed inference on the 10 verified demo students in both `Build_1` and `Build_2`:
- **Student S1001 (High Risk Benchmark):**
  - Predicted Class: `0` (Dropout)
  - Probabilities: `[0.7449, 0.0614, 0.1937]`
  - Risk Score: `74.5 / 100` (High)
  - Trend: `Stable` (Sem 1 Risk: 71, Sem 2 Risk: 74)
- **Zero Retraining Verified:** Inference runs in < 2ms without re-fitting or retraining.
- **Artifact Immutability:** Hash and byte comparison confirmed identical model weights across both builds.

---

## 5. Explainability & Trajectory Contracts

### 5.1 SHAP Explanations:
- Derived dynamically using `ml/explainability/explainer.py`.
- Generates top 3–5 contributing factors for the selected student, indicating:
  - Feature name and current value
  - Impact level (`high`, `medium`, `low`)
  - Direction of impact (`increases_risk` vs `reduces_risk`)
- Handled gracefully with fallback approximation when multi-class string base scores are encountered in modern XGBoost/SHAP environments.

### 5.2 Real Sem 1 → Sem 2 Trajectory:
- Derived strictly from real curricular units:
  - `Curricular units 1st sem (approved)` & `Curricular units 1st sem (grade)`
  - `Curricular units 2nd sem (approved)` & `Curricular units 2nd sem (grade)`
- Strictly adheres to non-fictional policy: No fabricated weekly or synthetic intermediary points.
- Trajectory Trend definition:
  - `Deteriorating`: Sem 2 risk >= Sem 1 risk + 5 points
  - `Improving`: Sem 2 risk <= Sem 1 risk - 5 points
  - `Stable`: Risk change within +/- 5 points

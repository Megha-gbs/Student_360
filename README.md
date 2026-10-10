# Student360
Student360 is an AI-powered student analytics platform for KPMG HacXLerate 2026. It uses predictive analytics and explainable AI to identify at-risk students, analyze academic performance, and provide actionable insights through role-based dashboards, enabling timely interventions and improved student success.

---

## 🎯 Purpose & Problem Statement

Higher education institutions face persistent challenges in retaining at-risk students before academic difficulties become irreversible. Conventional institutional reporting is largely retroactive—identifying student struggles only after course failure or semester withdrawal occurs.

**Student360** transforms student support from reactive remediation into proactive, science-backed retention. Built for **KPMG HacXLerate 2026**, the platform combines predictive machine learning, localized TreeSHAP explainability, counterfactual what-if simulations, and role-based institutional management into a unified command center. 

Crucially, Student360 enforces a strict **Human-in-the-Loop** operating model: predictive models serve solely as advisory decision support, ensuring that academic advisors and faculty retain full oversight and approval authority over all interventions.

---

## 🔑 Key Features

### 1. Risk Analytics & Triage
- **Priority Queue**: Triages the entire student cohort by real-time dropout probability with multi-tiered risk filtering (High, Medium, Low) and server-side search.
- **Student 360 Holistic Profile**: Centralizes demographic indicators, fee payment standing, academic progress, and historical trajectories.
- **Multi-Class Outcome Forecasting**: Estimates probabilities across three discrete student outcomes (`Dropout`, `Enrolled`, `Graduate`).

### 2. Explainable AI & Counterfactual Simulation
- **Localized SHAP Attributions**: Computes per-student feature impacts using TreeSHAP, isolating the specific institutional, financial, and academic drivers that elevate or reduce risk.
- **What-If Counterfactual Simulator**: Allows advisors to simulate academic interventions (e.g., passing retake units or grade improvements) and visualize projected risk trajectory deltas prior to prescribing actions.
- **Global Cohort Feature Importance**: Identifies macro retention trends across degree programs and academic terms.

### 3. Human-in-the-Loop Intervention Management
- **Advisory Decision Support**: Automatically drafts personalized intervention plans (e.g., peer tutoring, bursar payment plans, faculty mentoring).
- **Mandatory Advisor Approval**: Interventions remain in a `Pending Human Approval` state until verified and authorized by an institutional advisor.
- **Simulated Demonstration Outcome Projections**: Projects potential recovery paths while transparently labeling simulated demonstration indicators.

### 4. Enterprise College Operations
- **Role-Based Portals**: Tailored interfaces for Administrators, Faculty Members, and Students.
- **Academic Operations**: Integrated modules for class timetables, attendance tracking, internal examination schedules, assignment submissions, marks management, and institutional announcements.
- **Audit Logging**: Tracks administrative operations, student status modifications, and CSV cohort data imports.

---

## 👥 Role-Based Dashboards

| Role | Primary Capabilities & Workflows |
| :--- | :--- |
| **Institutional Admin** | System-wide retention metrics, department overviews, batch CSV student enrollment import, fee tracking, user role management, and audit log monitoring. |
| **Faculty Member** | Course-level student queues, class attendance recording, assignment creation and grading, marks updates, timetable access, and localized student risk alerts. |
| **Student** | Personal risk status overview, academic trajectory charts, timetable schedule, attendance percentages, upcoming examinations, fee payment status, and institutional announcements. |

---

## 🧠 Machine Learning & Explainability Pipeline

Student360 leverages a production-grade machine learning architecture trained and evaluated on the validated UCI Student Performance & Dropout dataset.

### Pipeline Architecture
```
┌─────────────────────────┐
│     UCI Cohort Data     │ (4,424 Records, 36 Baseline Features)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Preprocessing Pipeline  │ (StandardScaler, OneHotEncoder, Mean Imputer)
│ models/preprocessor.joblib│ Fitted strictly on 70% Training Split
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   XGBoost Classifier    │ (Version: student360_xgb_v2_real_features)
│ models/xgboost_model_v1 │ Multi-class Softprob (Dropout, Enrolled, Graduate)
└────────────┬────────────┘
             │
     ┌───────┴───────┐
     ▼               ▼
┌───────────┐ ┌───────────┐
│ Real-Time │ │  TreeSHAP │ Local & Global Feature Attribution
│ Risk Prob │ │ Explainer │ (Mean |SHAP| Impact Scoring)
└───────────┘ └───────────┘
```

### Verified Model Performance

Evaluated on held-out test data (`N=664`) partitioned with stratified splitting (Seed 42):

| Metric | Training Split (`N=3096`) | Validation Split (`N=664`) | Held-out Test Split (`N=664`) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 89.18% | 75.75% | **80.27%** |
| **ROC-AUC (OvR Macro)** | 97.23% | 88.37% | **91.46%** |
| **ROC-AUC (OvR Weighted)** | 97.47% | 88.80% | **92.20%** |
| **Dropout Precision** | 89.37% | 71.93% | **85.20%** |
| **Dropout Recall** | 84.14% | 67.75% | **78.04%** |
| **Dropout F1-Score** | 86.23% | 68.96% | **81.46%** |

### Top Risk Attribution Drivers (SHAP)
1. **Curricular units 2nd semester (approved)**: Strongest indicator of academic momentum.
2. **Curricular units 1st semester (approved)**: Early academic baseline indicator.
3. **Tuition fees up to date**: Major non-academic retention threshold.
4. **Curricular units 2nd semester (grade)**: Academic quality score.
5. **Debtor status & Scholarship status**: Financial stability flags.
6. **Age at enrollment**: Non-traditional student transition risk factor.

---

## 📈 Semester Trajectory & What-If Simulation

### Semester-over-Semester Trajectory
Unlike synthetic time-series generators, Student360 maps historical trajectories strictly from real curricular records:
- **Semester 1**: Enrolled units, approved units, average evaluation grades.
- **Semester 2**: Longitudinal progression demonstrating improvement, stagnation, or decline.

### Counterfactual What-If Analysis
Advisors can test hypothetical academic scenarios to determine viable recovery pathways:
- Adjust second-semester units passed (0 to 6).
- Adjust grade expectations (0.0 to 20.0 scale).
- Recalculate model inference dynamically with baseline delta comparison.

---

## 💻 Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+, verified on Python 3.13)
- **ASGI Server**: Uvicorn
- **Machine Learning**: XGBoost (`xgboost 3.4.1`), Scikit-Learn (`scikit-learn 1.4.2`), Joblib
- **Explainability**: SHAP (`shap 0.44.1`)
- **Data Processing**: Pandas, NumPy
- **Validation**: Pydantic v2

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **Data Visualization**: Recharts
- **HTTP Client**: Axios with Bearer token interceptor
- **Routing**: React Router v6

---

## 📊 Dataset & Responsible AI Governance

### Dataset Reference
- **Source**: UCI Machine Learning Repository — *Predict Students' Dropout and Academic Success*
- **Size**: 4,424 student records across 17 undergraduate degree programs
- **Features**: 36 demographic, socio-economic, and academic baseline features

### Responsible AI & Ethical Safeguards
1. **Advisory Decision Support**: AI outputs are strictly informative. The platform does not take automated disciplinary, enrollment, or financial actions.
2. **Human Oversight**: Every intervention requires explicit human review and authorization by certified advisors or faculty.
3. **Transparent Explanations**: Every prediction is accompanied by verifiable SHAP feature attributions so educators understand the "why" behind risk scores.
4. **Data Integrity & Labeling**: Demonstration records, matched features, and synthetic counterfactual outcomes are explicitly labeled in the interface.

---

## 🚀 Installation & Local Setup

### Prerequisites
- **Python**: Version 3.10 or higher
- **Node.js**: Version 18 or higher (Node.js 20+ recommended)
- **Git**

### 1. Clone & Navigate to Project
```bash
git clone <repository-url>
cd Student360-main
```

### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
# (or pip install -r requirements.txt)

# Start FastAPI server
python -m uvicorn backend.app.main:app --port 8000 --host 127.0.0.1 --reload
```
*The backend API will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install node dependencies
npm install

# Start development server
npm run dev
```
*The frontend application will be live at `http://localhost:5173`.*

### 4. Production Build Verification
To validate production compilation:
```bash
cd frontend
npm run build
```

---

## 🔐 Evaluation Accounts & Demonstration Credentials

For testing and hackathon evaluation, pre-configured role-based credentials are provided on the login interface:

| Role | Username / Identifier | Email | Password |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin@student360.edu` | `password123` |
| **Faculty** | `faculty` | `faculty@student360.edu` | `password123` |
| **Student** | `student` *(or `s1001`)* | `student@student360.edu` | `password123` |

*The login interface includes an interactive 1-click autofill card to streamline evaluator testing.*

---

## 🌐 Deployments & Project Links

- **Live Application Frontend**: [https://student360-plum.vercel.app](https://student360-plum.vercel.app)
- **Live Backend API**: [https://student360-gy0b.onrender.com](https://student360-gy0b.onrender.com)
- **API Health Check**: `https://student360-gy0b.onrender.com/health`

---

## 👥 Team & Acknowledgments

- **Hackathon**: KPMG HacXLerate 2026
- **Project**: Student360
- **Development & Integration**: Meghana (Integration Lead) & Team Student360
- **Data Source**: UCI Machine Learning Repository

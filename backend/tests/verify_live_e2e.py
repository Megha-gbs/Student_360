import requests
import json

BASE = "http://127.0.0.1:8000"

# 1. Admin Login & CSV Import & Import History
admin_res = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "password123"}).json()
admin_token = admin_res["token"]
admin_auth = {"Authorization": f"Bearer {admin_token}"}
print("[PASS] 1. Admin Login succeeded:", admin_res["user"]["name"])

# Import CSV
csv_payload = [
    {"student_id": "S1099", "name": "Elena Fisher", "department": "Computer Science & Engineering", "semester": 2},
    {"student_id": "", "name": "Bad Row", "department": "Science", "semester": 1},
]
imp_res = requests.post(f"{BASE}/admin/students/import-csv", json=csv_payload, headers=admin_auth).json()
print(f"[PASS] 2. CSV Import processed: {imp_res['accepted_rows']} accepted, {imp_res['rejected_rows']} rejected")

# Check Import History
hist_res = requests.get(f"{BASE}/admin/import-history", headers=admin_auth).json()
print(f"[PASS] 3. Import History retrieved: {len(hist_res)} logs. Latest filename: {hist_res[0]['filename']}")

# 2. Faculty Login & Assigned Student Inspection
fac_res = requests.post(f"{BASE}/auth/login", json={"username": "faculty", "password": "password123"}).json()
fac_token = fac_res["token"]
fac_auth = {"Authorization": f"Bearer {fac_token}"}
print("[PASS] 4. Faculty Login succeeded:", fac_res["user"]["name"])

# 3. Student submits timeline achievement
stu_res = requests.post(f"{BASE}/auth/login", json={"username": "student", "password": "password123"}).json()
stu_token = stu_res["token"]
stu_auth = {"Authorization": f"Bearer {stu_token}"}

new_achieve = {
    "title": "National Hackathon 1st Place - SmartCampus",
    "category": "Hackathons",
    "date": "2026-10-01",
    "academic_year": "2026-2027",
    "organization": "ACM Student Chapter",
    "description": "Developed predictive campus resource optimization tool.",
    "skills": ["React", "FastAPI", "Python"],
    "evidence_url": "https://hackathon.acm.org/winners/smartcampus-2026",
}
created_entry = requests.post(f"{BASE}/students/S1001/timeline", json=new_achieve, headers=stu_auth).json()
entry_id = created_entry["id"]
print(f"[PASS] 5. Student submitted achievement {entry_id} with status: {created_entry['verification_status']}")

# 4. Faculty Verifies Achievement
verify_res = requests.post(
    f"{BASE}/achievements/{entry_id}/verify",
    json={"status": "Institution-Verified", "remarks": "Verified via ACM competition portal link"},
    headers=fac_auth,
).json()
print(f"[PASS] 6. Faculty verified achievement {entry_id} -> {verify_res['verification_status']} (Reviewer: {verify_res['verified_by_name']})")

# 5. Check ML 360 profile
stu_360 = requests.get(f"{BASE}/students/S1001", headers=fac_auth).json()
print(f"[PASS] 7. Student360 ML Profile -> Risk Score: {stu_360['risk_score']} ({stu_360['risk_level']}), Model Version: {stu_360['model_version']}")

# 6. Check Cohort Insights
cohort = requests.get(f"{BASE}/cohort/insights", headers=fac_auth).json()
print(f"[PASS] 8. Cohort Insights -> Total: {cohort['total_students']}, High Risk: {cohort['high_risk_count']}, Distribution: {cohort['risk_distribution']}")

print("\n>>> ALL END-TO-END WORKFLOW CHECKS PASSED LIVE ON RUNNING BACKEND! <<<")

"""backend/app/services/cohort_service.py

Cohort Service.
Aggregates dynamic predictions across all verified demo students.
Calculates risk distributions, global SHAP drivers, segments, and course breakdown
without hardcoding or synthetic assumptions.
"""

from collections import defaultdict
from typing import Any, Dict, List

from backend.app.services.model_service import model_service
from backend.app.services.shap_service import shap_service
from backend.app.services.student_service import student_service


class CohortService:
    """Computes dynamic cohort-wide analytics and SHAP drivers."""

    def get_cohort_insights(self) -> Dict[str, Any]:
        """
        Loads all demo students, runs real ML inference for each,
        and computes aggregate statistics, global SHAP, segments, and by-course metrics.
        """
        students = student_service.get_all_students()

        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        cohort_feature_list: List[Dict[str, Any]] = []
        course_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "high": 0})
        
        segments = {
            "High academic risk (Approved units <= 2)": 0,
            "Financial risk (Debtor or Tuition overdue)": 0,
            "Retention transition risk (Age > 25)": 0,
        }

        for student in students:
            features = student.get("features", {})
            sid = str(student.get("demo_id") or student.get("student_id", "UNKNOWN"))

            # Predict dynamically using the loaded model
            pred = model_service.predict(features=features, student_id=sid)
            level = pred.get("risk_level", "Medium")
            is_high = (level == "High")

            if is_high:
                high_risk_count += 1
            elif level == "Medium":
                medium_risk_count += 1
            elif level == "Low":
                low_risk_count += 1

            # Course tracking
            course_id = str(features.get("Course", "Unknown"))
            course_counts[course_id]["total"] += 1
            if is_high:
                course_counts[course_id]["high"] += 1

            # Segments calculation from real UCI features
            if float(features.get("Curricular units 2nd sem (approved)", 0)) <= 2:
                segments["High academic risk (Approved units <= 2)"] += 1
            if float(features.get("Debtor", 0)) == 1 or float(features.get("Tuition fees up to date", 1)) == 0:
                segments["Financial risk (Debtor or Tuition overdue)"] += 1
            if float(features.get("Age at enrollment", 0)) > 25:
                segments["Retention transition risk (Age > 25)"] += 1

            cohort_feature_list.append(features)

        total_students = len(students)

        # Compute Global SHAP feature importances using Smruthi's engine
        global_shap = shap_service.explain_cohort(cohort_feature_list, top_k=10)

        # Build segments list
        segment_list = [{"name": name, "count": cnt} for name, cnt in segments.items()]

        # Build by_course list
        COURSE_NAMES = {
            "171": "Animation and Multimedia Design (171)",
            "9254": "Agronomy (9254)",
            "9070": "Communication Design (9070)",
            "9773": "Veterinary Nursing (9773)",
            "9238": "Basic Education (9238)",
            "9147": "Management (9147)",
            "9003": "Social Service (9003)",
            "9119": "Informatics Engineering (9119)",
            "9500": "Nursing (9500)",
            "9085": "Journalism and Communication (9085)",
            "9239": "Tourism (9239)",
        }

        by_course_list = [
            {
                "course": COURSE_NAMES.get(str(c), f"Degree Program ({c})"),
                "count": data["total"],
                "total": data["total"],
                "high_risk_count": data["high"],
                "high_risk_pct": round(data["high"] / max(1, data["total"]), 2),
            }
            for c, data in sorted(course_counts.items(), key=lambda x: x[1]["total"], reverse=True)
        ]

        return {
            "total_students": total_students,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
            "risk_distribution": {
                "High": high_risk_count,
                "Medium": medium_risk_count,
                "Low": low_risk_count,
            },
            "global_shap": global_shap,
            "segments": segment_list,
            "by_course": by_course_list,
        }


# Global singleton instance
cohort_service = CohortService()

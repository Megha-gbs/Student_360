"""backend/app/services/intervention_service.py

Intervention Service.
Generates targeted intervention drafts based on real UCI risk contributors.
Strictly adheres to Human-in-the-Loop policy:
- AI drafts recommendations; human staff review, edit, and approve.
- Simulated outcomes are clearly labelled as demonstration simulations.
"""

from typing import Any, Dict, List, Optional
from backend.app.services.student_service import student_service


class InterventionService:
    """Manages intervention recommendations and human approval workflows."""

    def process_intervention(
        self,
        student_id: Optional[str] = None,
        intervention_type: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        approved: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Drafts or approves an intervention for a student.
        Maintains human-in-the-loop governance.
        """
        sid = student_id or "STUDENT"
        student = student_service.get_student_by_id(sid) if student_id else None
        features = student.get("features", {}) if student else {}

        # Determine context-aware category and recommendations based on real features
        approved_units_2nd = float(features.get("Curricular units 2nd sem (approved)", 5))
        is_debtor = float(features.get("Debtor", 0)) == 1
        tuition_overdue = float(features.get("Tuition fees up to date", 1)) == 0

        if is_debtor or tuition_overdue:
            category = "Financial Support & Tuition Planning"
            inferred_type = intervention_type or "Financial Aid Counseling"
            draft_text = (
                f"Proposed financial intervention for student {sid}: Consult with financial aid office "
                f"to resolve tuition payment status and explore scholarship/grant relief."
            )
            rec_actions = [
                "Schedule financial aid consultation",
                "Review tuition payment plan",
                "Emergency student grant referral",
            ]
        elif approved_units_2nd <= 2:
            category = "Academic Counseling & Tutoring"
            inferred_type = intervention_type or "Academic Counseling"
            draft_text = (
                f"Proposed academic intervention for student {sid}: Enroll in 1-on-1 subject tutoring "
                f"for 2nd semester courses and establish weekly progress reviews with faculty mentor."
            )
            rec_actions = [
                "Bi-weekly faculty mentoring check-in",
                "Enroll in course tutoring center",
                "Course load and credit audit",
            ]
        else:
            category = "Student Success & Retention Mentoring"
            inferred_type = intervention_type or "Faculty Mentorship"
            draft_text = (
                f"Proposed general retention support for student {sid}: Connect with academic advisor "
                f"to review graduation timeline and course performance."
            )
            rec_actions = [
                "Advisor check-in",
                "Peer study group connection",
            ]

        is_human_approved = bool(approved)
        status = "approved" if is_human_approved else "drafted"

        return {
            "student_id": sid,
            "intervention_type": inferred_type,
            "category": category,
            "draft": notes or draft_text,
            "status": status,
            "requires_human_approval": True,
            "human_approved": is_human_approved,
            "recommended_actions": rec_actions,
            "message": "Intervention approved by staff." if is_human_approved else "Intervention draft ready for human review.",
        }

    def simulate_outcome(
        self,
        student_id: str,
        student_features: Dict[str, Any],
        intervention_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Simulates follow-up post-intervention outcome.
        Clearly flagged with SIMULATED DEMONSTRATION OUTCOME badge.
        """
        # Calculate simulated risk based on improved approved units
        curr_approved = float(student_features.get("Curricular units 2nd sem (approved)", 2))
        simulated_units = min(curr_approved + 2, 6.0)

        # Baseline risk drop for demonstration
        sim_risk = max(20, int(round(74 - (simulated_units * 8))))
        sim_level = "Low" if sim_risk < 35 else ("Medium" if sim_risk < 65 else "High")

        return {
            "student_id": student_id,
            "simulated_risk_score": sim_risk,
            "simulated_risk_level": sim_level,
            "status": "simulated",
            "badge": "SIMULATED DEMONSTRATION OUTCOME",
            "note": "Simulated demonstration outcome post-intervention; not real intervention evidence.",
        }


# Global singleton instance
intervention_service = InterventionService()

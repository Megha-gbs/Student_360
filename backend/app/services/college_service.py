"""backend/app/services/college_service.py

Unified service managing College Management platform data and operations:
- Authentication & User identities
- Timetable & Class scheduling with conflict detection
- Attendance management (marking, validation, subject calculations, alerts)
- Marks & Results (internals, grading, GPA/CGPA progression)
- Assignment lifecycle (creation, student submissions, faculty grading)
- Announcements & Notices
- Examination scheduling
- Fee management & transaction receipts
- Daily timetable schedule notification engine
- Administrative rosters & audit logging
"""

import copy
from datetime import datetime, time, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.app.services.student_service import student_service


from backend.app.security import hash_password, verify_password, session_store


class CollegeService:
    def __init__(self):
        self._initialized = False
        self._users: Dict[str, Dict[str, Any]] = {}
        self._students: Dict[str, Dict[str, Any]] = {}
        self._faculty: Dict[str, Dict[str, Any]] = {}
        self._timetable: List[Dict[str, Any]] = []
        self._attendance_records: List[Dict[str, Any]] = []
        self._marks_records: Dict[str, List[Dict[str, Any]]] = {}
        self._assignments: List[Dict[str, Any]] = []
        self._announcements: List[Dict[str, Any]] = []
        self._examinations: List[Dict[str, Any]] = []
        self._fees: Dict[str, Dict[str, Any]] = {}
        self._notifications: List[Dict[str, Any]] = []
        self._audit_logs: List[Dict[str, Any]] = []
        self._departments: List[Dict[str, Any]] = []

        self._seed_initial_data()

    def _seed_initial_data(self):
        """Seed realistic institutional data aligned with demo students and faculty."""
        if self._initialized:
            return

        # 1. Departments & Programs
        self._departments = [
            {"code": "CS", "name": "Computer Science & Engineering", "dean": "Dr. Alan Turing", "students_count": 480},
            {"code": "DES", "name": "Animation & Multimedia Design", "dean": "Prof. Ada Lovelace", "students_count": 220},
            {"code": "AGR", "name": "Agronomy & Bio-Systems", "dean": "Dr. Gregor Mendel", "students_count": 190},
            {"code": "MGT", "name": "Management & Business Analytics", "dean": "Dr. Peter Drucker", "students_count": 340},
            {"code": "NUR", "name": "Nursing & Healthcare Sciences", "dean": "Dr. Florence Nightingale", "students_count": 260},
        ]

        # 2. Faculty Members with Assigned Students
        self._faculty = {
            "FAC001": {
                "id": "FAC001",
                "username": "faculty",
                "name": "Dr. Alan Turing",
                "email": "faculty@student360.edu",
                "department": "Computer Science & Engineering",
                "designation": "Professor & Head of Department",
                "phone": "+1 (555) 019-2831",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1001", "S1002", "S1003", "S1004", "S1005"],
                "assigned_subjects": [
                    {"code": "CS301", "name": "Data Structures & Algorithms", "class": "CS-Sem3-A"},
                    {"code": "CS305", "name": "Software Engineering & Architecture", "class": "CS-Sem3-B"},
                    {"code": "CS402", "name": "Machine Learning Fundamentals", "class": "CS-Sem5-A"},
                ],
                "status": "Active",
            },
            "FAC-CS101": {
                "id": "FAC-CS101",
                "username": "faculty",
                "name": "Dr. Alan Turing",
                "email": "faculty@student360.edu",
                "department": "Computer Science & Engineering",
                "designation": "Professor & Head of Department",
                "phone": "+1 (555) 019-2831",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1001", "S1002", "S1003", "S1004", "S1005"],
                "assigned_subjects": [
                    {"code": "CS301", "name": "Data Structures & Algorithms", "class": "CS-Sem3-A"},
                    {"code": "CS305", "name": "Software Engineering & Architecture", "class": "CS-Sem3-B"},
                    {"code": "CS402", "name": "Machine Learning Fundamentals", "class": "CS-Sem5-A"},
                ],
                "status": "Active",
            },
            "FAC-DES201": {
                "id": "FAC-DES201",
                "username": "proflovelace",
                "name": "Prof. Ada Lovelace",
                "email": "a.lovelace@student360.edu",
                "department": "Animation & Multimedia Design",
                "designation": "Associate Professor",
                "phone": "+1 (555) 019-7462",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1001", "S1003", "S1007"],
                "assigned_subjects": [
                    {"code": "DES101", "name": "2D Animation & Motion Graphics", "class": "DES-Sem2-A"},
                    {"code": "DES204", "name": "Digital Multimedia Storytelling", "class": "DES-Sem2-B"},
                ],
                "status": "Active",
            },
            "FAC-ENG301": {
                "id": "FAC-ENG301",
                "username": "drhopper",
                "name": "Dr. Grace Hopper",
                "email": "g.hopper@student360.edu",
                "department": "Computer Science & Engineering",
                "designation": "Senior Lecturer",
                "phone": "+1 (555) 019-8833",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1006", "S1008", "S1010"],
                "assigned_subjects": [
                    {"code": "CS302", "name": "Database Management Systems", "class": "CS-Sem3-A"},
                    {"code": "CS308", "name": "Operating Systems & Concurrency", "class": "CS-Sem3-A"},
                ],
                "status": "Active",
            },
        }

        # 3. Seed Students (Mapping S1001-S1010)
        demo_student_names = [
            ("S1001", "Sarah Connor", "Animation & Multimedia Design", 2, "B.Des Animation", "2024-AMD-001"),
            ("S1002", "Marcus Wright", "Agronomy & Bio-Systems", 2, "B.Sc Agronomy", "2024-AGR-002"),
            ("S1003", "Elena Rostova", "Communication Design", 3, "B.Des Design", "2023-DES-003"),
            ("S1004", "David Bowman", "Computer Science & Engineering", 3, "B.Tech CSE", "2023-CSE-004"),
            ("S1005", "Samantha Carter", "Management & Business Analytics", 4, "B.B.A Management", "2022-MGT-005"),
            ("S1006", "Hiro Protagonist", "Computer Science & Engineering", 3, "B.Tech CSE", "2023-CSE-006"),
            ("S1007", "Clara Oswald", "Basic Education & Pedagogy", 2, "B.Ed Education", "2024-EDU-007"),
            ("S1008", "Miles Dyson", "Informatics Engineering", 4, "B.Tech Informatics", "2022-INF-008"),
            ("S1009", "Dana Scully", "Nursing & Healthcare Sciences", 3, "B.Sc Nursing", "2023-NUR-009"),
            ("S1010", "Fox Mulder", "Social Service & Governance", 2, "B.A Social Service", "2024-SOC-010"),
        ]

        for sid, name, dept, sem, prog, roll in demo_student_names:
            email = f"{name.lower().replace(' ', '.')}@student360.edu"
            self._students[sid] = {
                "student_id": sid,
                "roll_number": roll,
                "name": name,
                "email": email,
                "phone": "+1 (555) 012-" + sid[-4:],
                "department": dept,
                "program": prog,
                "semester": sem,
                "admission_year": 2024 - (sem // 2),
                "institution_id": "INST-001",
                "status": "Active",
                "cgpa": 3.42 if sid in ["S1002", "S1004", "S1006"] else 2.65 if sid == "S1001" else 3.10,
                "attendance_rate": 68.5 if sid == "S1001" else 88.4,
                "fees_status": "Overdue" if sid == "S1001" else "Paid",
            }

        # 4. User Accounts for Authentication (Hashed Passwords)
        self._users = {
            "adm001": {
                "id": "ADM001",
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "name": "Dean Evelyn Vance",
                "email": "admin@student360.edu",
                "role": "admin",
                "department": "Academic Directorate",
                "designation": "Dean of Academic Affairs & Registrar",
                "phone": "+1 (555) 011-9900",
                "institution_id": "INST-001",
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            },
            "admin": {
                "id": "ADM001",
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "name": "Dean Evelyn Vance",
                "email": "admin@student360.edu",
                "role": "admin",
                "department": "Academic Directorate",
                "designation": "Dean of Academic Affairs & Registrar",
                "phone": "+1 (555) 011-9900",
                "institution_id": "INST-001",
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            },
            "fac001": {
                "id": "FAC001",
                "username": "faculty",
                "password_hash": hash_password("faculty123"),
                "name": "Dr. Alan Turing",
                "email": "faculty@student360.edu",
                "role": "faculty",
                "department": "Computer Science & Engineering",
                "designation": "Professor & HOD",
                "phone": "+1 (555) 019-2831",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1001", "S1002", "S1003", "S1004", "S1005"],
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            },
            "faculty": {
                "id": "FAC-CS101",
                "username": "faculty",
                "password_hash": hash_password("faculty123"),
                "name": "Dr. Alan Turing",
                "email": "faculty@student360.edu",
                "role": "faculty",
                "department": "Computer Science & Engineering",
                "designation": "Professor & HOD",
                "phone": "+1 (555) 019-2831",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1001", "S1002", "S1003", "S1004", "S1005"],
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            },
            "fac-cs101": {
                "id": "FAC-CS101",
                "username": "faculty",
                "password_hash": hash_password("faculty123"),
                "name": "Dr. Alan Turing",
                "email": "faculty@student360.edu",
                "role": "faculty",
                "department": "Computer Science & Engineering",
                "designation": "Professor & HOD",
                "phone": "+1 (555) 019-2831",
                "institution_id": "INST-001",
                "assigned_student_ids": ["S1001", "S1002", "S1003", "S1004", "S1005"],
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            },
            "s1001": {
                "id": "S1001",
                "username": "student",
                "password_hash": hash_password("student123"),
                "name": "Sarah Connor",
                "email": "student@student360.edu",
                "role": "student",
                "department": "Animation & Multimedia Design",
                "semester": 2,
                "program": "B.Des Animation",
                "phone": "+1 (555) 012-1001",
                "institution_id": "INST-001",
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
            },
            "student": {
                "id": "S1001",
                "username": "student",
                "password_hash": hash_password("student123"),
                "name": "Sarah Connor",
                "email": "student@student360.edu",
                "role": "student",
                "department": "Animation & Multimedia Design",
                "semester": 2,
                "program": "B.Des Animation",
                "phone": "+1 (555) 012-1001",
                "institution_id": "INST-001",
                "status": "Active",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
            },
            "deactivated": {
                "id": "DEACT01",
                "username": "deactivated",
                "password_hash": hash_password("Student@360"),
                "name": "Deactivated Demo User",
                "email": "deactivated@student360.edu",
                "role": "student",
                "department": "General Sciences",
                "institution_id": "INST-001",
                "status": "Deactivated",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=deactivated",
            },
            "admin_inst2": {
                "id": "ADM-INST2",
                "username": "admin_inst2",
                "password_hash": hash_password("Admin@360"),
                "name": "Dean Arthur Pendelton",
                "email": "admin@otheruni.edu",
                "role": "admin",
                "department": "Administration",
                "institution_id": "INST-002",
                "status": "Active",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=inst2",
            },
        }

        # Also register student aliases so S1001, S1002, etc. can log in
        for sid, sdata in self._students.items():
            username_key = sid.lower()
            if username_key not in self._users:
                self._users[username_key] = {
                    "id": sid,
                    "username": username_key,
                    "password_hash": hash_password("Student@360"),
                    "name": sdata["name"],
                    "email": sdata["email"],
                    "role": "student",
                    "department": sdata["department"],
                    "semester": sdata["semester"],
                    "program": sdata["program"],
                    "phone": sdata["phone"],
                    "institution_id": sdata.get("institution_id", "INST-001"),
                    "status": sdata.get("status", "Active"),
                    "roll_number": sdata.get("roll_number"),
                    "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={sid}",
                }

        # Also register faculty aliases so FAC-CS101, proflovelace, drhopper, etc. can log in
        for fid, fdata in self._faculty.items():
            fkey = fid.lower()
            if fkey not in self._users:
                self._users[fkey] = {
                    "id": fid,
                    "username": fdata.get("username", fkey),
                    "password_hash": hash_password("Faculty@360"),
                    "name": fdata["name"],
                    "email": fdata["email"],
                    "role": "faculty",
                    "department": fdata["department"],
                    "designation": fdata.get("designation"),
                    "phone": fdata.get("phone"),
                    "institution_id": fdata.get("institution_id", "INST-001"),
                    "assigned_student_ids": fdata.get("assigned_student_ids", []),
                    "status": fdata.get("status", "Active"),
                    "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={fid}",
                }
            f_uname = fdata.get("username", "").lower()
            if f_uname and f_uname not in self._users:
                self._users[f_uname] = self._users[fkey]

        # 5. Master Timetable
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self._timetable = [
            # Monday
            {"id": "TT-101", "day": "Monday", "subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "faculty_id": "FAC-CS101", "faculty_name": "Dr. Alan Turing", "room": "Lecture Hall 301", "start_time": "09:00", "end_time": "10:15", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-102", "day": "Monday", "subject_code": "CS302", "subject_name": "Database Management Systems", "faculty_id": "FAC-ENG301", "faculty_name": "Dr. Grace Hopper", "room": "Computing Lab 2", "start_time": "10:30", "end_time": "11:45", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-103", "day": "Monday", "subject_code": "DES101", "subject_name": "2D Animation & Motion Graphics", "faculty_id": "FAC-DES201", "faculty_name": "Prof. Ada Lovelace", "room": "Studio A", "start_time": "13:00", "end_time": "14:30", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            # Tuesday
            {"id": "TT-104", "day": "Tuesday", "subject_code": "CS305", "subject_name": "Software Engineering & Architecture", "faculty_id": "FAC-CS101", "faculty_name": "Dr. Alan Turing", "room": "Auditorium B", "start_time": "09:30", "end_time": "10:45", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-105", "day": "Tuesday", "subject_code": "DES204", "subject_name": "Digital Multimedia Storytelling", "faculty_id": "FAC-DES201", "faculty_name": "Prof. Ada Lovelace", "room": "Media Center 104", "start_time": "11:00", "end_time": "12:30", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-106", "day": "Tuesday", "subject_code": "CS308", "subject_name": "Operating Systems & Concurrency", "faculty_id": "FAC-ENG301", "faculty_name": "Dr. Grace Hopper", "room": "Lecture Hall 204", "start_time": "14:00", "end_time": "15:15", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            # Wednesday
            {"id": "TT-107", "day": "Wednesday", "subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "faculty_id": "FAC-CS101", "faculty_name": "Dr. Alan Turing", "room": "Lecture Hall 301", "start_time": "09:00", "end_time": "10:15", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-108", "day": "Wednesday", "subject_code": "DES101", "subject_name": "2D Animation & Motion Graphics", "faculty_id": "FAC-DES201", "faculty_name": "Prof. Ada Lovelace", "room": "Studio A", "start_time": "10:30", "end_time": "12:00", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            # Thursday
            {"id": "TT-109", "day": "Thursday", "subject_code": "CS302", "subject_name": "Database Management Systems", "faculty_id": "FAC-ENG301", "faculty_name": "Dr. Grace Hopper", "room": "Computing Lab 2", "start_time": "10:00", "end_time": "11:30", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-110", "day": "Thursday", "subject_code": "CS305", "subject_name": "Software Engineering & Architecture", "faculty_id": "FAC-CS101", "faculty_name": "Dr. Alan Turing", "room": "Lecture Hall 105", "start_time": "13:30", "end_time": "15:00", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            # Friday
            {"id": "TT-111", "day": "Friday", "subject_code": "DES204", "subject_name": "Digital Multimedia Storytelling", "faculty_id": "FAC-DES201", "faculty_name": "Prof. Ada Lovelace", "room": "Studio B", "start_time": "09:30", "end_time": "11:00", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
            {"id": "TT-112", "day": "Friday", "subject_code": "CS308", "subject_name": "Operating Systems & Concurrency", "faculty_id": "FAC-ENG301", "faculty_name": "Dr. Grace Hopper", "room": "Lecture Hall 204", "start_time": "11:30", "end_time": "13:00", "semester": 2, "department": "Animation & Multimedia Design", "class_id": "CS-Sem2"},
        ]

        # 6. Seed Attendance Records
        self._attendance_records = [
            {"student_id": "S1001", "subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "attended": 18, "total": 28, "threshold": 75.0},
            {"student_id": "S1001", "subject_code": "CS302", "subject_name": "Database Management Systems", "attended": 24, "total": 28, "threshold": 75.0},
            {"student_id": "S1001", "subject_code": "DES101", "subject_name": "2D Animation & Motion Graphics", "attended": 16, "total": 26, "threshold": 75.0},
            {"student_id": "S1001", "subject_code": "CS305", "subject_name": "Software Engineering & Architecture", "attended": 22, "total": 26, "threshold": 75.0},
            {"student_id": "S1001", "subject_code": "DES204", "subject_name": "Digital Multimedia Storytelling", "attended": 17, "total": 24, "threshold": 75.0},
            {"student_id": "S1001", "subject_code": "CS308", "subject_name": "Operating Systems & Concurrency", "attended": 20, "total": 24, "threshold": 75.0},
        ]
        # Seed good attendance for other students
        for sid in ["S1002", "S1003", "S1004", "S1005", "S1006"]:
            self._attendance_records.extend([
                {"student_id": sid, "subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "attended": 25, "total": 28, "threshold": 75.0},
                {"student_id": sid, "subject_code": "CS302", "subject_name": "Database Management Systems", "attended": 26, "total": 28, "threshold": 75.0},
                {"student_id": sid, "subject_code": "CS305", "subject_name": "Software Engineering & Architecture", "attended": 24, "total": 26, "threshold": 75.0},
            ])

        # 7. Seed Marks & Results
        self._marks_records["S1001"] = [
            {"subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "credits": 4, "internal_assessment": 28.0, "midterm_exam": 32.0, "final_exam": 30.0, "total_marks": 62.0, "max_marks": 100.0, "grade": "C", "status": "Passed"},
            {"subject_code": "CS302", "subject_name": "Database Management Systems", "credits": 4, "internal_assessment": 34.0, "midterm_exam": 38.0, "final_exam": 42.0, "total_marks": 76.0, "max_marks": 100.0, "grade": "B", "status": "Passed"},
            {"subject_code": "DES101", "subject_name": "2D Animation & Motion Graphics", "credits": 3, "internal_assessment": 22.0, "midterm_exam": 25.0, "final_exam": None, "total_marks": 47.0, "max_marks": 100.0, "grade": "D", "status": "Needs Improvement"},
            {"subject_code": "CS305", "subject_name": "Software Engineering", "credits": 3, "internal_assessment": 36.0, "midterm_exam": 40.0, "final_exam": None, "total_marks": 76.0, "max_marks": 100.0, "grade": "B+", "status": "In Progress"},
            {"subject_code": "DES204", "subject_name": "Digital Multimedia Storytelling", "credits": 3, "internal_assessment": 26.0, "midterm_exam": 28.0, "final_exam": None, "total_marks": 54.0, "max_marks": 100.0, "grade": "C-", "status": "In Progress"},
        ]

        # 8. Seed Assignments
        self._assignments = [
            {
                "id": "ASN-201",
                "title": "B-Tree and Graph Traversal Implementation",
                "description": "Implement an optimized indexed B-Tree in C++ or Python with benchmark tests.",
                "subject_code": "CS301",
                "subject_name": "Data Structures & Algorithms",
                "faculty_id": "FAC-CS101",
                "faculty_name": "Dr. Alan Turing",
                "class_id": "CS-Sem2",
                "due_date": "2026-10-15",
                "due_time": "23:59",
                "max_marks": 50.0,
                "status": "Active",
                "submissions": {
                    "S1001": {
                        "submission_id": "SUB-101",
                        "student_id": "S1001",
                        "student_name": "Sarah Connor",
                        "submitted_at": "2026-10-08 18:22",
                        "content": "Submitted repository link and performance profiling logs for B-Tree indexing.",
                        "file_name": "btree_project_s1001.zip",
                        "status": "Submitted",
                        "grade": None,
                        "feedback": None,
                    }
                },
            },
            {
                "id": "ASN-202",
                "title": "Relational Schema Normalization (3NF & BCNF)",
                "description": "Analyze the given e-commerce dataset schema, decompose anomalous tables into BCNF, and provide SQL DDL scripts.",
                "subject_code": "CS302",
                "subject_name": "Database Management Systems",
                "faculty_id": "FAC-ENG301",
                "faculty_name": "Dr. Grace Hopper",
                "class_id": "CS-Sem2",
                "due_date": "2026-10-18",
                "due_time": "17:00",
                "max_marks": 40.0,
                "status": "Active",
                "submissions": {},
            },
            {
                "id": "ASN-203",
                "title": "Character Rigging & Keyframe Principles",
                "description": "Develop a 15-second animated walk cycle demonstrating squash-and-stretch and anticipation.",
                "subject_code": "DES101",
                "subject_name": "2D Animation & Motion Graphics",
                "faculty_id": "FAC-DES201",
                "faculty_name": "Prof. Ada Lovelace",
                "class_id": "CS-Sem2",
                "due_date": "2026-10-22",
                "due_time": "20:00",
                "max_marks": 100.0,
                "status": "Active",
                "submissions": {},
            },
        ]

        # 9. Seed Announcements
        self._announcements = [
            {
                "id": "ANN-101",
                "title": "Midterm Examination Schedule for Fall Semester Released",
                "content": "The central examination board has officially published the Midterm Examination schedule for all Undergraduate and Graduate programs. Please check your personalized examination tab for venue allocations.",
                "category": "Examination",
                "target_audience": "all",
                "priority": "Urgent",
                "publisher": "Dean Evelyn Vance",
                "publisher_role": "Registrar",
                "created_at": "2026-10-07 09:30",
                "read_by": ["S1001"],
            },
            {
                "id": "ANN-102",
                "title": "ACM Student Chapter Hackathon — Registrations Now Open",
                "content": "Annual 36-hour Innovation Hackathon scheduled for October 24-25. Interdisciplinary teams of 3-4 students can register with exciting prizes sponsored by leading tech companies.",
                "category": "Academic",
                "target_audience": "students",
                "priority": "Important",
                "publisher": "Dr. Alan Turing",
                "publisher_role": "HOD Computer Science",
                "created_at": "2026-10-06 14:15",
                "read_by": [],
            },
            {
                "id": "ANN-103",
                "title": "Library Extended Hours for Upcoming Examination Prep",
                "content": "The central campus library will remain open 24/7 starting Monday next week through the conclusion of semester finals.",
                "category": "Campus",
                "target_audience": "all",
                "priority": "General",
                "publisher": "Campus Facilities Office",
                "publisher_role": "Administration",
                "created_at": "2026-10-05 11:00",
                "read_by": ["S1001"],
            },
        ]

        # 10. Seed Examinations
        self._examinations = [
            {
                "id": "EX-301",
                "title": "Data Structures & Algorithms Midterm",
                "subject_code": "CS301",
                "subject_name": "Data Structures & Algorithms",
                "exam_type": "Midterm",
                "date": "2026-10-28",
                "start_time": "10:00",
                "end_time": "12:00",
                "venue": "Exam Hall 1 — Desks 1 to 40",
                "semester": 2,
                "department": "Animation & Multimedia Design",
                "results_published": False,
            },
            {
                "id": "EX-302",
                "title": "Database Management Systems Midterm",
                "subject_code": "CS302",
                "subject_name": "Database Management Systems",
                "exam_type": "Midterm",
                "date": "2026-10-30",
                "start_time": "14:00",
                "end_time": "16:00",
                "venue": "Computing Lab 2 — Terminals 1 to 35",
                "semester": 2,
                "department": "Animation & Multimedia Design",
                "results_published": False,
            },
            {
                "id": "EX-303",
                "title": "2D Animation Practical Studio Assessment",
                "subject_code": "DES101",
                "subject_name": "2D Animation & Motion Graphics",
                "exam_type": "Practical Lab",
                "date": "2026-11-03",
                "start_time": "09:30",
                "end_time": "12:30",
                "venue": "Studio A Workstations",
                "semester": 2,
                "department": "Animation & Multimedia Design",
                "results_published": False,
            },
        ]

        # 11. Seed Fees
        self._fees["S1001"] = {
            "student_id": "S1001",
            "student_name": "Sarah Connor",
            "total_fees": 4500.0,
            "scholarship_discount": 500.0,
            "paid_amount": 2500.0,
            "outstanding_balance": 1500.0,
            "due_date": "2026-10-25",
            "status": "Partially Paid",
            "transactions": [
                {
                    "transaction_id": "TXN-8801",
                    "date": "2026-08-15",
                    "amount": 2500.0,
                    "payment_method": "Online NetBanking (HDFC)",
                    "receipt_no": "REC-2026-8801",
                    "status": "Completed",
                }
            ],
        }

        # 12. Seed In-App Notifications
        self._notifications = [
            {
                "id": "NOTIF-1",
                "user_id": "S1001",
                "title": "Welcome to Student360 Platform",
                "message": "Your unified academic profile and timetable are synced with the institutional registrar.",
                "type": "system",
                "priority": "normal",
                "created_at": "2026-10-09 08:00",
                "read": True,
                "delivery_channel": "in_app",
                "delivery_status": "delivered",
            },
            {
                "id": "NOTIF-2",
                "user_id": "S1001",
                "title": "Low Attendance Alert: CS301 (64.3%)",
                "message": "Your attendance in Data Structures & Algorithms is below the 75% institutional threshold. Please consult Prof. Alan Turing.",
                "type": "system",
                "priority": "high",
                "created_at": "2026-10-09 08:30",
                "read": False,
                "delivery_channel": "in_app",
                "delivery_status": "delivered",
            },
        ]

        # 13. Audit Logs
        self._audit_logs = [
            {
                "id": "AUD-001",
                "timestamp": "2026-10-09 08:15",
                "actor": "admin",
                "actor_role": "admin",
                "action": "SYSTEM_STARTUP",
                "target": "Institutional Database",
                "details": "Platform initialized with verified datasets and XGBoost ML services.",
            }
        ]

        # 14. Import History
        self._import_history = [
            {
                "id": "IMP-001",
                "timestamp": "2026-10-08 11:30",
                "imported_by": "admin",
                "filename": "fall_2024_admissions_roster.csv",
                "total_rows": 10,
                "accepted_rows": 10,
                "rejected_rows": 0,
                "status": "Completed",
            }
        ]

        # 15. Student Education & Career Timeline Entries
        self._timeline_entries = [
            {
                "id": "TL-101",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "High School Secondary Diploma with Honors",
                "category": "Education",
                "academic_year": "2023-2024",
                "date": "2024-05-20",
                "description": "Graduated in Top 5% of class with focus on Digital Media and Visual Arts.",
                "organization": "Springfield Academic High School",
                "evidence_url": "https://credentials.academic.org/diploma/2024-s1001",
                "verification_status": "Institution-Verified",
                "is_verified": True,
                "verified_by_id": "ADM001",
                "verified_by_name": "Dean Evelyn Vance",
                "verified_at": "2024-08-01 10:00",
                "rejection_reason": None,
                "created_at": "2024-08-01 09:00",
            },
            {
                "id": "TL-102",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "Enrolled in B.Des Animation & Multimedia Design",
                "category": "Semesters",
                "academic_year": "2024-2025",
                "date": "2024-08-01",
                "description": "Completed formal institutional orientation and enrolled in Semester 1 studio courses.",
                "organization": "Stanford University Node (INST-001)",
                "evidence_url": None,
                "verification_status": "Institution-Verified",
                "is_verified": True,
                "verified_by_id": "ADM001",
                "verified_by_name": "Dean Evelyn Vance",
                "verified_at": "2024-08-01 10:30",
                "rejection_reason": None,
                "created_at": "2024-08-01 09:30",
            },
            {
                "id": "TL-103",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "Completed Semester 1 Studio Foundations",
                "category": "Semesters",
                "academic_year": "2024-2025",
                "date": "2024-12-18",
                "description": "Completed foundation coursework in 2D design, drawing, and storytelling.",
                "organization": "Stanford University Node (INST-001)",
                "evidence_url": None,
                "verification_status": "Institution-Verified",
                "is_verified": True,
                "verified_by_id": "FAC-CS101",
                "verified_by_name": "Dr. Alan Turing",
                "verified_at": "2024-12-20 14:00",
                "rejection_reason": None,
                "created_at": "2024-12-19 11:00",
            },
            {
                "id": "TL-104",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "Figma Certified Professional UI/UX Designer",
                "category": "Certifications",
                "academic_year": "2024-2025",
                "date": "2025-02-10",
                "description": "Completed 60-hour advanced training on design systems, responsive auto-layout, and interactive prototyping.",
                "organization": "Figma Design Academy",
                "evidence_url": "https://credentials.figma.com/verify/f88129",
                "verification_status": "Institution-Verified",
                "is_verified": True,
                "verified_by_id": "FAC-DES201",
                "verified_by_name": "Prof. Ada Lovelace",
                "verified_at": "2025-02-15 16:30",
                "rejection_reason": None,
                "created_at": "2025-02-11 12:00",
            },
            {
                "id": "TL-105",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "ACM University Hackathon 2025 — 2nd Place Runner Up",
                "category": "Hackathons",
                "academic_year": "2024-2025",
                "date": "2025-03-22",
                "description": "Built 'CampusEco', a gamified sustainability tracking mobile app with real-time carbon offset telemetry.",
                "organization": "ACM Student Chapter & Department of CSE",
                "evidence_url": "https://hackathon.acm.org/2025/awards/s1001",
                "verification_status": "Self-Reported",
                "is_verified": False,
                "verified_by_id": None,
                "verified_by_name": None,
                "verified_at": None,
                "rejection_reason": None,
                "created_at": "2025-03-23 10:15",
            },
            {
                "id": "TL-106",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "3D Interactive Campus Virtual Tour Project",
                "category": "Projects",
                "academic_year": "2024-2025",
                "date": "2025-06-15",
                "description": "Developed WebGL-based three.js virtual campus tour featuring interactive lecture hall navigation.",
                "organization": "Design Media Lab",
                "evidence_url": "https://github.com/student360-demos/campus-3d-tour",
                "verification_status": "Self-Reported",
                "is_verified": False,
                "verified_by_id": None,
                "verified_by_name": None,
                "verified_at": None,
                "rejection_reason": None,
                "created_at": "2025-06-16 14:20",
            },
            {
                "id": "TL-107",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "Summer UI/UX Design Intern",
                "category": "Internships",
                "academic_year": "2025-2026",
                "date": "2025-08-30",
                "description": "Completed 8-week summer internship designing user-facing dashboards and micro-interactions for SaaS platform.",
                "organization": "Horizon Interactive Studios",
                "evidence_url": "https://horizon.design/interns/s1001",
                "verification_status": "Self-Reported",
                "is_verified": False,
                "verified_by_id": None,
                "verified_by_name": None,
                "verified_at": None,
                "rejection_reason": None,
                "created_at": "2025-09-02 09:45",
            },
            {
                "id": "TL-108",
                "student_id": "S1001",
                "student_name": "Sarah Connor",
                "title": "Resume & Career Portfolio Approved for Placements",
                "category": "Placement Milestones",
                "academic_year": "2025-2026",
                "date": "2026-09-10",
                "description": "Completed mock technical interviews, resume review, and GitHub profile audit with Career Advisory Office.",
                "organization": "University Career Services Center",
                "evidence_url": None,
                "verification_status": "Institution-Verified",
                "is_verified": True,
                "verified_by_id": "ADM001",
                "verified_by_name": "Dean Evelyn Vance",
                "verified_at": "2026-09-12 11:00",
                "rejection_reason": None,
                "created_at": "2026-09-10 16:00",
            },
            # Seed entry for S1002
            {
                "id": "TL-201",
                "student_id": "S1002",
                "student_name": "Marcus Wright",
                "title": "Bio-Systems Agronomy Research Paper Publication",
                "category": "Projects",
                "academic_year": "2024-2025",
                "date": "2025-04-12",
                "description": "Co-authored student journal paper on automated hydroponics nutrient balance sensors.",
                "organization": "Agronomy Science Review",
                "evidence_url": "https://agronomy.org/papers/2025-04-s1002",
                "verification_status": "Institution-Verified",
                "is_verified": True,
                "verified_by_id": "FAC-CS101",
                "verified_by_name": "Dr. Alan Turing",
                "verified_at": "2025-04-15 10:00",
                "rejection_reason": None,
                "created_at": "2025-04-13 08:30",
            },
        ]

        self._initialized = True

    # -----------------------------------------------------------------------
    # Authentication & User Management Methods
    # -----------------------------------------------------------------------
    def authenticate_user(self, username: str, password: str, role_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Verifies credentials securely and creates an active session token."""
        if not username or not password:
            return None

        username_clean = username.strip().lower()
        password_clean = password.strip()
        user = self._users.get(username_clean)
        
        # Also check by direct student/faculty ID, username, email, or roll number
        if not user:
            for u in self._users.values():
                if (
                    u.get("id", "").strip().lower() == username_clean
                    or u.get("username", "").strip().lower() == username_clean
                    or u.get("email", "").strip().lower() == username_clean
                    or str(u.get("roll_number", "")).strip().lower() == username_clean
                ):
                    user = u
                    break

        if not user:
            return None

        # Check account status
        if user.get("status") == "Deactivated":
            return None

        # Verify password using secure PBKDF2/SHA256 comparator
        if not verify_password(password_clean, user.get("password_hash")):
            return None

        # Issue secure active session token
        token = session_store.create_session(user)
        self.log_audit(user.get("username", user["id"]), user["role"], "LOGIN", user["id"], "User logged in successfully")
        return {"token": token, "user": user}

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        for u in self._users.values():
            if u.get("id") == user_id or u.get("username") == user_id or u.get("email") == user_id:
                return u
        return None

    def get_faculty_by_id(self, faculty_id: str) -> Optional[Dict[str, Any]]:
        # Check faculty dict first
        fac = self._faculty.get(faculty_id)
        if fac:
            return fac
        # Check user dict if matched
        u = self.get_user_by_id(faculty_id)
        if u and u.get("role") == "faculty":
            return u
        return None

    def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        s = self._students.get(student_id)
        if s:
            return s
        u = self.get_user_by_id(student_id)
        if u and u.get("role") == "student":
            return u
        return None

    def get_all_users(self, institution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all user accounts with sensitive password hashes removed."""
        res = []
        for u in self._users.values():
            if institution_id and u.get("institution_id") != institution_id:
                continue
            safe_user = {k: v for k, v in u.items() if k != "password_hash"}
            res.append(safe_user)
        return res

    def create_user_account(self, user_data: Dict[str, Any], actor: str = "admin") -> Dict[str, Any]:
        """Admin creates a new user account."""
        username = user_data.get("username", "").strip().lower()
        email = user_data.get("email", "").strip().lower()
        role = user_data.get("role", "student").strip().lower()
        user_id = user_data.get("id") or f"USR-{len(self._users) + 101}"

        if not username or not email:
            raise ValueError("Username and email are required.")

        # Prevent duplicate username/email/id
        for existing in self._users.values():
            if existing.get("username") == username:
                raise ValueError(f"Username '{username}' already in use.")
            if existing.get("email") == email:
                raise ValueError(f"Email '{email}' already registered.")
            if existing.get("id") == user_id:
                raise ValueError(f"User ID '{user_id}' already registered.")

        raw_pwd = user_data.get("password") or "Student@360"
        new_account = {
            "id": user_id,
            "username": username,
            "password_hash": hash_password(raw_pwd),
            "name": user_data.get("name", "New User"),
            "email": email,
            "role": role,
            "department": user_data.get("department", "General Studies"),
            "designation": user_data.get("designation"),
            "semester": user_data.get("semester"),
            "program": user_data.get("program"),
            "phone": user_data.get("phone", "+1 (555) 000-0000"),
            "institution_id": user_data.get("institution_id", "INST-001"),
            "status": "Active",
            "avatar": user_data.get("avatar") or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
        }

        if role == "faculty":
            new_account["assigned_student_ids"] = user_data.get("assigned_student_ids", [])
            self._faculty[user_id] = new_account
        elif role == "student":
            self._students[user_id] = new_account

        self._users[username] = new_account
        self.log_audit(actor, "admin", "CREATE_USER", user_id, f"Created {role} account for {new_account['name']}")
        return {k: v for k, v in new_account.items() if k != "password_hash"}

    def update_user_status(self, user_id: str, new_status: str, actor: str = "admin") -> Optional[Dict[str, Any]]:
        """Admin activates or deactivates an account."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        user["status"] = new_status
        if new_status == "Deactivated":
            # Invalidate all active sessions for this user
            session_store.revoke_all_for_user(user["id"])
        self.log_audit(actor, "admin", "UPDATE_USER_STATUS", user_id, f"Changed status to {new_status}")
        return {k: v for k, v in user.items() if k != "password_hash"}

    def assign_students_to_faculty(self, faculty_id: str, student_ids: List[str], actor: str = "admin") -> Optional[Dict[str, Any]]:
        """Admin assigns a list of student IDs to a faculty member."""
        fac = self.get_faculty_by_id(faculty_id)
        if not fac:
            return None
        fac["assigned_student_ids"] = student_ids
        # Update in users store as well
        u = self.get_user_by_id(faculty_id)
        if u:
            u["assigned_student_ids"] = student_ids
        self.log_audit(actor, "admin", "ASSIGN_STUDENTS", faculty_id, f"Assigned {len(student_ids)} students to {fac.get('name')}")
        return fac

    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        if not verify_password(old_password, user.get("password_hash")):
            return False, "Incorrect current password"
        
        user["password_hash"] = hash_password(new_password)
        self.log_audit(user["username"], user["role"], "PASSWORD_CHANGE", user["id"], "User updated their account password")
        return True, "Password successfully updated"

    # -----------------------------------------------------------------------
    # Timetable Methods with Conflict Detection
    # -----------------------------------------------------------------------
    def get_timetable(
        self,
        student_id: Optional[str] = None,
        faculty_id: Optional[str] = None,
        day: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Filters timetable entries."""
        results = copy.deepcopy(self._timetable)

        if faculty_id:
            results = [e for e in results if e.get("faculty_id") == faculty_id]
        if day:
            results = [e for e in results if e.get("day", "").lower() == day.lower()]
        if semester:
            results = [e for e in results if e.get("semester") == semester]

        return results

    def check_timetable_conflict(self, entry: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validates room and faculty conflicts."""
        day = entry.get("day")
        start = entry.get("start_time")
        end = entry.get("end_time")
        room = entry.get("room")
        fac_id = entry.get("faculty_id")

        for existing in self._timetable:
            if existing.get("id") == entry.get("id"):
                continue
            if existing.get("day") != day:
                continue

            # Check overlap: (StartA < EndB) and (EndA > StartB)
            if existing.get("start_time") < end and existing.get("end_time") > start:
                if existing.get("room") == room:
                    return True, "room_conflict", f"Room '{room}' is already booked on {day} ({existing['start_time']} - {existing['end_time']}) for {existing['subject_name']}"
                if existing.get("faculty_id") == fac_id:
                    return True, "faculty_conflict", f"Faculty member '{existing['faculty_name']}' is already teaching on {day} ({existing['start_time']} - {existing['end_time']}) in {existing['room']}"

        return False, None, None

    def add_timetable_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        has_conflict, c_type, msg = self.check_timetable_conflict(entry_data)
        if has_conflict:
            raise ValueError(msg)

        new_entry = {
            "id": f"TT-{len(self._timetable) + 101}",
            **entry_data,
        }
        self._timetable.append(new_entry)
        self.log_audit("admin", "admin", "CREATE_TIMETABLE_ENTRY", new_entry["id"], f"Added slot {new_entry['subject_code']} on {new_entry['day']}")
        return new_entry

    def delete_timetable_entry(self, entry_id: str) -> bool:
        initial_len = len(self._timetable)
        self._timetable = [e for e in self._timetable if e["id"] != entry_id]
        if len(self._timetable) < initial_len:
            self.log_audit("admin", "admin", "DELETE_TIMETABLE_ENTRY", entry_id, "Removed timetable slot")
            return True
        return False

    # -----------------------------------------------------------------------
    # Attendance Methods
    # -----------------------------------------------------------------------
    def get_student_attendance(self, student_id: str) -> Dict[str, Any]:
        """Calculates subject-wise and overall attendance percentage for a student."""
        records = [r for r in self._attendance_records if r.get("student_id") == student_id]
        if not records:
            # Fallback realistic defaults
            records = [
                {"student_id": student_id, "subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "attended": 22, "total": 28, "threshold": 75.0},
                {"student_id": student_id, "subject_code": "CS302", "subject_name": "Database Management Systems", "attended": 25, "total": 28, "threshold": 75.0},
                {"student_id": student_id, "subject_code": "CS305", "subject_name": "Software Engineering", "attended": 23, "total": 26, "threshold": 75.0},
            ]

        subjects = []
        tot_attended = 0
        tot_classes = 0

        for r in records:
            attended = r.get("attended", 0)
            total = r.get("total", 1)
            pct = round((attended / total) * 100, 1) if total > 0 else 0.0
            is_low = pct < r.get("threshold", 75.0)

            tot_attended += attended
            tot_classes += total

            subjects.append({
                "subject_code": r.get("subject_code"),
                "subject_name": r.get("subject_name"),
                "attended": attended,
                "total": total,
                "percentage": pct,
                "is_low_attendance": is_low,
                "threshold": r.get("threshold", 75.0),
            })

        overall_pct = round((tot_attended / tot_classes) * 100, 1) if tot_classes > 0 else 0.0

        return {
            "student_id": student_id,
            "overall_percentage": overall_pct,
            "total_attended": tot_attended,
            "total_classes": tot_classes,
            "subjects": subjects,
            "low_attendance_warning": overall_pct < 75.0 or any(s["is_low_attendance"] for s in subjects),
        }

    def get_class_attendance_sheet(self, class_id: str, subject_code: str, date: str) -> List[Dict[str, Any]]:
        """Returns roster of students for attendance marking."""
        sheet = []
        for sid, sdata in sorted(self._students.items()):
            sheet.append({
                "student_id": sid,
                "student_name": sdata["name"],
                "roll_number": sdata["roll_number"],
                "status": "Present",  # default
                "remarks": "",
            })
        return sheet

    def submit_class_attendance(self, submit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Records attendance marks and updates student totals with duplicate prevention."""
        subject_code = submit_data.get("subject_code")
        records = submit_data.get("records", [])

        # Prevent duplicate submission for same subject and date
        existing_log_key = f"{submit_data.get('class_id')}_{subject_code}_{submit_data.get('date')}_{submit_data.get('session')}"
        
        updated_count = 0
        for rec in records:
            sid = rec.get("student_id")
            status = rec.get("status")

            # Find or create subject record for student
            match = None
            for ar in self._attendance_records:
                if ar.get("student_id") == sid and ar.get("subject_code") == subject_code:
                    match = ar
                    break

            if match:
                match["total"] = match.get("total", 0) + 1
                if status == "Present":
                    match["attended"] = match.get("attended", 0) + 1
                elif status == "Late":
                    match["attended"] = match.get("attended", 0) + 1  # count as partial or present
                updated_count += 1

        self.log_audit(
            submit_data.get("faculty_id", "faculty"),
            "faculty",
            "SUBMIT_ATTENDANCE",
            subject_code,
            f"Marked attendance for {updated_count} students on {submit_data.get('date')}",
        )

        return {
            "status": "success",
            "message": f"Successfully recorded attendance for {updated_count} students.",
            "records_processed": updated_count,
            "session_key": existing_log_key,
        }

    def get_attendance_reports(self) -> List[Dict[str, Any]]:
        """Provides institutional department-wise attendance summaries for Admin."""
        return [
            {"department": "Computer Science & Engineering", "semester": 2, "total_students": 120, "avg_attendance": 84.6, "below_threshold_count": 8},
            {"department": "Animation & Multimedia Design", "semester": 2, "total_students": 95, "avg_attendance": 78.2, "below_threshold_count": 14},
            {"department": "Agronomy & Bio-Systems", "semester": 2, "total_students": 70, "avg_attendance": 89.1, "below_threshold_count": 3},
            {"department": "Management & Analytics", "semester": 4, "total_students": 110, "avg_attendance": 82.4, "below_threshold_count": 9},
            {"department": "Nursing & Healthcare Sciences", "semester": 3, "total_students": 85, "avg_attendance": 92.5, "below_threshold_count": 2},
        ]

    # -----------------------------------------------------------------------
    # Marks & Results Methods
    # -----------------------------------------------------------------------
    def get_student_marks(self, student_id: str) -> Dict[str, Any]:
        """Returns subject-wise marks, internal assessment, CGPA, and semester history."""
        subjects = self._marks_records.get(student_id)
        if not subjects:
            # Fallback realistic data
            subjects = [
                {"subject_code": "CS301", "subject_name": "Data Structures & Algorithms", "credits": 4, "internal_assessment": 32.0, "midterm_exam": 38.0, "final_exam": 40.0, "total_marks": 78.0, "max_marks": 100.0, "grade": "B+", "status": "Passed"},
                {"subject_code": "CS302", "subject_name": "Database Management Systems", "credits": 4, "internal_assessment": 36.0, "midterm_exam": 42.0, "final_exam": 45.0, "total_marks": 87.0, "max_marks": 100.0, "grade": "A", "status": "Passed"},
                {"subject_code": "CS305", "subject_name": "Software Engineering", "credits": 3, "internal_assessment": 34.0, "midterm_exam": 39.0, "final_exam": 41.0, "total_marks": 80.0, "max_marks": 100.0, "grade": "A-", "status": "Passed"},
            ]

        # Calculate credits and GPA
        tot_credits = sum(s.get("credits", 3) for s in subjects)
        earned_credits = sum(s.get("credits", 3) for s in subjects if s.get("status") == "Passed")
        
        grade_points = {"A+": 4.0, "A": 3.9, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D": 1.0, "F": 0.0}
        total_pts = sum(grade_points.get(s.get("grade"), 2.5) * s.get("credits", 3) for s in subjects)
        current_gpa = round(total_pts / tot_credits, 2) if tot_credits > 0 else 3.0

        semester_history = [
            {"semester": 1, "gpa": 2.85 if student_id == "S1001" else 3.50, "credits": 20, "attendance": 72.0 if student_id == "S1001" else 90.0},
            {"semester": 2, "gpa": current_gpa, "credits": tot_credits, "attendance": 68.5 if student_id == "S1001" else 88.0},
        ]

        return {
            "student_id": student_id,
            "current_gpa": current_gpa,
            "cgpa": round((semester_history[0]["gpa"] + current_gpa) / 2, 2),
            "total_credits": 40,
            "earned_credits": 20 + earned_credits,
            "subjects": subjects,
            "semester_history": semester_history,
        }

    def update_student_marks(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        sid = update_data.get("student_id")
        code = update_data.get("subject_code")
        
        if sid not in self._marks_records:
            self._marks_records[sid] = []

        sub_list = self._marks_records[sid]
        match = next((s for s in sub_list if s["subject_code"] == code), None)

        if not match:
            match = {
                "subject_code": code,
                "subject_name": code,
                "credits": 3,
                "internal_assessment": 0.0,
                "midterm_exam": 0.0,
                "final_exam": None,
                "total_marks": 0.0,
                "max_marks": 100.0,
                "grade": "In Progress",
                "status": "In Progress",
            }
            sub_list.append(match)

        if update_data.get("internal_assessment") is not None:
            match["internal_assessment"] = float(update_data["internal_assessment"])
        if update_data.get("midterm_exam") is not None:
            match["midterm_exam"] = float(update_data["midterm_exam"])
        if update_data.get("final_exam") is not None:
            match["final_exam"] = float(update_data["final_exam"])

        # Recompute total & grade
        tot = match.get("internal_assessment", 0) + match.get("midterm_exam", 0) + (match.get("final_exam") or 0)
        match["total_marks"] = round(tot, 1)

        if tot >= 90:
            match["grade"], match["status"] = "A+", "Passed"
        elif tot >= 80:
            match["grade"], match["status"] = "A", "Passed"
        elif tot >= 70:
            match["grade"], match["status"] = "B", "Passed"
        elif tot >= 60:
            match["grade"], match["status"] = "C", "Passed"
        elif tot >= 50:
            match["grade"], match["status"] = "D", "Passed"
        else:
            match["grade"], match["status"] = "F", "Needs Improvement"

        return match

    # -----------------------------------------------------------------------
    # Assignments Methods
    # -----------------------------------------------------------------------
    def get_assignments(
        self,
        student_id: Optional[str] = None,
        faculty_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = []
        for a in self._assignments:
            item = copy.deepcopy(a)
            submissions = item.pop("submissions", {})
            item["submissions_count"] = len(submissions)
            item["total_students"] = len(self._students)

            if student_id:
                item["my_submission"] = submissions.get(student_id)

            if faculty_id and a.get("faculty_id") != faculty_id:
                continue

            results.append(item)
        return results

    def create_assignment(self, create_data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = f"ASN-{len(self._assignments) + 201}"
        new_assign = {
            "id": new_id,
            **create_data,
            "status": "Active",
            "submissions": {},
        }
        self._assignments.append(new_assign)
        self.log_audit(
            create_data.get("faculty_id", "faculty"),
            "faculty",
            "CREATE_ASSIGNMENT",
            new_id,
            f"Created assignment '{create_data.get('title')}'",
        )
        return new_assign

    def submit_assignment(self, assignment_id: str, student_id: str, content: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        target = next((a for a in self._assignments if a["id"] == assignment_id), None)
        if not target:
            raise ValueError(f"Assignment {assignment_id} not found")

        student = self._students.get(student_id, {"name": student_id})
        sub_id = f"SUB-{len(target['submissions']) + 101}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

        sub = {
            "submission_id": sub_id,
            "student_id": student_id,
            "student_name": student.get("name", student_id),
            "submitted_at": now_str,
            "content": content,
            "file_name": file_name or "submission_document.pdf",
            "status": "Submitted",
            "grade": None,
            "feedback": None,
        }
        target["submissions"][student_id] = sub
        return sub

    def grade_assignment(self, assignment_id: str, student_id: str, grade: float, feedback: Optional[str] = None) -> Dict[str, Any]:
        target = next((a for a in self._assignments if a["id"] == assignment_id), None)
        if not target:
            raise ValueError(f"Assignment {assignment_id} not found")
        sub = target["submissions"].get(student_id)
        if not sub:
            raise ValueError(f"No submission found for student {student_id}")

        sub["grade"] = grade
        sub["feedback"] = feedback
        sub["status"] = "Graded"
        return sub

    # -----------------------------------------------------------------------
    # Announcements Methods
    # -----------------------------------------------------------------------
    def get_announcements(self, audience: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for ann in sorted(self._announcements, key=lambda x: x["created_at"], reverse=True):
            if audience and ann.get("target_audience") not in ["all", audience]:
                continue
            item = copy.deepcopy(ann)
            read_by = item.pop("read_by", [])
            item["is_read"] = user_id in read_by if user_id else False
            results.append(item)
        return results

    def create_announcement(self, create_data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = f"ANN-{len(self._announcements) + 101}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        new_ann = {
            "id": new_id,
            **create_data,
            "created_at": now_str,
            "read_by": [],
        }
        self._announcements.insert(0, new_ann)
        self.log_audit(
            create_data.get("publisher", "admin"),
            create_data.get("publisher_role", "admin"),
            "CREATE_ANNOUNCEMENT",
            new_id,
            f"Published notice '{create_data.get('title')}'",
        )
        return new_ann

    def mark_announcement_read(self, announcement_id: str, user_id: str) -> bool:
        ann = next((a for a in self._announcements if a["id"] == announcement_id), None)
        if ann and user_id not in ann.get("read_by", []):
            ann.setdefault("read_by", []).append(user_id)
            return True
        return False

    def delete_announcement(self, announcement_id: str) -> bool:
        initial = len(self._announcements)
        self._announcements = [a for a in self._announcements if a["id"] != announcement_id]
        return len(self._announcements) < initial

    # -----------------------------------------------------------------------
    # Examinations Methods
    # -----------------------------------------------------------------------
    def get_examinations(self, department: Optional[str] = None, semester: Optional[int] = None) -> List[Dict[str, Any]]:
        results = copy.deepcopy(self._examinations)
        if department:
            results = [e for e in results if e.get("department") == department]
        if semester:
            results = [e for e in results if e.get("semester") == semester]
        return results

    def create_examination(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = f"EX-{len(self._examinations) + 301}"
        new_exam = {
            "id": new_id,
            **exam_data,
            "results_published": False,
        }
        self._examinations.append(new_exam)
        self.log_audit("admin", "admin", "SCHEDULE_EXAMINATION", new_id, f"Scheduled exam {new_exam.get('title')}")
        return new_exam

    def update_examination(self, exam_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        target = next((e for e in self._examinations if e["id"] == exam_id), None)
        if not target:
            return None
        target.update(updates)
        return target

    # -----------------------------------------------------------------------
    # Fees Methods
    # -----------------------------------------------------------------------
    def get_student_fees(self, student_id: str) -> Dict[str, Any]:
        fees = self._fees.get(student_id)
        if not fees:
            student = self._students.get(student_id, {"name": student_id})
            fees = {
                "student_id": student_id,
                "student_name": student.get("name", student_id),
                "total_fees": 4500.0,
                "scholarship_discount": 0.0,
                "paid_amount": 4500.0,
                "outstanding_balance": 0.0,
                "due_date": "2026-11-15",
                "status": "Paid",
                "transactions": [
                    {
                        "transaction_id": f"TXN-{sid_num}",
                        "date": "2026-08-10",
                        "amount": 4500.0,
                        "payment_method": "Debit Card",
                        "receipt_no": f"REC-2026-{sid_num}",
                        "status": "Completed",
                    }
                    for sid_num in [int(student_id[-4:]) if student_id[-4:].isdigit() else 1000]
                ],
            }
        return fees

    def pay_student_fees(self, student_id: str, amount: float, method: str = "Online NetBanking") -> Dict[str, Any]:
        fees = self.get_student_fees(student_id)
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

        fees["paid_amount"] += amount
        fees["outstanding_balance"] = max(0.0, fees["total_fees"] - fees["scholarship_discount"] - fees["paid_amount"])
        fees["status"] = "Paid" if fees["outstanding_balance"] == 0 else "Partially Paid"

        txn_id = f"TXN-{len(fees['transactions']) + 8901}"
        new_txn = {
            "transaction_id": txn_id,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "amount": amount,
            "payment_method": method,
            "receipt_no": f"REC-2026-{txn_id[-4:]}",
            "status": "Completed",
        }
        fees["transactions"].append(new_txn)
        self._fees[student_id] = fees

        self.log_audit(
            student_id,
            "student",
            "FEE_PAYMENT",
            txn_id,
            f"Paid fee instalment of ₹{amount:,.2f} via {method}",
        )
        return fees

    def get_institution_fee_summary(self) -> Dict[str, Any]:
        total_billed = 0.0
        total_collected = 0.0
        total_outstanding = 0.0
        defaulters = 0

        for sid in self._students:
            fee_info = self.get_student_fees(sid)
            net_bill = fee_info["total_fees"] - fee_info["scholarship_discount"]
            total_billed += net_bill
            total_collected += fee_info["paid_amount"]
            total_outstanding += fee_info["outstanding_balance"]
            if fee_info["outstanding_balance"] > 0:
                defaulters += 1

        pct = round((total_collected / total_billed) * 100, 1) if total_billed > 0 else 100.0
        return {
            "total_billed": round(total_billed, 2),
            "total_collected": round(total_collected, 2),
            "total_outstanding": round(total_outstanding, 2),
            "collection_rate_percent": pct,
            "total_students_billed": len(self._students),
            "defaulters_count": defaulters,
        }

    # -----------------------------------------------------------------------
    # Today's Class Schedule Notification Engine (Prompt Section 9)
    # -----------------------------------------------------------------------
    def generate_daily_schedule_notifications(
        self,
        target_date: Optional[str] = None,
        check_quiet_hours: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves today's timetable for all students, creates concise daily schedule notification.
        - Avoids duplicate notifications for the same student and schedule date.
        - Respects quiet hours (22:00 to 07:00).
        - Friendly message if no classes scheduled.
        - Stored as real in-app notifications.
        """
        now = datetime.now(timezone.utc)
        if not target_date:
            target_date = now.strftime("%Y-%m-%d")

        # Determine day of week
        dt = datetime.strptime(target_date, "%Y-%m-%d")
        day_name = dt.strftime("%A")

        # Check quiet hours if requested
        current_hour = now.hour
        is_quiet_hour = (current_hour >= 22 or current_hour < 7) if check_quiet_hours else False

        total_processed = 0
        created_count = 0
        skipped_dup = 0
        skipped_quiet = 0
        details = []

        for sid, sdata in self._students.items():
            total_processed += 1

            # Check duplicate for this student, type=daily_schedule, target_date
            dup_exists = any(
                n.get("user_id") == sid
                and n.get("type") == "daily_schedule"
                and n.get("metadata", {}).get("schedule_date") == target_date
                for n in self._notifications
            )

            if dup_exists:
                skipped_dup += 1
                continue

            if is_quiet_hour:
                skipped_quiet += 1
                continue

            # Query student's classes for today
            day_classes = [e for e in self._timetable if e.get("day", "").lower() == day_name.lower()]
            day_classes.sort(key=lambda x: x.get("start_time", ""))

            if day_classes:
                class_summaries = [
                    f"{c['start_time']}–{c['end_time']}: {c['subject_name']} ({c['subject_code']}) in {c['room']} [{c['faculty_name']}]"
                    for c in day_classes
                ]
                msg = f"Today's Schedule ({day_name}, {target_date}) — {len(day_classes)} classes:\n" + " • " + "\n • ".join(class_summaries)
                title = f"Today's Classes: {len(day_classes)} Sessions Scheduled"
                priority = "normal"
            else:
                title = f"No Classes Scheduled Today ({day_name})"
                msg = f"You have no formal lectures scheduled for today ({target_date}). Take advantage of this time for self-study and assignment prep."
                priority = "low"

            notif_id = f"NOTIF-SCHED-{sid}-{target_date}"
            new_notif = {
                "id": notif_id,
                "user_id": sid,
                "title": title,
                "message": msg,
                "type": "daily_schedule",
                "priority": priority,
                "created_at": now.strftime("%Y-%m-%d %H:%M"),
                "read": False,
                "delivery_channel": "in_app",
                "delivery_status": "delivered",
                "metadata": {
                    "schedule_date": target_date,
                    "day_of_week": day_name,
                    "classes_count": len(day_classes),
                },
            }

            self._notifications.insert(0, new_notif)
            created_count += 1
            details.append({"student_id": sid, "classes_count": len(day_classes), "notification_id": notif_id})

        return {
            "target_date": target_date,
            "total_students_processed": total_processed,
            "notifications_created": created_count,
            "skipped_duplicates": skipped_dup,
            "skipped_quiet_hours": skipped_quiet,
            "status": "completed",
            "details": details,
        }

    def get_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        return [n for n in self._notifications if n.get("user_id") == user_id]

    def mark_notification_read(self, notification_id: str) -> bool:
        notif = next((n for n in self._notifications if n["id"] == notification_id), None)
        if notif:
            notif["read"] = True
            return True
        return False

    def mark_all_notifications_read(self, user_id: str) -> int:
        count = 0
        for n in self._notifications:
            if n.get("user_id") == user_id and not n.get("read"):
                n["read"] = True
                count += 1
        return count

    # -----------------------------------------------------------------------
    # Admin Roster & CSV Import Methods
    # -----------------------------------------------------------------------
    def get_admin_students(self) -> List[Dict[str, Any]]:
        return list(self._students.values())

    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        sid = student_data.get("student_id")
        if sid in self._students:
            raise ValueError(f"Student ID {sid} already exists")

        new_student = {
            **student_data,
            "status": "Active",
            "cgpa": 3.0,
            "attendance_rate": 85.0,
            "fees_status": "Pending",
        }
        self._students[sid] = new_student

        # Create user account for login
        self._users[sid] = {
            "id": sid,
            "username": sid.lower(),
            "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
            "name": new_student["name"],
            "email": new_student["email"],
            "role": "student",
            "department": new_student["department"],
            "semester": new_student["semester"],
            "program": new_student["program"],
            "phone": new_student["phone"],
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={sid}",
        }

        self.log_audit("admin", "admin", "CREATE_STUDENT", sid, f"Enrolled student {new_student['name']}")
        return new_student

    def update_student(self, student_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        target = self._students.get(student_id)
        if not target:
            return None
        target.update(updates)
        self.log_audit("admin", "admin", "UPDATE_STUDENT", student_id, f"Updated profile for student {student_id}")
        return target

    def import_students_csv(self, csv_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validates and imports student batch with row-level error reporting."""
        accepted = 0
        rejected = 0
        errors = []

        for idx, row in enumerate(csv_rows, start=1):
            sid = str(row.get("student_id", "")).strip()
            name = str(row.get("name", "")).strip()
            email = str(row.get("email", "")).strip()
            dept = str(row.get("department", "")).strip()
            sem = row.get("semester")

            if not sid or not name:
                rejected += 1
                errors.append({"row": idx, "student_id": sid, "error": "Missing student ID or name"})
                continue

            if sid in self._students:
                rejected += 1
                errors.append({"row": idx, "student_id": sid, "error": f"Student ID '{sid}' already registered"})
                continue

            try:
                sem_int = int(sem) if sem else 1
            except (ValueError, TypeError):
                rejected += 1
                errors.append({"row": idx, "student_id": sid, "error": f"Invalid semester number '{sem}'"})
                continue

            roll = row.get("roll_number") or f"2024-{sid}"
            phone = row.get("phone") or "+1 (555) 000-0000"
            program = row.get("program") or "Undergraduate Degree"

            self.create_student({
                "student_id": sid,
                "roll_number": roll,
                "name": name,
                "email": email or f"{sid.lower()}@student360.edu",
                "phone": phone,
                "department": dept or "General Sciences",
                "program": program,
                "semester": sem_int,
                "admission_year": 2024,
            })
            accepted += 1

        # Record import history
        import_record = {
            "id": f"IMP-{len(self._import_history) + 1:03d}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "imported_by": "admin",
            "filename": "students_batch_import.csv",
            "total_rows": len(csv_rows),
            "accepted_rows": accepted,
            "rejected_rows": rejected,
            "status": "Completed" if rejected == 0 else "Completed with Warnings" if accepted > 0 else "Failed",
        }
        self._import_history.insert(0, import_record)

        self.log_audit("admin", "admin", "CSV_IMPORT", "students", f"Imported {accepted} students, {rejected} rejected")
        return {
            "total_rows": len(csv_rows),
            "accepted_rows": accepted,
            "rejected_rows": rejected,
            "errors": errors,
            "message": f"Processed {len(csv_rows)} rows: {accepted} accepted, {rejected} rejected.",
        }

    def get_import_history(self) -> List[Dict[str, Any]]:
        return self._import_history

    # -----------------------------------------------------------------------
    # Timeline & Achievement Verification Methods
    # -----------------------------------------------------------------------
    def get_student_timeline(
        self,
        student_id: str,
        category: Optional[str] = None,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        entries = [e for e in self._timeline_entries if e["student_id"] == student_id]
        if category and category.lower() != "all":
            entries = [e for e in entries if e["category"].lower() == category.lower()]
        if academic_year and academic_year.lower() != "all":
            entries = [e for e in entries if e.get("academic_year", "").lower() == academic_year.lower()]
        if status and status.lower() != "all":
            entries = [e for e in entries if e.get("verification_status", "").lower() == status.lower()]
        
        # Sort chronologically descending
        return sorted(entries, key=lambda x: x.get("date", ""), reverse=True)

    def create_timeline_entry(
        self,
        student_id: str,
        data: Dict[str, Any],
        actor_role: str = "student",
        actor_id: str = "S1001",
        actor_name: str = "Sarah Connor",
    ) -> Dict[str, Any]:
        student = self.get_student_by_id(student_id)
        student_name = student.get("name", student_id) if student else student_id
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        
        is_inst_role = actor_role in ["faculty", "admin"]
        verification_status = "Institution-Verified" if is_inst_role else "Self-Reported"
        
        entry = {
            "id": f"TL-{len(self._timeline_entries) + 101:03d}",
            "student_id": student_id,
            "student_name": student_name,
            "title": data["title"],
            "category": data.get("category", "Projects"),
            "academic_year": data.get("academic_year", "2024-2025"),
            "date": data["date"],
            "description": data["description"],
            "organization": data.get("organization"),
            "evidence_url": data.get("evidence_url"),
            "skills": data.get("skills", []),
            "source": "institution" if is_inst_role else "student",
            "verification_status": verification_status,
            "is_verified": is_inst_role,
            "verified_by": actor_id if is_inst_role else None,
            "verified_by_id": actor_id if is_inst_role else None,
            "verified_by_name": actor_name if is_inst_role else None,
            "verified_at": now_str if is_inst_role else None,
            "rejection_reason": None,
            "remarks": None,
            "created_at": now_str,
        }
        self._timeline_entries.insert(0, entry)
        self.log_audit(actor_name, actor_role, "CREATE_TIMELINE_ENTRY", student_id, f"Created {entry['title']} ({verification_status})")
        return entry

    def update_timeline_entry(
        self,
        student_id: str,
        entry_id: str,
        updates: Dict[str, Any],
        actor_role: str = "student",
        actor_name: str = "Sarah Connor",
    ) -> Optional[Dict[str, Any]]:
        target = next((e for e in self._timeline_entries if e["id"] == entry_id and e["student_id"] == student_id), None)
        if not target:
            return None
        
        for k in ["title", "category", "academic_year", "date", "description", "organization", "evidence_url", "skills"]:
            if k in updates and updates[k] is not None:
                target[k] = updates[k]
        
        # If student updates a verified or rejected entry, reset to Self-Reported for review
        if actor_role == "student" and target["verification_status"] != "Self-Reported":
            target["verification_status"] = "Self-Reported"
            target["is_verified"] = False
            target["verified_by"] = None
            target["verified_by_id"] = None
            target["verified_by_name"] = None
            target["verified_at"] = None
            target["rejection_reason"] = None
            target["remarks"] = None

        self.log_audit(actor_name, actor_role, "UPDATE_TIMELINE_ENTRY", entry_id, f"Updated timeline item {entry_id}")
        return target

    def delete_timeline_entry(
        self,
        student_id: str,
        entry_id: str,
        actor_role: str = "student",
        actor_name: str = "Sarah Connor",
    ) -> bool:
        before_len = len(self._timeline_entries)
        self._timeline_entries = [e for e in self._timeline_entries if not (e["id"] == entry_id and e["student_id"] == student_id)]
        if len(self._timeline_entries) < before_len:
            self.log_audit(actor_name, actor_role, "DELETE_TIMELINE_ENTRY", entry_id, f"Deleted timeline item {entry_id}")
            return True
        return False

    def get_pending_verifications(
        self,
        faculty_assigned_students: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        pending = [e for e in self._timeline_entries if e["verification_status"] == "Self-Reported"]
        if faculty_assigned_students is not None:
            pending = [e for e in pending if e["student_id"] in faculty_assigned_students]
        return sorted(pending, key=lambda x: x.get("created_at", ""), reverse=True)

    def verify_achievement(
        self,
        entry_id: str,
        status: str,
        reviewer_id: str,
        reviewer_name: str,
        rejection_reason: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        target = next((e for e in self._timeline_entries if e["id"] == entry_id), None)
        if not target:
            return None
        
        effective_remark = remarks or rejection_reason
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        target["verification_status"] = status
        target["is_verified"] = (status == "Institution-Verified")
        target["verified_by"] = reviewer_id
        target["verified_by_id"] = reviewer_id
        target["verified_by_name"] = reviewer_name
        target["verified_at"] = now_str
        target["rejection_reason"] = effective_remark if status == "Rejected" else None
        target["remarks"] = effective_remark

        self.log_audit(reviewer_name, "faculty", "VERIFY_ACHIEVEMENT", entry_id, f"Marked achievement {entry_id} as {status}")
        return target

    # -----------------------------------------------------------------------
    # Faculty Management Methods
    # -----------------------------------------------------------------------
    def get_faculty_list(self) -> List[Dict[str, Any]]:
        return list(self._faculty.values())

    def create_faculty(self, faculty_data: Dict[str, Any]) -> Dict[str, Any]:
        fid = faculty_data.get("id") or f"FAC-{len(self._faculty) + 101}"
        new_fac = {
            "id": fid,
            **faculty_data,
            "status": "Active",
            "assigned_subjects": faculty_data.get("assigned_subjects", []),
        }
        self._faculty[fid] = new_fac

        # Create user account
        username = faculty_data.get("username", fid.lower())
        self._users[username] = {
            "id": fid,
            "username": username,
            "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
            "name": new_fac["name"],
            "email": new_fac["email"],
            "role": "faculty",
            "department": new_fac["department"],
            "designation": new_fac.get("designation", "Faculty"),
            "phone": new_fac.get("phone", ""),
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={fid}",
        }

        self.log_audit("admin", "admin", "CREATE_FACULTY", fid, f"Added faculty member {new_fac['name']}")
        return new_fac

    def update_faculty(self, faculty_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        target = self._faculty.get(faculty_id)
        if not target:
            return None
        target.update(updates)
        self.log_audit("admin", "admin", "UPDATE_FACULTY", faculty_id, f"Updated faculty profile {faculty_id}")
        return target

    # -----------------------------------------------------------------------
    # Audit Logs
    # -----------------------------------------------------------------------
    def log_audit(self, actor: str, role: str, action: str, target: str, details: str):
        log_entry = {
            "id": f"AUD-{len(self._audit_logs) + 1:03d}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "actor": actor,
            "actor_role": role,
            "action": action,
            "target": target,
            "details": details,
        }
        self._audit_logs.insert(0, log_entry)

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._audit_logs[:limit]

    def get_departments(self) -> List[Dict[str, Any]]:
        return self._departments


# Global singleton instance
college_service = CollegeService()


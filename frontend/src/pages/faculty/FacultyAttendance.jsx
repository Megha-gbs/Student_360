import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Calendar,
  Clock,
  UserCheck,
  UserX,
  AlertCircle,
  CheckCircle2,
  Save,
  Filter,
} from 'lucide-react';
import { attendanceApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function FacultyAttendance() {
  const { user } = useAuth();
  const [classId, setClassId] = useState('CS-Sem2');
  const [subjectCode, setSubjectCode] = useState('CS301');
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [session, setSession] = useState('Morning');
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });

  const loadAttendanceSheet = async () => {
    setLoading(true);
    setStatusMessage({ text: '', type: '' });
    try {
      const data = await attendanceApi.getClassAttendanceSheet({
        class_id: classId,
        subject_code: subjectCode,
        date: date,
      });
      setStudents(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAttendanceSheet();
  }, [classId, subjectCode, date]);

  const handleStatusChange = (studentId, newStatus) => {
    setStudents((prev) =>
      prev.map((s) => (s.student_id === studentId ? { ...s, status: newStatus } : s))
    );
  };

  const handleMarkAll = (status) => {
    setStudents((prev) => prev.map((s) => ({ ...s, status })));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatusMessage({ text: '', type: '' });

    try {
      const payload = {
        class_id: classId,
        subject_code: subjectCode,
        date: date,
        session: session,
        faculty_id: user?.id || 'FAC-CS101',
        records: students.map((s) => ({
          student_id: s.student_id,
          student_name: s.student_name,
          roll_number: s.roll_number,
          status: s.status,
          remarks: s.remarks,
        })),
      };

      const res = await attendanceApi.submitAttendance(payload);
      setStatusMessage({
        text: `Attendance saved successfully: ${res.records_processed} student records committed.`,
        type: 'success',
      });
    } catch (err) {
      setStatusMessage({
        text: err.response?.data?.detail || 'Failed to submit attendance records.',
        type: 'error',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const presentCount = students.filter((s) => s.status === 'Present').length;
  const absentCount = students.filter((s) => s.status === 'Absent').length;
  const lateCount = students.filter((s) => s.status === 'Late').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">
            Class Attendance Management
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Record lecture session attendance and commit to official university registrar
          </p>
        </div>

        <button
          onClick={handleSubmit}
          disabled={submitting || students.length === 0}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-indigo-600/20 flex items-center gap-2 disabled:opacity-60 self-start sm:self-auto"
        >
          <Save className="w-3.5 h-3.5" />
          {submitting ? 'Saving Records...' : 'Save & Submit Attendance'}
        </button>
      </div>

      {statusMessage.text && (
        <div
          className={`p-4 rounded-2xl text-xs font-semibold flex items-center gap-2 ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200 border border-emerald-200 dark:border-emerald-800'
              : 'bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200 border border-rose-200 dark:border-rose-800'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Class & Date Filter Bar */}
      <div className="card-panel p-5 grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
        <div>
          <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
            Course Subject
          </label>
          <select
            value={subjectCode}
            onChange={(e) => setSubjectCode(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none font-semibold"
          >
            <option value="CS301">CS301 — Data Structures & Algorithms</option>
            <option value="CS305">CS305 — Software Engineering & Architecture</option>
            <option value="CS402">CS402 — Machine Learning Fundamentals</option>
          </select>
        </div>

        <div>
          <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
            Class Section
          </label>
          <select
            value={classId}
            onChange={(e) => setClassId(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none font-semibold"
          >
            <option value="CS-Sem2">CS-Sem2 (Design & Core)</option>
            <option value="CS-Sem3-A">CS-Sem3 Section A</option>
            <option value="CS-Sem3-B">CS-Sem3 Section B</option>
          </select>
        </div>

        <div>
          <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
            Date
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono font-semibold"
          />
        </div>

        <div>
          <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
            Session Period
          </label>
          <select
            value={session}
            onChange={(e) => setSession(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none font-semibold"
          >
            <option value="Morning">Morning Lecture (09:00 - 10:15)</option>
            <option value="Afternoon">Afternoon Lab (13:30 - 15:00)</option>
          </select>
        </div>
      </div>

      {/* Attendance Stats & Quick Actions Bar */}
      <div className="card-panel p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4 text-xs font-bold">
          <span className="text-slate-500">Roster: {students.length} students</span>
          <span className="text-emerald-600 dark:text-emerald-400">Present: {presentCount}</span>
          <span className="text-rose-600 dark:text-rose-400">Absent: {absentCount}</span>
          <span className="text-amber-600 dark:text-amber-400">Late: {lateCount}</span>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => handleMarkAll('Present')}
            className="px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-bold hover:bg-emerald-100 transition-all flex items-center gap-1"
          >
            <UserCheck className="w-3.5 h-3.5" />
            Mark All Present
          </button>
          <button
            onClick={() => handleMarkAll('Absent')}
            className="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 border border-rose-200 dark:border-rose-800 font-bold hover:bg-rose-100 transition-all flex items-center gap-1"
          >
            <UserX className="w-3.5 h-3.5" />
            Clear All
          </button>
        </div>
      </div>

      {/* Student Roster Marking Table */}
      <div className="card-panel p-5 overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-surface-darkborder text-slate-500 dark:text-slate-400">
              <th className="py-3 px-4 font-bold">Student ID</th>
              <th className="py-3 px-4 font-bold">Roll Number</th>
              <th className="py-3 px-4 font-bold">Full Name</th>
              <th className="py-3 px-4 font-bold text-center">Attendance Status</th>
              <th className="py-3 px-4 font-bold">Remarks</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {students.map((student) => (
              <tr key={student.student_id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                <td className="py-3 px-4 font-mono font-bold text-indigo-600 dark:text-indigo-400">
                  {student.student_id}
                </td>
                <td className="py-3 px-4 font-mono text-slate-500">
                  {student.roll_number}
                </td>
                <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">
                  {student.student_name}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center justify-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleStatusChange(student.student_id, 'Present')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                        student.status === 'Present'
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                      }`}
                    >
                      Present
                    </button>
                    <button
                      type="button"
                      onClick={() => handleStatusChange(student.student_id, 'Absent')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                        student.status === 'Absent'
                          ? 'bg-rose-600 text-white shadow-sm'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                      }`}
                    >
                      Absent
                    </button>
                    <button
                      type="button"
                      onClick={() => handleStatusChange(student.student_id, 'Late')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                        student.status === 'Late'
                          ? 'bg-amber-600 text-white shadow-sm'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                      }`}
                    >
                      Late
                    </button>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <input
                    type="text"
                    placeholder="Optional note..."
                    value={student.remarks || ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      setStudents((prev) =>
                        prev.map((s) => (s.student_id === student.student_id ? { ...s, remarks: val } : s))
                      );
                    }}
                    className="w-full p-1.5 rounded-lg border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-xs text-slate-800 dark:text-slate-200 outline-none"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

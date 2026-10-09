import React, { useState, useEffect } from 'react';
import {
  FileText,
  Plus,
  Calendar,
  Clock,
  User,
  CheckCircle2,
  Award,
  X,
  Upload,
} from 'lucide-react';
import { assignmentsApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import StatusBadge from '../../components/StatusBadge';

export default function FacultyAssignments() {
  const { user } = useAuth();
  const facultyId = user?.id || 'FAC-CS101';

  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [gradingSub, setGradingSub] = useState(null); // { assignmentId, studentId, studentName, ... }
  const [gradeVal, setGradeVal] = useState('');
  const [feedbackVal, setFeedbackVal] = useState('');

  // Create form state
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSubCode, setNewSubCode] = useState('CS301');
  const [newSubName, setNewSubName] = useState('Data Structures & Algorithms');
  const [newDueDate, setNewDueDate] = useState('2026-10-25');
  const [newDueTime, setNewDueTime] = useState('23:59');
  const [newMaxMarks, setNewMaxMarks] = useState(50);
  const [createMsg, setCreateMsg] = useState('');

  const loadAssignments = async () => {
    try {
      const data = await assignmentsApi.listAssignments({ faculty_id: facultyId });
      setAssignments(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssignments();
  }, [facultyId]);

  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    try {
      await assignmentsApi.createAssignment({
        title: newTitle,
        description: newDesc,
        subject_code: newSubCode,
        subject_name: newSubName,
        faculty_id: facultyId,
        faculty_name: user?.name || 'Dr. Alan Turing',
        class_id: 'CS-Sem2',
        due_date: newDueDate,
        due_time: newDueTime,
        max_marks: parseFloat(newMaxMarks),
      });
      setShowCreateModal(false);
      setNewTitle('');
      setNewDesc('');
      setCreateMsg('Assignment successfully published to class section.');
      loadAssignments();
      setTimeout(() => setCreateMsg(''), 5000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGradeSubmit = async (e) => {
    e.preventDefault();
    if (!gradingSub) return;
    try {
      await assignmentsApi.gradeAssignment(gradingSub.assignmentId, gradingSub.studentId, {
        grade: parseFloat(gradeVal),
        feedback: feedbackVal,
      });
      setGradingSub(null);
      setGradeVal('');
      setFeedbackVal('');
      loadAssignments();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">
            Assignment Management & Grading Studio
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Design coursework, review student deliverables, and publish rubric evaluations
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-indigo-600/20 flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-3.5 h-3.5" />
          Create New Assignment
        </button>
      </div>

      {createMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200 border border-emerald-200 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{createMsg}</span>
        </div>
      )}

      {/* Published Assignments Cards */}
      <div className="space-y-4">
        {assignments.map((item) => (
          <div
            key={item.id}
            className="card-panel p-5 space-y-4 hover:border-indigo-300 transition-all"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-surface-darkborder">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
                    {item.subject_code}
                  </span>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    {item.title}
                  </h3>
                  <StatusBadge status={item.status} />
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {item.description}
                </p>
              </div>

              <div className="text-xs text-slate-500 space-y-1 text-left md:text-right flex-shrink-0">
                <p className="font-mono font-bold text-slate-800 dark:text-slate-200">
                  Due: {item.due_date} at {item.due_time}
                </p>
                <p className="text-[11px] text-slate-400">
                  Max: {item.max_marks} points
                </p>
              </div>
            </div>

            {/* Submissions Section */}
            <div>
              <div className="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                <span>Received Deliverables ({item.submissions_count || 0})</span>
                <span className="text-slate-400">Section: {item.class_id}</span>
              </div>

              {item.submissions_count === 0 ? (
                <p className="text-xs text-slate-400 italic py-2">
                  No submissions uploaded yet by enrolled students.
                </p>
              ) : (
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/70 dark:border-surface-darkborder flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <User className="w-4 h-4 text-slate-400" />
                    <div>
                      <p className="text-xs font-bold text-slate-900 dark:text-white">
                        Sarah Connor (S1001)
                      </p>
                      <p className="text-[11px] text-slate-500">
                        Submitted: btree_project_s1001.zip
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setGradingSub({
                        assignmentId: item.id,
                        studentId: 'S1001',
                        studentName: 'Sarah Connor',
                        maxMarks: item.max_marks,
                      });
                      setGradeVal('48');
                      setFeedbackVal('Outstanding B-Tree traversal benchmarks.');
                    }}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    <Award className="w-3.5 h-3.5" />
                    Grade & Feedback
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Assignment Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-surface-darkpanel w-full max-w-lg rounded-2xl shadow-2xl border border-slate-200 dark:border-surface-darkborder p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-surface-darkborder pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Create & Publish Course Assignment
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateAssignment} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Assignment Title
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Dynamic Programming & Memoization Lab"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Instructions & Requirements
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Detailed project guidelines, submission format, and rubric..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Due Date
                  </label>
                  <input
                    type="date"
                    required
                    value={newDueDate}
                    onChange={(e) => setNewDueDate(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Max Marks
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="100"
                    required
                    value={newMaxMarks}
                    onChange={(e) => setNewMaxMarks(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white outline-none font-mono font-bold"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-surface-darkborder">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-600 dark:text-slate-400 font-semibold hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-md shadow-indigo-600/20"
                >
                  Publish Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Grade Submission Modal */}
      {gradingSub && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-surface-darkpanel w-full max-w-md rounded-2xl shadow-2xl border border-slate-200 dark:border-surface-darkborder p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-surface-darkborder pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Grade Submission: {gradingSub.studentName}
              </h3>
              <button onClick={() => setGradingSub(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGradeSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Grade Score (Max {gradingSub.maxMarks} pts)
                </label>
                <input
                  type="number"
                  min="0"
                  max={gradingSub.maxMarks}
                  required
                  value={gradeVal}
                  onChange={(e) => setGradeVal(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-mono font-bold text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Instructor Feedback & Comments
                </label>
                <textarea
                  rows={3}
                  value={feedbackVal}
                  onChange={(e) => setFeedbackVal(e.target.value)}
                  placeholder="Provide pedagogical feedback, code review remarks, or remediation advice..."
                  className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-surface-darkborder bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-surface-darkborder">
                <button
                  type="button"
                  onClick={() => setGradingSub(null)}
                  className="px-4 py-2 rounded-xl text-slate-600 dark:text-slate-400 font-semibold hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-md shadow-indigo-600/20"
                >
                  Publish Grade
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

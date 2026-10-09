import React, { useState, useEffect } from 'react';
import {
  Award,
  CheckSquare,
  Clock,
  CreditCard,
  FileText,
  Calendar,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  BookOpen,
} from 'lucide-react';
import MetricCard from '../../components/MetricCard';
import TimetableWidget from '../../components/TimetableWidget';
import AttendanceOverview from '../../components/AttendanceOverview';
import AssignmentTable from '../../components/AssignmentTable';
import AnnouncementPanel from '../../components/AnnouncementPanel';
import AcademicPerformanceChart from '../../components/AcademicPerformanceChart';
import { useAuth } from '../../context/AuthContext';
import {
  attendanceApi,
  marksApi,
  timetableApi,
  assignmentsApi,
  announcementsApi,
  feesApi,
} from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { formatINR } from '../../utils/currency';

export default function StudentDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const studentId = user?.id || 'S1001';

  const [attendance, setAttendance] = useState(null);
  const [marks, setMarks] = useState(null);
  const [timetable, setTimetable] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [fees, setFees] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [attData, marksData, ttData, asnData, annData, feesData] = await Promise.all([
        attendanceApi.getStudentAttendance(studentId).catch(() => null),
        marksApi.getStudentMarks(studentId).catch(() => null),
        timetableApi.getTimetable().catch(() => []),
        assignmentsApi.listAssignments({ student_id: studentId }).catch(() => []),
        announcementsApi.listAnnouncements({ audience: 'students', user_id: studentId }).catch(() => []),
        feesApi.getStudentFees(studentId).catch(() => null),
      ]);

      setAttendance(attData);
      setMarks(marksData);
      setTimetable(ttData || []);
      setAssignments(asnData || []);
      setAnnouncements(annData || []);
      setFees(feesData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [studentId]);

  const pendingAssignments = assignments.filter((a) => !a.my_submission).length;

  return (
    <div className="space-y-6">
      {/* A. Welcome Header */}
      <div className="card-panel p-6 bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 text-white relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <img
              src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
              alt={user?.name || 'Student'}
              className="w-16 h-16 rounded-2xl object-cover ring-4 ring-white/20 shadow-lg flex-shrink-0"
            />
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-white/20 text-white">
                  {user?.program || 'B.Des Animation & Multimedia'}
                </span>
                <span className="text-indigo-200 text-xs font-mono">
                  Roll: {user?.roll_number || '2024-AMD-001'}
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black tracking-tight mt-1">
                Welcome back, {user?.name || 'Sarah Connor'}!
              </h2>
              <p className="text-xs text-indigo-200 mt-0.5">
                Academic Year 2024-2025 • Semester {user?.semester || 2} • {user?.department || 'Animation & Multimedia Design'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => navigate('/student/timeline')}
              className="px-3.5 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md text-white font-semibold rounded-xl text-xs transition-all border border-white/20 flex items-center gap-1.5"
            >
              <Award className="w-3.5 h-3.5" />
              Career Timeline
            </button>
            <button
              onClick={() => navigate('/student/timetable')}
              className="px-3.5 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md text-white font-semibold rounded-xl text-xs transition-all border border-white/20 flex items-center gap-1.5"
            >
              <Calendar className="w-3.5 h-3.5" />
              Today's Classes
            </button>
            <button
              onClick={() => navigate('/student/ml-retention')}
              className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-purple-900/40 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              ML Retention Insights
            </button>
          </div>
        </div>

        {/* Ambient background blur */}
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* B. Academic Summary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
        <MetricCard
          title="Current GPA"
          value={marks?.current_gpa || '2.85'}
          subtitle={`CGPA: ${marks?.cgpa || '3.08'}`}
          icon={Award}
          colorScheme="indigo"
          trend="+0.15"
          trendType="positive"
          onClick={() => navigate('/student/marks')}
        />

        <MetricCard
          title="Attendance"
          value={`${attendance?.overall_percentage || 68.5}%`}
          subtitle="Target: 75%"
          icon={CheckSquare}
          colorScheme={attendance?.overall_percentage < 75 ? 'rose' : 'emerald'}
          badge={attendance?.overall_percentage < 75 ? 'Low' : 'Good'}
          badgeColor={attendance?.overall_percentage < 75 ? 'rose' : 'emerald'}
          onClick={() => navigate('/student/attendance')}
        />

        <MetricCard
          title="Credits Earned"
          value={`${marks?.earned_credits || 20} / ${marks?.total_credits || 40}`}
          subtitle="50% completed"
          icon={BookOpen}
          colorScheme="purple"
          onClick={() => navigate('/student/marks')}
        />

        <MetricCard
          title="Assignments"
          value={pendingAssignments}
          subtitle="Awaiting Submission"
          icon={FileText}
          colorScheme={pendingAssignments > 0 ? 'amber' : 'emerald'}
          badge={pendingAssignments > 0 ? 'Due Soon' : 'Done'}
          badgeColor={pendingAssignments > 0 ? 'amber' : 'emerald'}
          onClick={() => navigate('/student/assignments')}
        />

        <MetricCard
          title="Examinations"
          value="3 Upcoming"
          subtitle="Starts Oct 28"
          icon={Clock}
          colorScheme="indigo"
          onClick={() => navigate('/student/exams')}
        />

        <MetricCard
          title="Tuition Fees"
          value={fees?.outstanding_balance ? formatINR(fees.outstanding_balance) : 'Paid'}
          subtitle={fees?.status || 'Partially Paid'}
          icon={CreditCard}
          colorScheme={fees?.outstanding_balance > 0 ? 'amber' : 'emerald'}
          badge={fees?.status || 'Dues'}
          badgeColor={fees?.outstanding_balance > 0 ? 'amber' : 'emerald'}
          onClick={() => navigate('/student/fees')}
        />
      </div>

      {/* C & D. Timetable and Attendance */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <TimetableWidget schedule={timetable} />
        </div>
        <div className="lg:col-span-5">
          <AttendanceOverview attendanceData={attendance} />
        </div>
      </div>

      {/* Performance Analytics Chart */}
      <AcademicPerformanceChart marksData={marks} />

      {/* Assignments & Announcements */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <AssignmentTable
            assignments={assignments}
            studentId={studentId}
            onAssignmentUpdated={loadData}
          />
        </div>
        <div className="lg:col-span-5">
          <AnnouncementPanel
            announcements={announcements}
            userId={studentId}
            onRefresh={loadData}
          />
        </div>
      </div>
    </div>
  );
}

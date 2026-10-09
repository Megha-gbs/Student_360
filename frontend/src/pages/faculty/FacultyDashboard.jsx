import React, { useState, useEffect } from 'react';
import {
  Users,
  CheckSquare,
  FileText,
  Clock,
  Calendar,
  BrainCircuit,
  ArrowRight,
  BookOpen,
  Award,
  Sparkles,
} from 'lucide-react';
import MetricCard from '../../components/MetricCard';
import TimetableWidget from '../../components/TimetableWidget';
import AnnouncementPanel from '../../components/AnnouncementPanel';
import { useAuth } from '../../context/AuthContext';
import { timetableApi, assignmentsApi, announcementsApi } from '../../services/api';
import { useNavigate } from 'react-router-dom';

export default function FacultyDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const facultyId = user?.id || 'FAC-CS101';

  const [timetable, setTimetable] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      timetableApi.getTimetable({ faculty_id: facultyId }).catch(() => []),
      assignmentsApi.listAssignments({ faculty_id: facultyId }).catch(() => []),
      announcementsApi.listAnnouncements({ audience: 'faculty', user_id: facultyId }).catch(() => []),
    ]).then(([tt, asn, ann]) => {
      setTimetable(tt || []);
      setAssignments(asn || []);
      setAnnouncements(ann || []);
      setLoading(false);
    });
  }, [facultyId]);

  return (
    <div className="space-y-6">
      {/* Faculty Welcome Banner */}
      <div className="card-panel p-6 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <img
              src={user?.avatar || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80'}
              alt={user?.name || 'Faculty'}
              className="w-16 h-16 rounded-2xl object-cover ring-4 ring-indigo-500/30 shadow-lg flex-shrink-0"
            />
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
                  {user?.designation || 'Professor & Head of Department'}
                </span>
                <span className="text-slate-400 text-xs font-mono">
                  Faculty ID: {facultyId}
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black tracking-tight mt-1">
                Welcome back, {user?.name || 'Dr. Alan Turing'}
              </h2>
              <p className="text-xs text-indigo-200 mt-0.5">
                {user?.department || 'Computer Science & Engineering'} • 3 Active Course Sections Assigned
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => navigate('/faculty/attendance')}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-indigo-600/30 flex items-center gap-1.5"
            >
              <CheckSquare className="w-3.5 h-3.5" />
              Mark Class Attendance
            </button>
            <button
              onClick={() => navigate('/faculty/retention')}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-purple-600/30 flex items-center gap-1.5"
            >
              <BrainCircuit className="w-3.5 h-3.5" />
              Priority Retention Queue
            </button>
          </div>
        </div>
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <MetricCard
          title="Assigned Students"
          value="128"
          subtitle="Across 3 sections"
          icon={Users}
          colorScheme="indigo"
          onClick={() => navigate('/faculty/students')}
        />
        <MetricCard
          title="Today's Classes"
          value="2 Sessions"
          subtitle="Hall 301 & Lab 2"
          icon={Calendar}
          colorScheme="emerald"
          onClick={() => navigate('/faculty/timetable')}
        />
        <MetricCard
          title="Attendance Marking"
          value="Pending"
          subtitle="Morning session open"
          icon={CheckSquare}
          colorScheme="amber"
          badge="Action Required"
          badgeColor="amber"
          onClick={() => navigate('/faculty/attendance')}
        />
        <MetricCard
          title="Submissions to Grade"
          value="18"
          subtitle="DSA & Software Eng"
          icon={FileText}
          colorScheme="purple"
          onClick={() => navigate('/faculty/assignments')}
        />
        <MetricCard
          title="At-Risk Retention"
          value="3 Students"
          subtitle="High priority warning"
          icon={BrainCircuit}
          colorScheme="rose"
          badge="ML Alert"
          badgeColor="rose"
          onClick={() => navigate('/faculty/retention')}
        />
      </div>

      {/* Teaching Timetable & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <TimetableWidget
            schedule={timetable}
            title="Faculty Teaching Schedule"
          />
        </div>
        <div className="lg:col-span-4 space-y-4">
          <div className="card-panel p-5 space-y-3">
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              Faculty Quick Actions
            </h4>
            <div className="space-y-2">
              <button
                onClick={() => navigate('/faculty/attendance')}
                className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200/80 dark:border-surface-darkborder text-xs font-bold text-left flex items-center justify-between group transition-all"
              >
                <span className="flex items-center gap-2">
                  <CheckSquare className="w-4 h-4 text-indigo-600" />
                  Take Class Attendance Sheet
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => navigate('/faculty/marks')}
                className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200/80 dark:border-surface-darkborder text-xs font-bold text-left flex items-center justify-between group transition-all"
              >
                <span className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-emerald-600" />
                  Enter Internal Assessment Marks
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => navigate('/faculty/assignments')}
                className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200/80 dark:border-surface-darkborder text-xs font-bold text-left flex items-center justify-between group transition-all"
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-purple-600" />
                  Create New Assignment
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => navigate('/faculty/retention')}
                className="w-full p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 border border-purple-200 text-xs font-bold text-left flex items-center justify-between group transition-all text-purple-900 dark:text-purple-200"
              >
                <span className="flex items-center gap-2">
                  <BrainCircuit className="w-4 h-4 text-purple-600" />
                  View Retention Priority Queue
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-purple-600 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>

          <AnnouncementPanel
            announcements={announcements}
            userId={facultyId}
          />
        </div>
      </div>
    </div>
  );
}

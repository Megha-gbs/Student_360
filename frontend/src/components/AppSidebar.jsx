import React, { useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  CheckSquare,
  Award,
  FileText,
  Clock,
  CreditCard,
  LineChart,
  User,
  Users,
  GraduationCap,
  Building2,
  BellRing,
  ShieldCheck,
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Sparkles,
  BookOpen,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function AppSidebar({ isOpenMobile, onCloseMobile }) {
  const { user, role, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Navigation Items per Role
  const studentNav = [
    { label: 'Dashboard', path: '/student/dashboard', icon: LayoutDashboard },
    { label: 'Daily Timetable', path: '/student/timetable', icon: Calendar },
    { label: 'Attendance', path: '/student/attendance', icon: CheckSquare, badge: 'Low' },
    { label: 'Marks & Results', path: '/student/marks', icon: Award },
    { label: 'Assignments', path: '/student/assignments', icon: FileText, badge: '2 Due' },
    { label: 'Examinations', path: '/student/exams', icon: Clock },
    { label: 'Career & Timeline', path: '/student/timeline', icon: Sparkles },
    { label: 'Fees & Dues', path: '/student/fees', icon: CreditCard },
    { label: 'ML Retention AI', path: '/student/ml-retention', icon: BrainCircuit, highlight: true },
    { label: 'My Profile', path: '/student/profile', icon: User },
  ];

  const facultyNav = [
    { label: 'Dashboard', path: '/faculty/dashboard', icon: LayoutDashboard },
    { label: 'Teaching Schedule', path: '/faculty/timetable', icon: Calendar },
    { label: 'Class & Students', path: '/faculty/students', icon: Users },
    { label: 'Mark Attendance', path: '/faculty/attendance', icon: CheckSquare, badge: 'Pending' },
    { label: 'Internal Marks', path: '/faculty/marks', icon: Award },
    { label: 'Assignments', path: '/faculty/assignments', icon: FileText },
    { label: 'Announcements', path: '/faculty/announcements', icon: BellRing },
    { label: 'Priority Retention Queue', path: '/faculty/retention', icon: BrainCircuit, highlight: true, badge: 'AI' },
    { label: 'My Profile', path: '/faculty/profile', icon: User },
  ];

  const adminNav = [
    { label: 'Institution Overview', path: '/admin/dashboard', icon: LayoutDashboard },
    { label: 'Student Directory', path: '/admin/students', icon: GraduationCap },
    { label: 'Faculty Roster', path: '/admin/faculty', icon: Users },
    { label: 'Departments & Degrees', path: '/admin/departments', icon: Building2 },
    { label: 'Master Timetable', path: '/admin/timetable', icon: Calendar },
    { label: 'Attendance Reports', path: '/admin/attendance-reports', icon: CheckSquare },
    { label: 'Examinations', path: '/admin/exams', icon: Clock },
    { label: 'Fee Management', path: '/admin/fees', icon: CreditCard },
    { label: 'Official Notices', path: '/admin/announcements', icon: BellRing },
    { label: 'Users & Audit Logs', path: '/admin/users-audit', icon: ShieldCheck },
    { label: 'ML Cohort Intelligence', path: '/admin/cohort-intelligence', icon: BrainCircuit, highlight: true, badge: 'AI' },
    { label: 'Profile Settings', path: '/admin/profile', icon: User },
  ];

  const navItems = role === 'admin' ? adminNav : role === 'faculty' ? facultyNav : studentNav;

  const roleColors = {
    student: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
    faculty: 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    admin: 'bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-400 border-purple-200 dark:border-purple-800',
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col bg-white dark:bg-[#111625] border-r border-slate-200/90 dark:border-surface-darkborder transition-all duration-300 ease-in-out ${
          collapsed ? 'w-20' : 'w-64'
        } ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200/80 dark:border-surface-darkborder">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 flex-shrink-0">
              <GraduationCap className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white flex items-center gap-1.5">
                  Student<span className="text-indigo-600 dark:text-indigo-400">360</span>
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                  Campus Operating System
                </span>
              </div>
            )}
          </div>

          {/* Desktop Collapse Toggle */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Current Active Persona Card */}
        {!collapsed && user && (
          <div className="p-3 mx-3 my-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/70 dark:border-surface-darkborder flex items-center gap-3">
            <img
              src={user.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=user'}
              alt={user.name}
              className="w-10 h-10 rounded-full object-cover ring-2 ring-indigo-500/30 flex-shrink-0"
            />
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-slate-900 dark:text-slate-100 truncate">
                {user.name}
              </p>
              <span
                className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${
                  roleColors[role] || roleColors.student
                }`}
              >
                {role}
              </span>
            </div>
          </div>
        )}

        {/* Navigation List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);

            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onCloseMobile}
                title={collapsed ? item.label : undefined}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25 font-semibold'
                    : item.highlight
                    ? 'bg-purple-50 dark:bg-purple-950/30 text-purple-700 dark:text-purple-300 hover:bg-purple-100 dark:hover:bg-purple-950/60 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                <Icon
                  className={`w-4 h-4 flex-shrink-0 transition-transform group-hover:scale-110 ${
                    isActive
                      ? 'text-white'
                      : item.highlight
                      ? 'text-purple-600 dark:text-purple-400'
                      : 'text-slate-400 group-hover:text-slate-700 dark:group-hover:text-slate-200'
                  }`}
                />
                {!collapsed && (
                  <span className="truncate flex-1">{item.label}</span>
                )}
                {!collapsed && item.badge && (
                  <span
                    className={`px-1.5 py-0.5 text-[10px] font-bold rounded-md uppercase ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : item.badge === 'Low'
                        ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        : 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Footer Actions */}
        <div className="p-3 border-t border-slate-200/80 dark:border-surface-darkborder space-y-1">
          <button
            onClick={handleLogout}
            title={collapsed ? 'Logout' : undefined}
            className="w-full flex items-center gap-3 px-3 py-2 text-xs font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-xl transition-colors"
          >
            <LogOut className="w-4 h-4 flex-shrink-0" />
            {!collapsed && <span>Sign Out</span>}
          </button>
        </div>
      </aside>
    </>
  );
}

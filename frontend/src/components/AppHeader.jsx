import React, { useState } from 'react';
import {
  Menu,
  Bell,
  Search,
  User,
  GraduationCap,
  Briefcase,
  ShieldAlert,
  ChevronDown,
  Sparkles,
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import NotificationCenter from './NotificationCenter';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function AppHeader({ onToggleMobileSidebar, pageTitle, pageSubtitle }) {
  const { user, role, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getRoleBadgeStyle = (r) => {
    switch (r) {
      case 'admin':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800';
      case 'faculty':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      case 'student':
        return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';
    }
  };

  return (
    <>
      <header className="sticky top-0 z-30 h-16 bg-white/90 dark:bg-[#111625]/90 backdrop-blur-md border-b border-slate-200/80 dark:border-surface-darkborder flex items-center justify-between px-4 lg:px-6 transition-colors">
        {/* Left: Mobile Toggle & Page Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileSidebar}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden"
            aria-label="Toggle Navigation Menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div>
            <h1 className="text-sm lg:text-base font-extrabold text-slate-900 dark:text-white tracking-tight">
              {pageTitle || 'Student360 Platform'}
            </h1>
            {pageSubtitle && (
              <p className="hidden md:block text-[11px] text-slate-500 dark:text-slate-400">
                {pageSubtitle}
              </p>
            )}
          </div>
        </div>

        {/* Center: Institutional Identity Badge */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-xl bg-slate-100/70 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">
            {user?.department || 'University Portal'} &bull; Verified Institution
          </span>
        </div>

        {/* Right: Actions (Notifications, Theme Toggle, User Profile) */}
        <div className="flex items-center gap-2.5">
          {/* Notification Center Trigger with Badge */}
          <button
            onClick={() => setShowNotifications(true)}
            className="relative p-2 rounded-xl text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Notifications & Today's Schedule Sync"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 animate-pulse ring-2 ring-white dark:ring-surface-darkpanel" />
          </button>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Profile Pill & Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2.5 p-1.5 pr-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-200 dark:hover:border-slate-700 transition-colors"
            >
              <img
                src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
                alt={user?.name || 'User'}
                className="w-8 h-8 rounded-full object-cover ring-2 ring-indigo-500/30"
              />
              <div className="hidden sm:block text-left">
                <p className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
                  {user?.name || 'Authenticated User'}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className={`px-1.5 py-0.2 text-[9px] font-bold rounded uppercase border ${getRoleBadgeStyle(role)}`}>
                    {role}
                  </span>
                  {user?.id && (
                    <span className="text-[10px] text-slate-400 font-mono">
                      {user.id}
                    </span>
                  )}
                </div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden sm:block ml-1" />
            </button>

            {showUserMenu && (
              <div
                className="absolute right-0 mt-2 w-64 bg-white dark:bg-surface-darkpanel rounded-2xl shadow-xl border border-slate-200 dark:border-surface-darkborder py-2 z-50 animate-in fade-in zoom-in-95 duration-100"
                onClick={() => setShowUserMenu(false)}
              >
                <div className="px-4 py-3 border-b border-slate-100 dark:border-surface-darkborder">
                  <p className="text-xs font-bold text-slate-900 dark:text-slate-100 truncate">
                    {user?.name}
                  </p>
                  <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase border ${getRoleBadgeStyle(role)}`}>
                      {role} Access
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      ID: {user?.id}
                    </span>
                  </div>
                </div>

                <div className="px-4 py-2 text-[11px] text-slate-500 dark:text-slate-400 space-y-1 border-b border-slate-100 dark:border-surface-darkborder">
                  <div>Department: <span className="font-semibold text-slate-700 dark:text-slate-200">{user?.department || 'General'}</span></div>
                  {user?.designation && <div>Title: <span className="font-semibold text-slate-700 dark:text-slate-200">{user.designation}</span></div>}
                  {user?.program && <div>Program: <span className="font-semibold text-slate-700 dark:text-slate-200">{user.program}</span></div>}
                </div>

                <div className="pt-2 px-2">
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl font-bold flex items-center justify-between transition-colors"
                  >
                    <span>Sign Out & End Session</span>
                    <span className="text-[10px] opacity-70">&rarr;</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>


      {/* Slide-out Notification Drawer */}
      <NotificationCenter
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
      />
    </>
  );
}

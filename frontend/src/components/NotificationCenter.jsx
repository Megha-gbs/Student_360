import React, { useState, useEffect } from 'react';
import {
  Bell,
  X,
  CheckCheck,
  Calendar,
  AlertTriangle,
  Info,
  Clock,
  Sparkles,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import { notificationsApi } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function NotificationCenter({ isOpen, onClose }) {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [filter, setFilter] = useState('all');
  const [triggerResultMsg, setTriggerResultMsg] = useState('');

  const loadNotifications = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await notificationsApi.getNotifications(user.id);
      setNotifications(data || []);
    } catch (err) {
      console.warn('Could not fetch notifications from backend', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, user]);

  const handleMarkAsRead = async (id) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    if (!user) return;
    try {
      await notificationsApi.markAllRead(user.id);
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerDailySchedule = async () => {
    setTriggering(true);
    setTriggerResultMsg('');
    try {
      const res = await notificationsApi.triggerDailySchedule();
      setTriggerResultMsg(
        `Synced: ${res.notifications_created} created, ${res.skipped_duplicates} existing/skipped.`
      );
      await loadNotifications();
    } catch (err) {
      setTriggerResultMsg('Error triggering backend notification engine.');
    } finally {
      setTriggering(false);
      setTimeout(() => setTriggerResultMsg(''), 5000);
    }
  };

  if (!isOpen) return null;

  const unreadCount = notifications.filter((n) => !n.read).length;

  const filteredNotifs = notifications.filter((n) => {
    if (filter === 'all') return true;
    if (filter === 'schedule') return n.type === 'daily_schedule';
    if (filter === 'system') return n.type === 'system';
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-md bg-white dark:bg-surface-darkpanel h-full shadow-2xl flex flex-col border-l border-slate-200 dark:border-surface-darkborder z-10 transition-transform">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-200 dark:border-surface-darkborder flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/40">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-xl">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                Notifications
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 text-xs font-semibold bg-rose-500 text-white rounded-full">
                    {unreadCount} new
                  </span>
                )}
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Daily schedule alerts & announcements
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Schedule Trigger Banner (Prompt Section 9) */}
        <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/30 border-b border-indigo-100 dark:border-indigo-900/40">
          <div className="flex items-start justify-between gap-3">
            <div>
              <span className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider">
                <Sparkles className="w-3 h-3" /> Daily Timetable Sync
              </span>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5">
                Dispatch today's class schedule notification to students.
              </p>
            </div>
            <button
              onClick={handleTriggerDailySchedule}
              disabled={triggering}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg shadow-sm transition-all flex items-center gap-1.5 disabled:opacity-60 flex-shrink-0"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${triggering ? 'animate-spin' : ''}`} />
              {triggering ? 'Syncing...' : 'Sync Today'}
            </button>
          </div>
          {triggerResultMsg && (
            <div className="mt-2 text-xs font-medium text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {triggerResultMsg}
            </div>
          )}
        </div>

        {/* Filter bar & Actions */}
        <div className="px-5 py-2.5 border-b border-slate-200 dark:border-surface-darkborder flex items-center justify-between text-xs">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setFilter('all')}
              className={`px-2.5 py-1 rounded-md font-medium ${
                filter === 'all'
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white'
                  : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'
              }`}
            >
              All ({notifications.length})
            </button>
            <button
              onClick={() => setFilter('schedule')}
              className={`px-2.5 py-1 rounded-md font-medium ${
                filter === 'schedule'
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white'
                  : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'
              }`}
            >
              Schedule
            </button>
            <button
              onClick={() => setFilter('system')}
              className={`px-2.5 py-1 rounded-md font-medium ${
                filter === 'system'
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white'
                  : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'
              }`}
            >
              System
            </button>
          </div>
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium flex items-center gap-1"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              Mark all read
            </button>
          )}
        </div>

        {/* Notification List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
              Loading notifications...
            </div>
          ) : filteredNotifs.length === 0 ? (
            <div className="py-16 text-center text-slate-400 dark:text-slate-500">
              <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                No notifications right now
              </p>
              <p className="text-xs mt-1">
                You're all caught up on class timetables and announcements!
              </p>
            </div>
          ) : (
            filteredNotifs.map((notif) => {
              const isSchedule = notif.type === 'daily_schedule';
              const isHigh = notif.priority === 'high';

              return (
                <div
                  key={notif.id}
                  onClick={() => !notif.read && handleMarkAsRead(notif.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer relative ${
                    !notif.read
                      ? 'bg-indigo-50/50 dark:bg-indigo-950/20 border-indigo-200 dark:border-indigo-900/60 shadow-sm'
                      : 'bg-white dark:bg-slate-800/40 border-slate-200/80 dark:border-surface-darkborder hover:border-slate-300'
                  }`}
                >
                  {!notif.read && (
                    <span className="absolute top-3.5 right-3.5 w-2 h-2 rounded-full bg-indigo-600 animate-pulse" />
                  )}

                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg flex-shrink-0 ${
                        isSchedule
                          ? 'bg-purple-100 dark:bg-purple-950/70 text-purple-600 dark:text-purple-400'
                          : isHigh
                          ? 'bg-rose-100 dark:bg-rose-950/70 text-rose-600 dark:text-rose-400'
                          : 'bg-blue-100 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400'
                      }`}
                    >
                      {isSchedule ? (
                        <Calendar className="w-4 h-4" />
                      ) : isHigh ? (
                        <AlertTriangle className="w-4 h-4" />
                      ) : (
                        <Info className="w-4 h-4" />
                      )}
                    </div>

                    <div className="flex-1 pr-4">
                      <div className="flex items-center gap-2">
                        <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          {notif.title}
                        </h4>
                        <span className="text-[10px] uppercase px-1.5 py-0.5 rounded font-mono font-semibold bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                          {notif.delivery_channel}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 whitespace-pre-line leading-relaxed">
                        {notif.message}
                      </p>
                      <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-400">
                        <Clock className="w-3 h-3" />
                        <span>{notif.created_at}</span>
                        <span>•</span>
                        <span className="text-emerald-600 dark:text-emerald-400">
                          {notif.delivery_status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

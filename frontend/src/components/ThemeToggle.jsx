import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  return (
    <div className="flex items-center bg-slate-100 dark:bg-surface-darkpanel p-1 rounded-xl border border-slate-200 dark:border-surface-darkborder shadow-inner">
      <button
        onClick={() => setTheme('light')}
        className={`p-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
          theme === 'light'
            ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
            : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'
        }`}
        title="Light Mode"
      >
        <Sun className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Light</span>
      </button>

      <button
        onClick={() => setTheme('dark')}
        className={`p-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
          theme === 'dark'
            ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
            : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'
        }`}
        title="Dark Mode"
      >
        <Moon className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Dark</span>
      </button>

      <button
        onClick={() => setTheme('system')}
        className={`p-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
          theme === 'system'
            ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
            : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'
        }`}
        title="Follow System Theme"
      >
        <Monitor className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Auto</span>
      </button>
    </div>
  );
}

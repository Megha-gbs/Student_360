import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Lock,
  Mail,
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
  Moon,
  Sun,
  Database,
  Users,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const DEMO_CREDENTIALS = [
  {
    role: 'Admin',
    email: 'admin@student360.edu',
    identifier: 'admin',
    password: 'password123',
  },
  {
    role: 'Faculty',
    email: 'faculty@student360.edu',
    identifier: 'faculty',
    password: 'password123',
  },
  {
    role: 'Student',
    email: 'student@student360.edu',
    identifier: 'student',
    password: 'password123',
  },
];

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (setter) => (e) => {
    setter(e.target.value);
    setSelectedRole(null);
    if (error) {
      setError('');
    }
  };

  const handleSelectDemoCredential = (cred) => {
    setIdentifier(cred.email);
    setPassword(cred.password);
    setSelectedRole(cred.role);
    setError('');
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const cleanId = identifier.trim();
    const cleanPass = password.trim();

    if (!cleanId || !cleanPass) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);
    setError('');

    // Map institutional demo email to backend identifier so both "admin@student360.edu"
    // and canonical IDs authenticate seamlessly against the backend API
    let lookupId = cleanId;
    const lower = cleanId.toLowerCase();
    if (lower === 'admin@student360.edu') {
      lookupId = 'admin';
    } else if (lower === 'faculty@student360.edu') {
      lookupId = 'faculty';
    } else if (lower === 'student@student360.edu') {
      lookupId = 'student';
    } else if (lower.endsWith('@student360.edu')) {
      lookupId = lower.replace('@student360.edu', '');
    }

    const res = await login(lookupId, cleanPass);
    setLoading(false);

    if (res.success) {
      const userRole = res.user?.role;
      if (userRole === 'admin') {
        navigate('/admin/dashboard');
      } else if (userRole === 'faculty') {
        navigate('/faculty/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } else {
      setError(
        res.error === 'Invalid credentials' ||
          res.error?.toLowerCase().includes('credential') ||
          res.error?.toLowerCase().includes('user') ||
          res.error?.toLowerCase().includes('password')
          ? 'Invalid institutional ID, email, or password. Please verify your credentials and try again.'
          : res.error || 'Authentication failed. Please verify your network connection and credentials.'
      );
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#FAF9FF] dark:bg-[#0E0C1B] text-[#1E1B4B] dark:text-gray-100 transition-colors duration-200">
      {/* =====================================================================
          LEFT PANEL: Full-height Purple Brand & Feature Showcase
          ===================================================================== */}
      <div className="relative w-full lg:w-1/2 min-h-[480px] lg:min-h-screen bg-gradient-to-br from-[#4C1D95] via-[#5B21B6] to-[#3B0764] text-white p-8 sm:p-12 lg:p-16 flex flex-col justify-between overflow-hidden shadow-2xl">
        {/* Subtle decorative circular shapes */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full border border-white/10" />
          <div className="absolute -top-16 -left-16 w-72 h-72 rounded-full border border-white/10" />
          <div className="absolute top-1/3 -right-28 w-96 h-96 rounded-full bg-white/[0.04] blur-2xl" />
          <div className="absolute -bottom-36 -right-36 w-[480px] h-[480px] rounded-full border border-white/10" />
          <div className="absolute -bottom-20 -right-20 w-[340px] h-[340px] rounded-full border border-white/10" />
          <div className="absolute bottom-16 -left-20 w-80 h-80 rounded-full bg-purple-400/[0.08] blur-3xl" />
        </div>

        {/* Top: Small rounded-square S3 logo */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-11 h-11 rounded-[12px] bg-white flex items-center justify-center shadow-lg shadow-purple-950/25">
            <span className="text-[#5B21B6] font-extrabold text-lg tracking-tight">S3</span>
          </div>
          <span className="text-white/85 text-xs font-semibold uppercase tracking-widest">
            KPMG HacXLerate 2026
          </span>
        </div>

        {/* Middle: Large heading, Subtitle & Tagline */}
        <div className="relative z-10 my-12 lg:my-auto max-w-lg">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight">
            Student360
          </h1>
          <p className="text-purple-100 text-lg sm:text-xl font-normal leading-relaxed mt-4">
            AI-powered student success &amp; early warning platform.
          </p>
          <p className="text-purple-200/90 text-sm font-semibold tracking-wider uppercase mt-4">
            Predict · Explain · Act · Track.
          </p>
        </div>

        {/* Bottom: Three Feature Items */}
        <div className="relative z-10 space-y-4 pt-6 border-t border-white/15">
          <div className="flex items-start gap-3.5">
            <div className="w-7 h-7 rounded-full bg-white/15 backdrop-blur flex items-center justify-center shrink-0 mt-0.5 text-white">
              <Database className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-white text-sm font-bold">Real UCI academic data</span>
              <span className="text-purple-200 text-sm"> — Science-backed dropout prediction</span>
            </div>
          </div>

          <div className="flex items-start gap-3.5">
            <div className="w-7 h-7 rounded-full bg-white/15 backdrop-blur flex items-center justify-center shrink-0 mt-0.5 text-white">
              <Users className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-white text-sm font-bold">Human-in-the-loop</span>
              <span className="text-purple-200 text-sm"> — All interventions require approval</span>
            </div>
          </div>

          <div className="flex items-start gap-3.5">
            <div className="w-7 h-7 rounded-full bg-white/15 backdrop-blur flex items-center justify-center shrink-0 mt-0.5 text-white">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-white text-sm font-bold">Explainable AI</span>
              <span className="text-purple-200 text-sm"> — SHAP-powered risk explanations</span>
            </div>
          </div>
        </div>
      </div>

      {/* =====================================================================
          RIGHT PANEL: Light Lavender/White Sign In Form & Demo Card
          ===================================================================== */}
      <div className="relative w-full lg:w-1/2 min-h-screen bg-[#FAF9FF] dark:bg-[#0E0C1B] flex flex-col justify-between p-6 sm:p-10 lg:p-16 transition-colors duration-200">
        {/* Top-Right: Moon / Theme Icon */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            className="w-10 h-10 rounded-[10px] bg-white dark:bg-[#1C1838] border border-purple-100 dark:border-purple-900/50 shadow-sm flex items-center justify-center text-purple-900/70 hover:text-purple-900 dark:text-amber-300 dark:hover:text-amber-200 hover:border-purple-200 dark:hover:border-purple-700 transition-colors focus:outline-none"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>

        {/* Center: Sign In Form & Demo Credentials Card */}
        <div className="w-full max-w-md mx-auto my-auto py-8">
          <div className="mb-8">
            <h2 className="text-3xl font-extrabold text-[#1E1B4B] dark:text-white tracking-tight">
              Welcome back
            </h2>
            <p className="text-sm text-gray-500 dark:text-purple-200/70 mt-2">
              Sign in to your account to continue.
            </p>
          </div>

          {/* Inline Error Message */}
          {error && (
            <div
              role="alert"
              className="mb-6 p-4 rounded-[10px] bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 text-red-700 dark:text-red-300 text-xs flex items-start gap-3"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
              <div className="leading-relaxed">{error}</div>
            </div>
          )}

          {/* Sign In Form */}
          <form onSubmit={handleFormSubmit} className="space-y-5" noValidate>
            <div>
              <label
                htmlFor="email-input"
                className="block text-xs font-semibold text-gray-700 dark:text-purple-200/90 uppercase tracking-wider mb-2"
              >
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 dark:text-gray-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="email-input"
                  type="text"
                  autoComplete="email"
                  required
                  value={identifier}
                  onChange={handleInputChange(setIdentifier)}
                  placeholder="you@student360.edu"
                  className="w-full pl-10 pr-4 py-3 text-sm rounded-[10px] bg-white dark:bg-[#1A1633] border border-gray-250 dark:border-purple-900/50 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5B21B6]/25 dark:focus:ring-purple-500/30 focus:border-[#5B21B6] dark:focus:border-purple-500 transition-all shadow-sm"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="password-input"
                  className="block text-xs font-semibold text-gray-700 dark:text-purple-200/90 uppercase tracking-wider"
                >
                  Password
                </label>
                <span className="text-xs text-[#5B21B6] dark:text-purple-400 hover:underline cursor-pointer font-medium">
                  Forgot password?
                </span>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 dark:text-gray-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password-input"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={handleInputChange(setPassword)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-11 py-3 text-sm rounded-[10px] bg-white dark:bg-[#1A1633] border border-gray-250 dark:border-purple-900/50 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5B21B6]/25 dark:focus:ring-purple-500/30 focus:border-[#5B21B6] dark:focus:border-purple-500 transition-all shadow-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors focus:outline-none"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 bg-[#5B21B6] hover:bg-[#4C1D95] active:bg-[#3B0764] dark:bg-[#7C3AED] dark:hover:bg-[#6D28D9] text-white font-semibold rounded-[10px] text-sm transition-all shadow-md shadow-purple-600/20 dark:shadow-purple-900/40 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <span>Sign in</span>
              )}
            </button>
          </form>

          {/* Demo Credentials Card */}
          <div className="mt-8 p-4 rounded-[12px] bg-white dark:bg-[#17142E] border border-purple-100 dark:border-purple-900/50 shadow-sm transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-gray-700 dark:text-purple-200 uppercase tracking-wider">
                Demo credentials
              </span>
              <span className="text-[11px] text-[#5B21B6] dark:text-purple-400 font-medium">
                Click entry to autofill
              </span>
            </div>

            <div className="space-y-2">
              {DEMO_CREDENTIALS.map((cred) => {
                const isSelected = selectedRole === cred.role;
                return (
                  <button
                    key={cred.role}
                    type="button"
                    onClick={() => handleSelectDemoCredential(cred)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-[8px] border text-left transition-all ${
                      isSelected
                        ? 'bg-purple-50/90 dark:bg-purple-950/70 border-[#5B21B6] dark:border-purple-500 ring-1 ring-[#5B21B6]/30 dark:ring-purple-500/40'
                        : 'bg-[#FAF9FF] dark:bg-[#1E1A3C] border-purple-100/70 dark:border-purple-900/40 text-gray-900 dark:text-purple-100 hover:bg-white dark:hover:bg-[#252048] hover:border-purple-200 dark:hover:border-purple-700'
                    }`}
                  >
                    <div className="flex items-center gap-2 text-xs">
                      <span className={`font-bold ${isSelected ? 'text-[#5B21B6] dark:text-purple-300' : 'text-gray-900 dark:text-white'}`}>
                        {cred.role}
                      </span>
                      <span className="text-gray-400 dark:text-gray-500 font-mono">—</span>
                      <span className={`font-mono text-[11.5px] ${isSelected ? 'text-[#5B21B6] dark:text-purple-300 font-semibold' : 'text-gray-600 dark:text-purple-300/80'}`}>
                        {cred.email}
                      </span>
                    </div>
                    {isSelected ? (
                      <CheckCircle2 className="w-4 h-4 text-[#5B21B6] dark:text-purple-400 shrink-0" />
                    ) : (
                      <span className="text-[11px] text-gray-400 dark:text-gray-500 font-medium">Select</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Bottom Disclaimers */}
        <div className="w-full max-w-md mx-auto pt-6 text-center text-xs text-gray-400 dark:text-purple-300/60 space-y-1.5 border-t border-purple-100/60 dark:border-purple-900/40">
          <p>
            Decision support only — human approval required for all interventions.
          </p>
          <p>
            Cohort is a demonstration dataset. Matched and synthetic fields are labelled.
          </p>
        </div>
      </div>
    </div>
  );
}

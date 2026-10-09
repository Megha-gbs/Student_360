import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Lock,
  User,
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (setter) => (e) => {
    setter(e.target.value);
    if (error) {
      setError('');
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const cleanId = identifier.trim();
    const cleanPass = password.trim();

    if (!cleanId || !cleanPass) {
      setError('Please enter your institutional email or ID and password.');
      return;
    }

    setLoading(true);
    setError('');
    const res = await login(cleanId, cleanPass);
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
        res.error === 'Invalid credentials' || res.error?.toLowerCase().includes('credential') || res.error?.toLowerCase().includes('user')
          ? 'Invalid institutional ID, email, or password. Please verify your credentials and try again.'
          : res.error || 'Authentication failed. Please verify your network connection and credentials.'
      );
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f6f9] text-slate-800 flex flex-col justify-between py-10 px-4 sm:px-6">
      {/* Top Section / Centered Institutional Brand Header */}
      <div className="w-full max-w-md mx-auto text-center pt-2 pb-6">
        <div className="inline-flex items-center justify-center gap-3 mb-2">
          <div className="w-11 h-11 rounded-xl bg-indigo-700 flex items-center justify-center text-white shadow-sm">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div className="text-left">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 leading-tight">
              Student<span className="text-indigo-700">360</span>
            </h1>
            <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
              Learning Management & Academic Portal
            </p>
          </div>
        </div>
      </div>

      {/* Main Centered Login Card */}
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-7 sm:p-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-bold text-slate-900">
              Institutional Sign In
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Sign in with your institutional email or student ID.
            </p>
          </div>

          {/* Inline Error Alert */}
          {error && (
            <div
              role="alert"
              className="mb-5 p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2.5"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-600 mt-0.5" />
              <div className="leading-relaxed">{error}</div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleFormSubmit} className="space-y-4" noValidate>
            <div>
              <label
                htmlFor="identifier-input"
                className="block text-xs font-semibold text-slate-700 mb-1.5"
              >
                Username / Institutional Email / ID
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="identifier-input"
                  type="text"
                  autoComplete="username"
                  required
                  value={identifier}
                  onChange={handleInputChange(setIdentifier)}
                  placeholder="e.g., student@student360.edu or S1001"
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-lg bg-slate-50 border border-slate-300 text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="password-input"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Password
                </label>
                <span className="text-xs text-indigo-700 hover:text-indigo-800 hover:underline cursor-pointer font-medium">
                  Forgot password?
                </span>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password-input"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={handleInputChange(setPassword)}
                  placeholder="Enter your password"
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-lg bg-slate-50 border border-slate-300 text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 transition-colors focus:outline-none"
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

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-indigo-700 hover:bg-indigo-800 active:bg-indigo-900 text-white font-semibold rounded-lg text-sm transition-colors shadow-sm flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Signing in...</span>
                  </>
                ) : (
                  <span>Sign In</span>
                )}
              </button>
            </div>
          </form>

          {/* Quick Demo Credentials Selector */}
          <div className="mt-5 pt-4 border-t border-slate-100">
            <div className="text-[11px] font-semibold text-slate-500 mb-2 text-center uppercase tracking-wider">
              Demo Evaluation Accounts
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => { setIdentifier('ADM001'); setPassword('admin123'); setError(''); }}
                className="px-2 py-1.5 text-xs font-medium rounded-lg bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 border border-slate-200 transition-colors text-center"
              >
                <span className="block font-bold">Admin</span>
                <span className="text-[10px] text-slate-500">ADM001</span>
              </button>
              <button
                type="button"
                onClick={() => { setIdentifier('FAC001'); setPassword('faculty123'); setError(''); }}
                className="px-2 py-1.5 text-xs font-medium rounded-lg bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 border border-slate-200 transition-colors text-center"
              >
                <span className="block font-bold">Faculty</span>
                <span className="text-[10px] text-slate-500">FAC001</span>
              </button>
              <button
                type="button"
                onClick={() => { setIdentifier('S1001'); setPassword('student123'); setError(''); }}
                className="px-2 py-1.5 text-xs font-medium rounded-lg bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 border border-slate-200 transition-colors text-center"
              >
                <span className="block font-bold">Student</span>
                <span className="text-[10px] text-slate-500">S1001</span>
              </button>
            </div>
          </div>

          {/* Secure Institutional Access Notice */}
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-center gap-2 text-[11px] text-slate-400">
            <ShieldCheck className="w-4 h-4 text-slate-400" />
            <span>Secure 256-Bit Encrypted Campus Authentication</span>
          </div>
        </div>
      </div>

      {/* Institutional Footer */}
      <footer className="w-full max-w-2xl mx-auto text-center text-xs text-slate-500 pt-8 pb-2 space-y-1">
        <div>
          Student360 &bull; Institutional Academic & Learning Management System
        </div>
        <div className="text-[11px] text-slate-400">
          For login assistance or account provisioning, please contact the IT Helpdesk at{' '}
          <span className="text-slate-600 font-medium">it-support@student360.edu</span>
        </div>
      </footer>
    </div>
  );
}

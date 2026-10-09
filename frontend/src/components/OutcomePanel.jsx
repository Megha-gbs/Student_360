import React, { useState, useEffect } from 'react';
import { Target, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';
import { simulateOutcome } from '../services/api';

export default function OutcomePanel({ studentId, currentRisk = 74 }) {
  const [loading, setLoading] = useState(false);
  const [outcome, setOutcome] = useState(null);
  const [error, setError] = useState(null);

  // Clear previous projection when student changes
  useEffect(() => {
    setOutcome(null);
    setError(null);
  }, [studentId]);

  const handleSimulateOutcome = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await simulateOutcome(studentId, { current_risk: currentRisk });
      if (res.success && res.data) {
        setOutcome(res.data);
      } else {
        setError(res.error || "Failed to simulate outcome.");
      }
    } catch (err) {
      setError(err.message || "Failed to simulate outcome.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-surface-darkcard p-6 rounded-2xl border border-slate-200 dark:border-surface-darkborder shadow-sm">
      {/* Header with Mandatory Strict Label */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 dark:border-surface-darkborder gap-2">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-purple-50 dark:bg-purple-950/60 rounded-lg text-purple-600 dark:text-purple-400">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Simulated Outcome Projection</h3>
            <p className="text-xs text-purple-700 dark:text-purple-400">
              Simulated demonstration outcome post-intervention; not real student improvement.
            </p>
          </div>
        </div>
        <span className="px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded-lg bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800 self-start sm:self-auto">
          Simulated demonstration outcome
        </span>
      </div>

      {!outcome ? (
        <div className="mt-6 text-center py-6">
          <p className="text-xs text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-4">
            Simulate the expected risk trajectory reduction if the approved academic and financial interventions are completed.
          </p>
          <button
            onClick={handleSimulateOutcome}
            disabled={loading}
            className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-md shadow-purple-600/25 transition-all inline-flex items-center space-x-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Forecasting...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Calculate Projected Outcome</span>
              </>
            )}
          </button>
          {error && (
            <div className="mt-4 p-3 bg-rose-50 dark:bg-rose-950/20 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900/60 rounded-xl text-xs flex items-center justify-center space-x-2 max-w-md mx-auto">
              <AlertCircle className="w-4 h-4 text-rose-500" />
              <span>{error}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="mt-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 bg-purple-50/60 dark:bg-purple-950/20 rounded-xl border border-purple-100 dark:border-purple-900/60">
              <span className="text-xs font-medium text-purple-800 dark:text-purple-300 block mb-1">Projected Dropout Risk</span>
              <span className="text-2xl font-extrabold text-purple-900 dark:text-purple-200">
                {outcome.projected_dropout_risk}
                <span className="text-sm font-normal text-purple-600 dark:text-purple-400"> / 100</span>
              </span>
              <span className="text-[11px] text-emerald-700 dark:text-emerald-400 font-bold block mt-1">
                ↓ Risk reduced by {currentRisk - outcome.projected_dropout_risk} pts
              </span>
            </div>

            <div className="p-4 bg-emerald-50/60 dark:bg-emerald-950/20 rounded-xl border border-emerald-100 dark:border-emerald-900/60">
              <span className="text-xs font-medium text-emerald-800 dark:text-emerald-300 block mb-1">Projected Retention Rate</span>
              <span className="text-2xl font-extrabold text-emerald-900 dark:text-emerald-200">
                {(outcome.projected_retention_probability * 100).toFixed(0)}%
              </span>
              <span className="text-[11px] text-emerald-700 dark:text-emerald-400 font-medium block mt-1">
                High likelihood of degree continuity
              </span>
            </div>

            <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-surface-darkborder">
              <span className="text-xs font-medium text-slate-600 dark:text-slate-400 block mb-1">Graduation Timeline</span>
              <span className="text-sm font-bold text-slate-800 dark:text-white block mt-1">
                {outcome.projected_graduation_timeline}
              </span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400 block mt-1">
                Confidence: <strong className="text-slate-700 dark:text-slate-300">{outcome.confidence}</strong>
              </span>
            </div>
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-surface-darkborder rounded-xl flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Projection Type: <code className="font-mono text-slate-700 dark:text-slate-300">{outcome.projection_type}</code></span>
            <button
              onClick={handleSimulateOutcome}
              className="text-xs font-medium text-purple-700 dark:text-purple-400 hover:text-purple-900 dark:hover:text-purple-200 underline"
            >
              Re-calculate Projection
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

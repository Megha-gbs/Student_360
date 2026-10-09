import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  RefreshCw,
  AlertTriangle,
  GraduationCap
} from 'lucide-react';
import { getStudent } from '../services/api';
import RiskCard from '../components/RiskCard';
import RiskTrajectory from '../components/RiskTrajectory';
import ShapReasons from '../components/ShapReasons';
import WhatIfPanel from '../components/WhatIfPanel';
import InterventionPanel from '../components/InterventionPanel';
import OutcomePanel from '../components/OutcomePanel';
import { LoadingSkeleton, ErrorState } from '../components/UIStateComponents';

export default function Student360() {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isCancelled = false;

    const fetchStudentData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getStudent(id);
        if (isCancelled) return;
        if (res.success && res.data) {
          setStudent(res.data);
        } else {
          setError(res.error || `Student profile ${id} could not be retrieved.`);
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err.message || `Error fetching student ${id}`);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    if (id) {
      fetchStudentData();
    }

    return () => {
      isCancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <Link to="/priority-queue" className="inline-flex items-center space-x-1.5 hover:text-indigo-600">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Priority Queue</span>
          </Link>
        </div>
        <LoadingSkeleton count={3} height="h-28" />
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ErrorState
          title="Student Profile Error"
          message={error || `Student ${id} could not be found in the system.`}
          onRetry={() => window.location.reload()}
        />
        <div className="mt-4 text-center">
          <Link
            to="/priority-queue"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-900 dark:bg-indigo-600 text-white text-xs font-semibold rounded-xl shadow"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Priority Queue</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Navigation Breadcrumb & Student Header */}
      <div>
        <Link
          to="/priority-queue"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Priority Queue</span>
        </Link>

        {/* Section A: Student Header Profile Banner */}
        <div className="bg-white dark:bg-surface-darkcard p-6 rounded-2xl border border-slate-200 dark:border-surface-darkborder shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-slate-800 to-indigo-900 flex items-center justify-center text-white font-extrabold text-xl shadow-md flex-shrink-0">
                {student.student_id.substring(0, 3)}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                    {student.student_id}
                  </h1>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                    Active Student Record
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-300 mt-0.5">
                  {student.course_name || 'Higher Education Degree Program'}
                </p>
              </div>
            </div>

            {/* Student Metadata Badges (Real UCI Demographics & Holistic Scoring) */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-surface-darkborder">
                <span className="text-slate-400 dark:text-slate-500 block text-[11px]">Age at Matriculation</span>
                <span className="font-bold text-slate-800 dark:text-white">{student.age_at_enrollment ?? 20} Years</span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-surface-darkborder">
                <span className="text-slate-400 dark:text-slate-500 block text-[11px]">Tuition Status</span>
                <span className={`font-bold ${student.tuition_fees_up_to_date === 1 ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-700 dark:text-rose-400'}`}>
                  {student.tuition_fees_up_to_date === 1 ? 'Up to date' : 'Overdue Hold'}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-surface-darkborder">
                <span className="text-slate-400 dark:text-slate-500 block text-[11px]">Debtor Status</span>
                <span className={`font-bold ${student.debtor === 1 ? 'text-rose-700 dark:text-rose-400' : 'text-slate-800 dark:text-slate-200'}`}>
                  {student.debtor === 1 ? 'Active Debt' : 'Clear'}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-surface-darkborder">
                <span className="text-slate-400 dark:text-slate-500 block text-[11px]">Scholarship</span>
                <span className="font-bold text-slate-800 dark:text-white">
                  {student.scholarship_holder === 1 ? 'Scholarship Holder' : 'Self-Funded'}
                </span>
              </div>
              <div className="p-2.5 bg-teal-50/80 dark:bg-teal-950/40 rounded-xl border border-teal-200/80 dark:border-teal-900/60">
                <span className="text-teal-700 dark:text-teal-400 block text-[11px] font-medium">Success Score</span>
                <span className="font-extrabold text-teal-900 dark:text-teal-200">
                  {student.success_score != null ? `${student.success_score} / 100` : 'Evaluating...'}
                </span>
                <span className="block text-[10px] text-teal-600 dark:text-teal-400 font-semibold">
                  {student.success_tier || 'Provisional'}
                </span>
              </div>
              <div className="p-2.5 bg-blue-50/80 dark:bg-blue-950/40 rounded-xl border border-blue-200/80 dark:border-blue-900/60">
                <span className="text-blue-700 dark:text-blue-400 block text-[11px] font-medium">Placement Readiness</span>
                <span className="font-extrabold text-blue-900 dark:text-blue-200">
                  {student.placement_readiness != null ? `${student.placement_readiness} / 100` : 'Evaluating...'}
                </span>
                <span className="block text-[10px] text-blue-600 dark:text-blue-400 font-semibold">
                  {student.placement_tier || 'Provisional'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section B: Risk Score + Risk Level + Trend */}
      <RiskCard
        riskScore={student.risk_score}
        riskLevel={student.risk_level}
        dropoutProbability={student.dropout_probability}
        trend={student.trend}
        modelVersion={student.model_version || 'student360_xgb_v2_real_features'}
      />

      {/* Section C: Real Sem 1 -> Sem 2 Trajectory */}
      <RiskTrajectory trajectory={student.trajectory} />

      {/* Section D: Why? — SHAP Explanations */}
      <ShapReasons reasons={student.top_reasons} />

      {/* Section E: What-If Simulation */}
      <WhatIfPanel
        studentId={student.student_id}
        originalRisk={student.risk_score}
        studentData={student}
      />

      {/* Section F & G: Recommended Intervention + Human Approval */}
      <InterventionPanel
        studentId={student.student_id}
        recommendedIntervention={student.recommended_intervention}
      />

      {/* Section H: Simulated Post-Intervention Outcome */}
      <OutcomePanel
        studentId={student.student_id}
        currentRisk={student.risk_score}
      />
    </div>
  );
}

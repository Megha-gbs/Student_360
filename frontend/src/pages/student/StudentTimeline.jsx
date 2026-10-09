import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Award,
  BookOpen,
  Briefcase,
  Code2,
  Trophy,
  CheckCircle2,
  Clock,
  XCircle,
  ExternalLink,
  Plus,
  Edit2,
  Trash2,
  Filter,
  Layers,
  GraduationCap,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  Info,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { timelineApi } from '../../services/api';

const CATEGORIES = [
  { id: 'All', label: 'All Milestones', icon: Layers },
  { id: 'Education', label: 'Education', icon: GraduationCap },
  { id: 'Semesters', label: 'Semesters', icon: BookOpen },
  { id: 'Projects', label: 'Projects', icon: Code2 },
  { id: 'Hackathons', label: 'Hackathons', icon: Trophy },
  { id: 'Certifications', label: 'Certifications', icon: Award },
  { id: 'Internships', label: 'Internships', icon: Briefcase },
  { id: 'Awards', label: 'Awards', icon: Sparkles },
  { id: 'Placement Milestones', label: 'Placement Milestones', icon: ShieldCheck },
];

export default function StudentTimeline() {
  const { user } = useAuth();
  const studentId = user?.id || 'S1001';

  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedYear, setSelectedYear] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    category: 'Projects',
    academic_year: '2024-2025',
    date: new Date().toISOString().split('T')[0],
    description: '',
    organization: '',
    evidence_url: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchTimeline = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await timelineApi.getTimeline(studentId, {
        category: selectedCategory !== 'All' ? selectedCategory : undefined,
        academic_year: selectedYear !== 'All' ? selectedYear : undefined,
        status: selectedStatus !== 'All' ? selectedStatus : undefined,
      });
      setTimeline(data);
    } catch (err) {
      setError('Failed to load education and career timeline records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, [studentId, selectedCategory, selectedYear, selectedStatus]);

  const handleOpenAdd = () => {
    setEditingItem(null);
    setFormData({
      title: '',
      category: 'Projects',
      academic_year: '2024-2025',
      date: new Date().toISOString().split('T')[0],
      description: '',
      organization: '',
      evidence_url: '',
    });
    setShowModal(true);
  };

  const handleOpenEdit = (item) => {
    setEditingItem(item);
    setFormData({
      title: item.title,
      category: item.category,
      academic_year: item.academic_year || '2024-2025',
      date: item.date,
      description: item.description,
      organization: item.organization || '',
      evidence_url: item.evidence_url || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this milestone entry?')) return;
    try {
      await timelineApi.deleteTimelineEntry(studentId, entryId);
      setTimeline((prev) => prev.filter((e) => e.id !== entryId));
    } catch (err) {
      alert('Failed to delete timeline entry.');
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.date || !formData.description) {
      alert('Please fill out all required fields.');
      return;
    }

    setSubmitting(true);
    try {
      if (editingItem) {
        const updated = await timelineApi.updateTimelineEntry(studentId, editingItem.id, formData);
        setTimeline((prev) => prev.map((e) => (e.id === editingItem.id ? updated : e)));
      } else {
        const created = await timelineApi.createTimelineEntry(studentId, formData);
        setTimeline((prev) => [created, ...prev]);
      }
      setShowModal(false);
    } catch (err) {
      alert('Failed to save timeline milestone. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getCategoryIcon = (category) => {
    const found = CATEGORIES.find((c) => c.id === category);
    const Icon = found ? found.icon : Award;
    return <Icon className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-white dark:bg-surface-darkpanel border border-slate-200 dark:border-surface-darkborder shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">
              Student Career & Academic Timeline
            </span>
            <span className="text-xs text-slate-400">&bull; ID: {studentId}</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Education, Milestones & Achievements
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Comprehensive chronological portfolio of formal education, certifications, hackathons, and placement readiness milestones.
          </p>
        </div>

        <button
          onClick={handleOpenAdd}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition-colors shadow-sm self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Milestone / Achievement</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-surface-darkpanel border border-slate-200 dark:border-surface-darkborder shadow-sm space-y-3">
        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const active = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-colors ${
                  active
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Secondary Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-100 dark:border-surface-darkborder text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-500 font-medium">Academic Year:</span>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-800 dark:text-slate-200 text-xs focus:ring-2 focus:ring-indigo-500"
            >
              <option value="All">All Years</option>
              <option value="2023-2024">2023–2024</option>
              <option value="2024-2025">2024–2025</option>
              <option value="2025-2026">2025–2026</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-500 font-medium">Status:</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-800 dark:text-slate-200 text-xs focus:ring-2 focus:ring-indigo-500"
            >
              <option value="All">All Statuses</option>
              <option value="Institution-Verified">Institution-Verified</option>
              <option value="Self-Reported">Self-Reported (Pending Review)</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>

          <div className="ml-auto text-slate-400 text-[11px]">
            Showing <strong className="text-slate-700 dark:text-slate-300">{timeline.length}</strong> milestones
          </div>
        </div>
      </div>

      {/* Main Timeline Stream */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          Loading timeline entries...
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      ) : timeline.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-surface-darkpanel border border-slate-200 dark:border-surface-darkborder rounded-2xl">
          <GraduationCap className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">No Milestones Found</p>
          <p className="text-xs text-slate-400 mt-1">Try resetting filters or click "Add Milestone" to submit a new entry.</p>
        </div>
      ) : (
        <div className="relative pl-6 sm:pl-8 border-l-2 border-indigo-200 dark:border-indigo-900/50 space-y-6 my-4">
          {timeline.map((item) => {
            const isVerified = item.verification_status === 'Institution-Verified';
            const isRejected = item.verification_status === 'Rejected';
            const isPending = item.verification_status === 'Self-Reported';

            return (
              <div key={item.id} className="relative group">
                {/* Node Bullet */}
                <div
                  className={`absolute -left-[31px] sm:-left-[39px] top-1.5 w-6 h-6 rounded-full flex items-center justify-center border-2 shadow-sm ${
                    isVerified
                      ? 'bg-emerald-500 border-white dark:border-slate-900 text-white'
                      : isRejected
                      ? 'bg-rose-500 border-white dark:border-slate-900 text-white'
                      : 'bg-amber-500 border-white dark:border-slate-900 text-white'
                  }`}
                >
                  {isVerified ? (
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  ) : isRejected ? (
                    <XCircle className="w-3.5 h-3.5" />
                  ) : (
                    <Clock className="w-3.5 h-3.5" />
                  )}
                </div>

                {/* Card */}
                <div className="p-5 rounded-2xl bg-white dark:bg-surface-darkpanel border border-slate-200 dark:border-surface-darkborder shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {getCategoryIcon(item.category)}
                          <span>{item.category}</span>
                        </span>

                        <span className="text-xs text-slate-400 font-medium flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{item.date}</span>
                          {item.academic_year && <span>({item.academic_year})</span>}
                        </span>

                        {/* Status Badge */}
                        {isVerified && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Institution-Verified</span>
                          </span>
                        )}
                        {isPending && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800">
                            <Clock className="w-3 h-3" />
                            <span>Self-Reported (Under Review)</span>
                          </span>
                        )}
                        {isRejected && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-800">
                            <XCircle className="w-3 h-3" />
                            <span>Verification Rejected</span>
                          </span>
                        )}
                      </div>

                      <h3 className="text-base font-bold text-slate-900 dark:text-white pt-1">
                        {item.title}
                      </h3>

                      {item.organization && (
                        <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                          {item.organization}
                        </p>
                      )}
                    </div>

                    {/* Action buttons for self-reported items */}
                    <div className="flex items-center gap-1.5 self-end sm:self-start opacity-90 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => handleOpenEdit(item)}
                        title="Edit milestone"
                        className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        title="Delete milestone"
                        className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mt-2">
                    {item.description}
                  </p>

                  {/* Rejection Note if applicable */}
                  {isRejected && item.rejection_reason && (
                    <div className="mt-3 p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 text-xs text-rose-700 dark:text-rose-300">
                      <strong>Reviewer Remarks:</strong> {item.rejection_reason}
                    </div>
                  )}

                  {/* Verification & Evidence Footer */}
                  <div className="flex flex-wrap items-center justify-between gap-2 mt-4 pt-3 border-t border-slate-100 dark:border-surface-darkborder text-[11px] text-slate-400">
                    <div className="flex items-center gap-2">
                      {isVerified && item.verified_by_name && (
                        <span>Verified by {item.verified_by_name} on {item.verified_at}</span>
                      )}
                      {isPending && (
                        <span>Pending institutional review by faculty advisor</span>
                      )}
                    </div>

                    {item.evidence_url && (
                      <a
                        href={item.evidence_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        <span>View Evidence Document</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add / Edit Milestone Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-surface-darkpanel border border-slate-200 dark:border-surface-darkborder rounded-2xl shadow-xl max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-surface-darkborder">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                {editingItem ? 'Edit Milestone Entry' : 'Add Milestone / Achievement'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                &times;
              </button>
            </div>

            <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/40 text-[11px] text-indigo-700 dark:text-indigo-300 flex items-start gap-2">
              <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>
                Submissions by students are categorized as <strong>Self-Reported</strong> and queued for review by assigned faculty or administrators.
              </span>
            </div>

            <form onSubmit={handleFormSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Milestone Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Winner of Smart Campus Hackathon, Figma Certification"
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Category *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  >
                    {CATEGORIES.filter((c) => c.id !== 'All').map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Academic Year *
                  </label>
                  <select
                    value={formData.academic_year}
                    onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="2023-2024">2023–2024</option>
                    <option value="2024-2025">2024–2025</option>
                    <option value="2025-2026">2025–2026</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Organization / Issuer
                  </label>
                  <input
                    type="text"
                    value={formData.organization}
                    onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                    placeholder="e.g. ACM Chapter, Microsoft, Horizon Studios"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Evidence Document / Verification Link
                </label>
                <input
                  type="url"
                  value={formData.evidence_url}
                  onChange={(e) => setFormData({ ...formData, evidence_url: e.target.value })}
                  placeholder="https://credentials.org/verify/... or GitHub repository"
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Description & Impact Details *
                </label>
                <textarea
                  rows={3}
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Summarize the project outcome, skills demonstrated, or competition result..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-surface-darkborder text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100 dark:border-surface-darkborder">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 dark:border-surface-darkborder text-slate-600 dark:text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold disabled:opacity-50"
                >
                  {submitting ? 'Saving...' : editingItem ? 'Save Changes' : 'Submit Milestone'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/store/authStore';
import {
    Activity,
    AlertTriangle,
    BarChart3,
    Brain,
    CheckCircle,
    RefreshCw,
    Users,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_ENGAGEMENT_TRACKER_API_URL ?? 'http://localhost:8005';
const LEARNING_STYLE_API = import.meta.env.VITE_LEARNING_STYLE_API_URL ?? 'http://localhost:8006';

interface StudentRow {
    student_id: string;
    engagement_score: number;
    engagement_level: string;
    engagement_trend: string;
    at_risk: boolean;
    risk_level: string;
    risk_probability: number | null;
    last_updated: string;
    learning_style?: string;
}

interface LearningStyleProfile {
    student_id: string;
    learning_style: string;
}

interface SystemStats {
    learning_style_distribution?: Record<string, number>;
}

interface ListResponse {
    total: number;
    students: StudentRow[];
}

const SCORE_BAR_COLOR = (score: number) => {
    if (score >= 70) return 'bg-emerald-500';
    if (score >= 40) return 'bg-amber-400';
    return 'bg-red-500';
};

export default function EngagementOverview() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const instituteId = user?.institute_id ?? 'LMS_INST_A';

    const [students, setStudents] = useState<StudentRow[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'all' | 'at_risk' | 'high_risk'>('all');
    const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
    const [avgLearningStyle, setAvgLearningStyle] = useState<string>('—');

    // Advanced Filters & Sort
    const [searchId, setSearchId] = useState('');
    const [scoreOp, setScoreOp] = useState<'all' | '>' | '<' | '=' | 'between'>('all');
    const [scoreVal1, setScoreVal1] = useState<number | ''>('');
    const [scoreVal2, setScoreVal2] = useState<number | ''>('');
    const [styleFilter, setStyleFilter] = useState<string>('all');
    const [dateOp, setDateOp] = useState<'all' | 'before' | 'after' | 'on'>('all');
    const [dateVal, setDateVal] = useState<string>('');
    const [sortOrder, setSortOrder] = useState<'none' | 'asc' | 'desc'>('none');

    const fetchStudents = async () => {
        setLoading(true);
        setError(null);
        try {
            const [listRes, profilesRes, statsRes] = await Promise.all([
                fetch(`${API_BASE}/api/v1/students/list?limit=200&institute_id=${encodeURIComponent(instituteId)}`),
                fetch(`${LEARNING_STYLE_API}/api/v1/students/?limit=500`),
                fetch(`${LEARNING_STYLE_API}/api/v1/system/stats`),
            ]);

            if (!listRes.ok) throw new Error(`Server responded with ${listRes.status}`);
            const data: ListResponse = await listRes.json();
            const studentsList = data.students as StudentRow[];

            const map: Record<string, string> = {};
            if (profilesRes.ok) {
                const profiles: LearningStyleProfile[] = await profilesRes.json();
                profiles.forEach((p) => { map[p.student_id] = p.learning_style; });
            }

            let modeStyle = '—';
            if (statsRes.ok) {
                const stats: SystemStats = await statsRes.json();
                const dist = stats.learning_style_distribution ?? {};
                const entries = Object.entries(dist);
                if (entries.length > 0) {
                    const [top] = entries.sort((a, b) => b[1] - a[1]);
                    modeStyle = top[0];
                }
            }
            setAvgLearningStyle(modeStyle);

            setStudents(studentsList.map((s) => ({ ...s, learning_style: map[s.student_id] })));
            setLastRefresh(new Date());
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Failed to load students');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { void fetchStudents(); }, [instituteId]);

    const displayed = students.filter(s => {
        if (filter === 'at_risk' && !s.at_risk) return false;
        if (filter === 'high_risk' && s.risk_level !== 'High') return false;

        if (searchId && !s.student_id.toLowerCase().includes(searchId.toLowerCase())) return false;

        if (scoreOp !== 'all' && scoreVal1 !== '') {
            const v1 = Number(scoreVal1);
            if (scoreOp === '>' && !(s.engagement_score > v1)) return false;
            if (scoreOp === '<' && !(s.engagement_score < v1)) return false;
            if (scoreOp === '=' && !(s.engagement_score === v1)) return false;
            if (scoreOp === 'between' && scoreVal2 !== '') {
                const v2 = Number(scoreVal2);
                if (!(s.engagement_score >= Math.min(v1, v2) && s.engagement_score <= Math.max(v1, v2))) return false;
            }
        }

        if (styleFilter !== 'all') {
            const styleMatch = (s.learning_style || '').toLowerCase() === styleFilter.toLowerCase();
            if (!styleMatch) return false;
        }

        if (dateOp !== 'all' && dateVal) {
            try {
                const dt = new Date(s.last_updated);
                const rowDateStr = dt.getFullYear() + '-' + String(dt.getMonth() + 1).padStart(2, '0') + '-' + String(dt.getDate()).padStart(2, '0');
                if (dateOp === 'before' && !(rowDateStr < dateVal)) return false;
                if (dateOp === 'after' && !(rowDateStr > dateVal)) return false;
                if (dateOp === 'on' && !(rowDateStr === dateVal)) return false;
            } catch (e) {
                // Ignore parsing errors for individual rows
            }
        }

        return true;
    });

    const sortedAndDisplayed = [...displayed].sort((a, b) => {
        if (sortOrder === 'none') return 0;
        const comp = a.student_id.localeCompare(b.student_id);
        return sortOrder === 'asc' ? comp : -comp;
    });

    const stats = {
        total: students.length,
        atRisk: students.filter(s => s.at_risk).length,
        highRisk: students.filter(s => s.risk_level === 'High').length,
        avgScore: students.length
            ? Math.round(students.reduce((sum, s) => sum + s.engagement_score, 0) / students.length)
            : 0,
    };

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-900 via-emerald-900 to-teal-900 pt-20 pb-10 px-4 sm:px-8">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between flex-wrap gap-4">
                        <div>
                            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                                <BarChart3 className="w-8 h-8 text-emerald-400" />
                                EduMind Overview
                            </h1>
                            <p className="text-slate-300 mt-1 text-sm font-medium">
                                Institute: <span className="text-emerald-400">{instituteId}</span>
                            </p>
                            <p className="text-slate-400 mt-0.5 text-xs">
                                Last refreshed: {lastRefresh.toLocaleTimeString()}
                            </p>
                        </div>
                        <button
                            onClick={() => void fetchStudents()}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 text-white border border-white/20 hover:bg-white/20 transition-colors text-sm"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            Refresh
                        </button>
                    </div>

                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 text-blue-400 mb-1">
                                <Users className="w-5 h-5" />
                                <span className="text-xs font-medium text-slate-300">Total Students</span>
                            </div>
                            <div className="text-2xl font-bold text-white">{stats.total}</div>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 text-emerald-400 mb-1">
                                <Activity className="w-5 h-5" />
                                <span className="text-xs font-medium text-slate-300">Avg Engagement</span>
                            </div>
                            <div className="text-2xl font-bold text-white">{stats.avgScore}%</div>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 text-purple-400 mb-1">
                                <Brain className="w-5 h-5" />
                                <span className="text-xs font-medium text-slate-300">Average Learning Style</span>
                            </div>
                            <div className="text-2xl font-bold text-white">{avgLearningStyle}</div>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 text-slate-400 mb-1">
                                <span className="text-xs font-medium text-slate-400">—</span>
                            </div>
                            <div className="text-2xl font-bold text-white/50">—</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8">
                {/* Filter Tabs */}
                <div className="flex gap-2 mb-6 flex-wrap">
                    {[
                        { key: 'all', label: 'All Students' },
                        { key: 'at_risk', label: 'At Risk' },
                        { key: 'high_risk', label: 'High Risk Only' },
                    ].map(tab => (
                        <button
                            key={tab.key}
                            onClick={() => setFilter(tab.key as typeof filter)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === tab.key
                                ? 'bg-emerald-600 text-white shadow'
                                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
                                }`}
                        >
                            {tab.label}
                            <span className="ml-2 text-xs opacity-70">
                                ({tab.key === 'all' ? stats.total : tab.key === 'at_risk' ? stats.atRisk : stats.highRisk})
                            </span>
                        </button>
                    ))}
                </div>

                {/* Advanced Filters */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6 shadow-sm flex flex-col gap-4">
                    <div className="text-sm font-semibold text-slate-700 flex justify-between items-center">
                        Advanced Filters
                        <button
                            onClick={() => {
                                setSearchId(''); setScoreOp('all'); setScoreVal1(''); setScoreVal2('');
                                setStyleFilter('all'); setDateOp('all'); setDateVal('');
                                setSortOrder('none');
                            }}
                            className="text-xs text-slate-500 hover:text-slate-700 underline font-normal px-2"
                        >
                            Clear Filters
                        </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Student ID Search & Sort */}
                        <div className="flex flex-col gap-1.5">
                            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Search / Sort by ID</label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="e.g. STU0001"
                                    className="flex-1 min-w-[100px] px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                    value={searchId}
                                    onChange={e => setSearchId(e.target.value)}
                                />
                                <select
                                    className="w-[90px] px-2 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                    value={sortOrder}
                                    onChange={e => setSortOrder(e.target.value as any)}
                                >
                                    <option value="none">Sort</option>
                                    <option value="asc">ID Asc</option>
                                    <option value="desc">ID Desc</option>
                                </select>
                            </div>
                        </div>

                        {/* Engagement Score */}
                        <div className="flex flex-col gap-1.5">
                            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Engagement Score</label>
                            <div className="flex flex-wrap gap-2">
                                <select
                                    className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 min-w-0"
                                    value={scoreOp}
                                    onChange={e => setScoreOp(e.target.value as any)}
                                >
                                    <option value="all">Any</option>
                                    <option value=">">Greater</option>
                                    <option value="<">Less</option>
                                    <option value="=">Exact</option>
                                    <option value="between">Between</option>
                                </select>
                                {scoreOp !== 'all' && (
                                    <input
                                        type="number"
                                        className="flex-1 min-w-[60px] px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                        placeholder="Val 1"
                                        value={scoreVal1}
                                        onChange={e => setScoreVal1(e.target.value ? Number(e.target.value) : '')}
                                    />
                                )}
                                {scoreOp === 'between' && (
                                    <input
                                        type="number"
                                        className="flex-1 min-w-[60px] px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                        placeholder="Val 2"
                                        value={scoreVal2}
                                        onChange={e => setScoreVal2(e.target.value ? Number(e.target.value) : '')}
                                    />
                                )}
                            </div>
                        </div>

                        {/* Learning Style */}
                        <div className="flex flex-col gap-1.5">
                            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Learning Style</label>
                            <select
                                className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                value={styleFilter}
                                onChange={e => setStyleFilter(e.target.value)}
                            >
                                <option value="all">All Styles</option>
                                <option value="auditory">Auditory</option>
                                <option value="visual">Visual</option>
                                <option value="reading">Reading</option>
                                <option value="kinesthetic">Kinesthetic</option>
                            </select>
                        </div>

                        {/* Date Filter */}
                        <div className="flex flex-col gap-1.5">
                            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Last Updated</label>
                            <div className="flex gap-2">
                                <select
                                    className="w-[100px] px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                    value={dateOp}
                                    onChange={e => setDateOp(e.target.value as any)}
                                >
                                    <option value="all">Any</option>
                                    <option value="before">Before</option>
                                    <option value="after">After</option>
                                    <option value="on">On</option>
                                </select>
                                {dateOp !== 'all' && (
                                    <input
                                        type="date"
                                        className="flex-1 w-[120px] px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                        value={dateVal}
                                        onChange={e => setDateVal(e.target.value)}
                                    />
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-center gap-3 text-red-700">
                        <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                        <div>
                            <p className="font-medium">Could not load student data</p>
                            <p className="text-sm text-red-500">{error} — make sure the engagement tracker is running on port 8005.</p>
                        </div>
                    </div>
                )}

                {/* Loading */}
                {loading && (
                    <div className="space-y-3">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="bg-white rounded-xl p-4 border border-slate-200 animate-pulse h-16" />
                        ))}
                    </div>
                )}

                {/* Empty */}
                {!loading && !error && displayed.length === 0 && (
                    <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                        <CheckCircle className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                        <p className="text-slate-500 font-medium">No students found</p>
                        <p className="text-slate-400 text-sm mt-1">
                            {filter !== 'all' ? 'Try switching to "All Students"' : 'Run the seed script to generate demo data.'}
                        </p>
                    </div>
                )}

                {/* Student Table */}
                {!loading && displayed.length > 0 && (
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-slate-50 border-b border-slate-200">
                                        <th className="text-left px-6 py-4 text-slate-500 font-semibold">Student ID</th>
                                        <th className="text-left px-6 py-4 text-slate-500 font-semibold">Engagement Score</th>
                                        <th className="text-left px-6 py-4 text-slate-500 font-semibold">Learning Style</th>
                                        <th className="text-left px-6 py-4 text-slate-500 font-semibold">Last Updated</th>
                                        <th className="text-left px-6 py-4 text-slate-500 font-semibold">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {sortedAndDisplayed.map(student => (
                                        <tr
                                            key={student.student_id}
                                            className="hover:bg-slate-50/60 transition-colors group"
                                        >
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-xs">
                                                        {student.student_id.replace(/\D/g, '').slice(-2) || '?'}
                                                    </div>
                                                    <span className="font-semibold text-slate-800">{student.student_id}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full transition-all ${SCORE_BAR_COLOR(student.engagement_score)}`}
                                                            style={{ width: `${Math.min(student.engagement_score, 100)}%` }}
                                                        />
                                                    </div>
                                                    <span className="font-semibold text-slate-700 w-10">
                                                        {student.engagement_score}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-slate-600">{student.learning_style ?? '—'}</span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-400 text-xs">
                                                {student.last_updated}
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <button
                                                        onClick={() => navigate({
                                                            to: '/engagement',
                                                            search: { student_id: student.student_id },
                                                        })}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 hover:border-emerald-300 text-xs font-semibold transition-all duration-150 whitespace-nowrap"
                                                    >
                                                        <Activity className="w-3.5 h-3.5" />
                                                        Engagement
                                                    </button>
                                                    <button
                                                        onClick={() => navigate({
                                                            to: '/learning-style',
                                                            search: { student_id: student.student_id },
                                                        })}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 hover:border-purple-300 text-xs font-semibold transition-all duration-150 whitespace-nowrap"
                                                    >
                                                        <Brain className="w-3.5 h-3.5" />
                                                        Learning Style
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-400">
                            Showing {sortedAndDisplayed.length} of {students.length} students
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

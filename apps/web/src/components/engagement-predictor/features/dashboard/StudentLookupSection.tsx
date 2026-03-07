import { ArrowRight, Loader2, Search, RefreshCw, ArrowLeft } from 'lucide-react';
import type { QuickStudent } from '../../core/types/dashboard';

interface StudentLookupSectionProps {
    studentInput: string;
    quickStudents: QuickStudent[];
    isLoadingDashboard: boolean;
    error: string | null;
    onStudentInputChange: (value: string) => void;
    onQuickSelect: (studentId: string) => Promise<void>;
    onLoadStudentDashboard: () => Promise<void>;
}

export function StudentLookupSection({
    studentInput,
    quickStudents,
    isLoadingDashboard,
    error,
    onStudentInputChange,
    onQuickSelect,
    onLoadStudentDashboard,
}: StudentLookupSectionProps) {
    return (
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <button
                        type="button"
                        onClick={() => {
                            window.location.href = '/engagement-overview';
                        }}
                        className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                        title="Back to Overview"
                    >
                        <ArrowLeft className="h-4 w-4" />
                    </button>
                    <div>
                        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Student Analytics Lookup</h2>
                        <p className="text-sm text-slate-600 dark:text-slate-400">Enter a student ID to view comprehensive engagement analytics and predictions</p>
                    </div>
                </div>
                <button
                    type="button"
                    onClick={() => {
                        if (studentInput) {
                            void onLoadStudentDashboard();
                        }
                    }}
                    disabled={isLoadingDashboard || !studentInput}
                    className="inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                    title="Refresh Dashboard"
                >
                    <RefreshCw className={`h-4 w-4 ${isLoadingDashboard ? 'animate-spin' : ''}`} />
                    <span className="hidden sm:inline">Refresh</span>
                </button>
            </div>

            <div className="mt-4 grid gap-4">
                <div className="grid gap-1.5">
                    <label htmlFor="studentInput" className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">Student ID</label>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 dark:text-slate-400" />
                        <input
                            id="studentInput"
                            type="text"
                            className="h-11 w-full rounded-xl border border-slate-300 bg-white pl-10 pr-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-400"
                            placeholder="Type student ID (e.g., STU0001)"
                            value={studentInput}
                            onChange={(event) => onStudentInputChange(event.target.value)}
                        />
                    </div>
                </div>

                <div className="grid gap-2">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">Quick Select Examples</p>
                    <div className="flex flex-wrap gap-2">
                        {quickStudents.map((student) => (
                            <button
                                key={student.id}
                                type="button"
                                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                onClick={() => void onQuickSelect(student.id)}
                            >
                                <span>{student.label}</span>
                                <span className="text-xs text-slate-500 dark:text-slate-400">{student.id}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <button
                        type="button"
                        className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0"
                        onClick={() => void onLoadStudentDashboard()}
                        disabled={isLoadingDashboard}
                    >
                        {isLoadingDashboard ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                        <span>{isLoadingDashboard ? 'Loading...' : 'Load Student Dashboard'}</span>
                    </button>
                </div>

                {error ? (
                    <div className="rounded-xl border border-red-300 bg-red-50 p-3 text-sm font-medium text-red-700">
                        {error}
                    </div>
                ) : null}
            </div>
        </section>
    );
}

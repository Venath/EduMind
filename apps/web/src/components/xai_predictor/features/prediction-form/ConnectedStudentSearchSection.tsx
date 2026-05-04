import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/store/authStore';
import { Brain, Loader2, Search, Wand2 } from 'lucide-react';
import { KeyboardEvent } from 'react';
import { useFormContext } from 'react-hook-form';
import type { StudentRiskRequest } from '../../core/services/xaiService';
import {
    formatRiskBadgeLabel,
    getEngagementBadgeClass,
    getRiskBadgeClass,
} from './statusStyles';
import { useConnectedStudentSearch } from './useConnectedStudentSearch';

type ConnectedStudentSearchSectionProps = {
    isAnalyzing: boolean;
    onAnalyzeStudent: (studentId: string) => Promise<void>;
    prefilledStudentId?: string;
};

export function ConnectedStudentSearchSection({
    isAnalyzing,
    onAnalyzeStudent,
    prefilledStudentId,
}: ConnectedStudentSearchSectionProps) {
    const { user } = useAuth();
    const { setValue } = useFormContext<StudentRiskRequest>();
    const instituteId = user?.institute_id ?? 'LMS_INST_A';
    const {
        query,
        setQuery,
        results,
        isSearching,
        hasSearched,
        error,
        searchStudents,
    } = useConnectedStudentSearch({
        instituteId,
        prefilledStudentId,
        onPrefillStudentId: (studentId) =>
            setValue('student_id', studentId, {
                shouldDirty: true,
                shouldTouch: true,
                shouldValidate: true,
            }),
    });

    const handleSearch = async (nextQuery?: string) => {
        if (nextQuery) {
            setQuery(nextQuery);
        }

        await searchStudents(nextQuery);
    };

    const handleUseStudentId = (studentId: string) => {
        setValue('student_id', studentId, {
            shouldDirty: true,
            shouldTouch: true,
            shouldValidate: true,
        });
    };

    const handleAnalyze = async (studentId: string) => {
        setValue('student_id', studentId, {
            shouldDirty: true,
            shouldTouch: true,
            shouldValidate: true,
        });
        await onAnalyzeStudent(studentId);
    };

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            void handleSearch();
        }
    };

    return (
        <section className="rounded-2xl border border-slate-200 bg-background p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950/70">
            <div className="mb-3">
                <div className="mb-2 inline-flex rounded-full bg-indigo-100 px-2.5 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">
                    Existing Student
                </div>
                <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-slate-50">
                    <Brain className="h-4 w-4 text-indigo-600 dark:text-indigo-300" />
                    Student Analytics Lookup
                </h2>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                    Enter a student ID to view explainable risk analytics and predictions.
                </p>
            </div>

            <div className="grid grid-cols-1 items-end gap-3 md:grid-cols-[1fr_auto]">
                <div className="relative grid gap-1.5">
                    <label
                        htmlFor="studentLookup"
                        className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
                    >
                        Student ID
                    </label>
                    <div className="relative">
                        <Search
                            className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 dark:text-slate-400"
                            aria-hidden="true"
                        />
                        <Input
                            id="studentLookup"
                            value={query}
                            onChange={(event) => setQuery(event.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Type student ID (e.g., STU0001)"
                            className="h-11 rounded-xl border-slate-300 bg-background pl-10 text-sm text-slate-900 placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-950"
                        />
                    </div>
                </div>
                <Button
                    type="button"
                    onClick={() => void handleSearch()}
                    disabled={isSearching}
                    className="h-11 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0 dark:shadow-indigo-950/60"
                >
                    {isSearching ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Loading
                        </>
                    ) : (
                        <>
                            <Search className="mr-2 h-4 w-4" />
                            Load Student Record
                        </>
                    )}
                </Button>
            </div>

            {error && (
                <div className="mt-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300">
                    {error}
                </div>
            )}

            {results.length > 0 && (
                <div className="mt-4 space-y-3">
                    {results.map((student) => (
                        <div
                            key={student.student_id}
                            className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-indigo-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-950/75 dark:hover:border-indigo-900"
                        >
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                <div className="space-y-2">
                                    <div className="flex items-center gap-2">
                                        <span className="text-base font-semibold text-slate-900 dark:text-slate-50">
                                            {student.student_id}
                                        </span>
                                        <Badge
                                            variant="outline"
                                            className={getEngagementBadgeClass(student.engagement_level)}
                                        >
                                            {student.engagement_level} engagement
                                        </Badge>
                                        <Badge
                                            variant="outline"
                                            className={getRiskBadgeClass(student.risk_level)}
                                        >
                                            {formatRiskBadgeLabel(student.risk_level)}
                                        </Badge>
                                    </div>
                                    <div className="flex flex-wrap gap-2 text-xs text-slate-600 dark:text-slate-400">
                                        {student.engagement_level !== 'Unavailable' ? (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Engagement score: {student.engagement_score.toFixed(1)}
                                            </span>
                                        ) : typeof student.risk_probability === 'number' ? (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Last risk score: {(student.risk_probability * 100).toFixed(1)}%
                                            </span>
                                        ) : (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Using stored XAI history
                                            </span>
                                        )}
                                        {student.learning_style && (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Learning style: {student.learning_style}
                                            </span>
                                        )}
                                        {typeof student.avg_completion_rate === 'number' && (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Completion: {student.avg_completion_rate.toFixed(1)}%
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={() => handleUseStudentId(student.student_id)}
                                        className="rounded-xl"
                                    >
                                        Use ID
                                    </Button>
                                    <Button
                                        type="button"
                                        onClick={() => void handleAnalyze(student.student_id)}
                                        disabled={isAnalyzing}
                                        className="rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 text-white shadow-lg shadow-indigo-500/30 hover:-translate-y-0.5 dark:shadow-indigo-950/60"
                                    >
                                        {isAnalyzing ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Analyzing
                                            </>
                                        ) : (
                                            <>
                                                <Wand2 className="mr-2 h-4 w-4" />
                                                Analyze
                                            </>
                                        )}
                                    </Button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {hasSearched && !isSearching && results.length === 0 && !error && (
                <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
                    No students matched that search.
                </div>
            )}
        </section>
    );
}

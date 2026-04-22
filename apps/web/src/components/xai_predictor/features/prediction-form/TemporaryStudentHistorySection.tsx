import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { History, Loader2, RefreshCw, Search, Sparkles } from 'lucide-react';
import type { KeyboardEvent } from 'react';
import { getRiskBadgeClass } from './statusStyles';
import { useTemporaryStudentHistory } from './useTemporaryStudentHistory';

type TemporaryStudentHistorySectionProps = {
    isLoadingPrediction: boolean;
    onOpenStudent: (studentId: string) => Promise<void>;
    refreshToken: number;
};

function formatUpdatedAt(value?: string | null): string {
    if (!value) {
        return 'Not recorded';
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return 'Not recorded';
    }

    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
    }).format(date);
}

export function TemporaryStudentHistorySection({
    isLoadingPrediction,
    onOpenStudent,
    refreshToken,
}: TemporaryStudentHistorySectionProps) {
    const {
        query,
        setQuery,
        records,
        isLoading,
        error,
        hasLoaded,
        totalLabel,
        loadRecords,
    } = useTemporaryStudentHistory({ refreshToken });

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            void loadRecords(query);
        }
    };

    return (
        <section className="rounded-2xl border border-slate-200 bg-background p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950/70">
            <div className="mb-3 flex items-start justify-between gap-3">
                <div>
                    <div className="mb-2 inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                        {totalLabel}
                    </div>
                    <h3 className="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-slate-50">
                        <History className="h-4 w-4 text-emerald-600 dark:text-emerald-300" />
                        Saved Temporary Students
                    </h3>
                    <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                        Reopen a saved temporary student record.
                    </p>
                </div>
                <Button
                    type="button"
                    variant="outline"
                    onClick={() => void loadRecords(query)}
                    disabled={isLoading}
                    className="rounded-xl"
                >
                    {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                        <RefreshCw className="h-4 w-4" />
                    )}
                </Button>
            </div>

            <div className="grid grid-cols-1 items-end gap-3 md:grid-cols-[1fr_auto]">
                <div className="grid gap-1.5">
                    <label
                        htmlFor="temporaryStudentLookup"
                        className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
                    >
                        Temporary Student ID
                    </label>
                    <div className="relative">
                        <Search
                            className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 dark:text-slate-400"
                            aria-hidden="true"
                        />
                        <Input
                            id="temporaryStudentLookup"
                            value={query}
                            onChange={(event) => setQuery(event.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Search saved temporary students"
                            className="h-11 rounded-xl border-slate-300 bg-background pl-10 text-sm text-slate-900 placeholder:text-slate-500 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-emerald-400 dark:focus:ring-emerald-950"
                        />
                    </div>
                </div>
                <Button
                    type="button"
                    onClick={() => void loadRecords(query)}
                    disabled={isLoading}
                    className="h-11 rounded-xl bg-emerald-600 px-4 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-700 dark:shadow-emerald-950/60"
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Loading
                        </>
                    ) : (
                        <>
                            <Search className="mr-2 h-4 w-4" />
                            Find Saved Records
                        </>
                    )}
                </Button>
            </div>

            {error ? (
                <div className="mt-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300">
                    {error}
                </div>
            ) : null}

            {records.length > 0 ? (
                <div className="mt-4 space-y-3">
                    {records.map((record) => (
                        <div
                            key={record.student_id}
                            className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-emerald-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-950/75 dark:hover:border-emerald-900"
                        >
                            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                                <div className="space-y-2">
                                    <div className="flex items-center gap-2">
                                        <span className="text-base font-semibold text-slate-900 dark:text-slate-50">
                                            {record.student_id}
                                        </span>
                                        <Badge
                                            variant="outline"
                                            className={getRiskBadgeClass(record.latest_risk_level)}
                                        >
                                            {record.latest_risk_level ?? 'Prediction pending'}
                                        </Badge>
                                    </div>
                                    <div className="flex flex-wrap gap-2 text-xs text-slate-600 dark:text-slate-400">
                                        <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                            Average grade: {record.avg_grade.toFixed(1)}%
                                        </span>
                                        {typeof record.latest_confidence === 'number' ? (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Prediction certainty: {(record.latest_confidence * 100).toFixed(0)}%
                                            </span>
                                        ) : null}
                                        {typeof record.latest_risk_score === 'number' ? (
                                            <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                                Risk score: {(record.latest_risk_score * 100).toFixed(1)}%
                                            </span>
                                        ) : null}
                                        <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                                            Updated: {formatUpdatedAt(record.updated_at)}
                                        </span>
                                    </div>
                                </div>

                                <Button
                                    type="button"
                                    onClick={() => void onOpenStudent(record.student_id)}
                                    disabled={isLoadingPrediction}
                                    className="rounded-xl bg-slate-900 text-white hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-slate-200"
                                >
                                    {isLoadingPrediction ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Opening
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="mr-2 h-4 w-4" />
                                            Open Prediction
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            ) : null}

            {hasLoaded && !isLoading && records.length === 0 && !error ? (
                <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
                    No saved temporary students matched that search.
                </div>
            ) : null}

            {query.trim() ? (
                <div className="mt-3 flex justify-end">
                    <Button
                        type="button"
                        variant="ghost"
                        className="rounded-xl text-xs text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                        onClick={() => {
                            setQuery('');
                            void loadRecords('');
                        }}
                    >
                        Show All Temporary Students
                    </Button>
                </div>
            ) : null}
        </section>
    );
}

import { AlertTriangle, Brain, CheckCircle2, Sparkles, Users } from 'lucide-react';

type XAIOverviewSectionProps = {
    systemStatus: 'healthy' | 'degraded' | 'checking' | 'offline';
    systemMessage: string;
    currentStudentId?: string;
    latestRiskLevel?: string;
    confidence?: number;
    modelLoaded: boolean;
};

function formatPredictionCertainty(value?: number): string {
    if (typeof value !== 'number' || Number.isNaN(value)) {
        return '--';
    }

    const normalized = value <= 1 ? value * 100 : value;
    return `${Math.round(normalized)}%`;
}

function getRiskCardStyles(riskLevel?: string): {
    card: string;
    icon: string;
} {
    const normalized = (riskLevel || '').trim().toLowerCase();

    if (normalized.includes('safe')) {
        return {
            card: 'border-emerald-200 dark:border-emerald-900',
            icon: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300',
        };
    }

    if (normalized.includes('medium')) {
        return {
            card: 'border-yellow-200 dark:border-yellow-900',
            icon: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950/60 dark:text-yellow-300',
        };
    }

    return {
        card: 'border-red-200 dark:border-red-900',
        icon: 'bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300',
    };
}

export function XAIOverviewSection({
    systemStatus,
    systemMessage,
    currentStudentId,
    latestRiskLevel,
    confidence,
    modelLoaded,
}: XAIOverviewSectionProps) {
    const riskCardStyles = getRiskCardStyles(latestRiskLevel);

    return (
        <>
            <section className="rounded-2xl border border-slate-200 bg-white/90 p-4 shadow-sm backdrop-blur dark:border-slate-800 dark:bg-slate-950/75">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div className="flex items-center gap-3">
                        <div className="grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-md shadow-indigo-500/30">
                            <Brain className="h-6 w-6" />
                        </div>
                        <div>
                            <h1 className="text-lg font-extrabold text-slate-900 dark:text-slate-50">EduMind Analytics</h1>
                            <p className="text-sm text-slate-600 dark:text-slate-400">Explainable Student Risk Intelligence Platform</p>
                        </div>
                    </div>

                    <div
                        className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${systemStatus === 'healthy'
                            ? 'border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300'
                            : systemStatus === 'degraded'
                                ? 'border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/60 dark:text-amber-300'
                                : systemStatus === 'checking'
                                    ? 'border-slate-300 bg-slate-50 text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300'
                                    : 'border-red-300 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300'
                            }`}
                    >
                        <span
                            className={`h-2 w-2 rounded-full ${systemStatus === 'healthy'
                                ? 'bg-emerald-500'
                                : systemStatus === 'degraded'
                                    ? 'bg-amber-500'
                                    : systemStatus === 'checking'
                                        ? 'bg-slate-500'
                                        : 'bg-red-500'
                                }`}
                        />
                        <span>
                            {systemStatus === 'healthy'
                                ? 'System Online'
                                : systemStatus === 'degraded'
                                    ? 'System Degraded'
                                    : systemStatus === 'checking'
                                        ? 'Checking...'
                                        : 'System Offline'}
                        </span>
                    </div>
                </div>
                <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">{systemMessage}</p>
            </section>

            <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <article className="rounded-xl border border-indigo-200 bg-white p-4 shadow-sm dark:border-indigo-900 dark:bg-slate-950/75">
                    <div className="mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">
                        <Users className="h-4 w-4" />
                    </div>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-slate-50">{currentStudentId || '--'}</div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Current Student</div>
                </article>

                <article className={`rounded-xl border bg-white p-4 shadow-sm dark:bg-slate-950/75 ${riskCardStyles.card}`}>
                    <div className={`mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg ${riskCardStyles.icon}`}>
                        <AlertTriangle className="h-4 w-4" />
                    </div>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-slate-50">{latestRiskLevel || '--'}</div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Latest Risk</div>
                </article>

                <article className="rounded-xl border border-amber-200 bg-white p-4 shadow-sm dark:border-amber-900 dark:bg-slate-950/75">
                    <div className="mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">
                        <Sparkles className="h-4 w-4" />
                    </div>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-slate-50">{formatPredictionCertainty(confidence)}</div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Prediction Certainty</div>
                </article>

                <article className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm dark:border-emerald-900 dark:bg-slate-950/75">
                    <div className="mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                        <CheckCircle2 className="h-4 w-4" />
                    </div>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-slate-50">{modelLoaded ? 'Insights Available' : 'Insights Unavailable'}</div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Analysis Access</div>
                </article>
            </section>
        </>
    );
}

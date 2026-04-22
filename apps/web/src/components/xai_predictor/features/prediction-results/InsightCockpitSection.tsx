import {
    Layers3,
    ShieldCheck,
    Sparkles,
    Target,
    TrendingDown,
    Users,
    WandSparkles,
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

import type {
    RiskPredictionResponse,
    StudentInsightsResponse,
} from '../../core/services/xaiService';
import { formatRiskBadgeLabel, getRiskBadgeClass } from '../prediction-form/statusStyles';

type InsightCockpitSectionProps = {
    prediction: RiskPredictionResponse;
    insights: StudentInsightsResponse;
    source: 'connected' | 'temporary';
};

function formatPercent(value?: number | null, digits = 0): string {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    return `${value.toFixed(digits)}%`;
}

function formatPercentile(value?: number | null, digits = 0): string {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    return `${value.toFixed(digits)}th percentile`;
}

function getOutcomeTone(riskLevel: string) {
    const normalized = riskLevel.toLowerCase();
    if (normalized.includes('safe')) {
        return {
            chip: 'from-emerald-400/80 via-emerald-500 to-emerald-600',
            glow: 'shadow-[0_0_80px_rgba(16,185,129,0.25)]',
            ring: 'border-emerald-300/60 dark:border-emerald-700/50',
        };
    }
    if (normalized.includes('medium')) {
        return {
            chip: 'from-amber-300/90 via-amber-400 to-yellow-500',
            glow: 'shadow-[0_0_80px_rgba(245,158,11,0.28)]',
            ring: 'border-amber-300/60 dark:border-amber-700/50',
        };
    }
    return {
        chip: 'from-rose-400/90 via-rose-500 to-red-600',
        glow: 'shadow-[0_0_80px_rgba(244,63,94,0.28)]',
        ring: 'border-rose-300/60 dark:border-rose-700/50',
    };
}

function getTrajectoryCounts(insights: StudentInsightsResponse) {
    return insights.case_outcome_explorer?.cases.reduce(
        (acc, item) => {
            const key = item.trajectory.toLowerCase();
            if (key.includes('improv')) {
                acc.improving += 1;
            } else if (key.includes('worsen')) {
                acc.worsening += 1;
            } else {
                acc.stable += 1;
            }
            return acc;
        },
        { improving: 0, stable: 0, worsening: 0 }
    ) ?? { improving: 0, stable: 0, worsening: 0 };
}

function getFairnessHeadline(parityScore?: number | null) {
    if (parityScore === null || parityScore === undefined || Number.isNaN(parityScore)) {
        return 'Not enough data';
    }
    if (parityScore >= 80) {
        return 'Broadly aligned';
    }
    if (parityScore >= 60) {
        return 'Needs monitoring';
    }
    return 'Bias watch needed';
}

function getStabilityHeadline(score?: number | null) {
    if (score === null || score === undefined || Number.isNaN(score)) {
        return 'Not enough data';
    }
    if (score >= 85) {
        return 'Very stable';
    }
    if (score >= 65) {
        return 'Mostly stable';
    }
    return 'Sensitive';
}

export function InsightCockpitSection({
    prediction,
    insights,
    source,
}: InsightCockpitSectionProps) {
    const cohort = insights.cohort_comparison;
    const fairness = insights.fairness_evaluation;
    const stability = insights.explanation_stability;
    const caseExplorer = insights.case_outcome_explorer;
    const bestInterventions = insights.interventions.slice(0, 3);
    const trajectoryCounts = getTrajectoryCounts(insights);
    const maxTrajectoryCount = Math.max(
        trajectoryCounts.improving,
        trajectoryCounts.stable,
        trajectoryCounts.worsening,
        1
    );
    const totalCases = caseExplorer?.cases.length ?? 0;
    const cohortRiskPercentile = cohort?.risk_percentile ?? null;
    const topIntervention = bestInterventions[0] ?? null;
    const certainty = prediction.confidence <= 1 ? prediction.confidence * 100 : prediction.confidence;
    const tone = getOutcomeTone(prediction.risk_level);
    const orbitAngle = ((cohortRiskPercentile ?? prediction.risk_score * 100) / 100) * 300 - 150;
    const orbitRadians = (orbitAngle * Math.PI) / 180;
    const orbitX = 50 + Math.cos(orbitRadians) * 30;
    const orbitY = 50 + Math.sin(orbitRadians) * 30;
    const scoreBars = [
        {
            label: 'Fairness parity',
            value: fairness?.parity_score ?? null,
            helper: fairness
                ? `${getFairnessHeadline(fairness.parity_score)} across monitored groups`
                : 'Fairness evaluation unavailable',
            className: 'from-emerald-400 via-emerald-500 to-teal-500',
        },
        {
            label: 'Explanation stability',
            value: stability?.stability_score ?? null,
            helper: stability
                ? `${getStabilityHeadline(stability.stability_score)} under local perturbations`
                : 'Stability diagnostics unavailable',
            className: 'from-sky-400 via-blue-500 to-indigo-500',
        },
        {
            label: 'Prediction certainty',
            value: certainty,
            helper: `${formatRiskBadgeLabel(prediction.risk_level)} is the leading modeled outcome`,
            className: 'from-fuchsia-400 via-violet-500 to-indigo-500',
        },
    ];

    return (
        <Card className="lg:col-span-12 overflow-hidden border shadow-sm">
            <CardHeader className="border-b bg-muted/20">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div className="max-w-2xl space-y-1">
                        <CardTitle className="flex items-center gap-2 text-lg">
                            <Sparkles className="h-5 w-5 text-primary" />
                            Strategic Insight Cockpit
                        </CardTitle>
                        <CardDescription>
                            Integrated view of risk position, intervention lift, and trust signals for this{' '}
                            {source === 'connected' ? 'connected' : 'temporary'} student analysis.
                        </CardDescription>
                    </div>
                    <span
                        className={`inline-flex w-fit self-start items-center rounded-full border px-3 py-1 text-xs font-semibold ${getRiskBadgeClass(
                            prediction.risk_level
                        )}`}
                    >
                        {formatRiskBadgeLabel(prediction.risk_level)}
                    </span>
                </div>
            </CardHeader>
            <CardContent className="grid gap-6 p-6 xl:grid-cols-[1.15fr_1fr_1fr]">
                <div className="relative overflow-hidden rounded-[1.5rem] border border-border/60 bg-gradient-to-br from-background via-background to-muted/25 p-5">
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
                                Risk core
                            </p>
                            <p className="mt-1 text-sm text-muted-foreground">
                                Current risk position with the strongest trust and lift signals.
                            </p>
                        </div>
                        <Target className="h-5 w-5 text-primary" />
                    </div>

                    <div className="space-y-5">
                        <div className="relative flex min-h-[18rem] items-center justify-center" style={{ perspective: '1200px' }}>
                            <div className="relative h-56 w-56 animate-in fade-in zoom-in-95 duration-700">
                                <div className="absolute inset-0 rounded-full border border-border/40" />
                                <div className="absolute inset-[16%] rounded-full border border-border/25" />
                                <div className="absolute inset-[8%] rounded-full border border-dashed border-primary/20 animate-spin" style={{ animationDuration: '24s' }} />
                                <div className="absolute left-1/2 top-1/2 w-36 -translate-x-1/2 -translate-y-1/2 rounded-[1.75rem] border border-border/70 bg-background/95 px-4 py-4 text-center shadow-xl backdrop-blur">
                                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                                        Risk score
                                    </p>
                                    <p className="mt-2 text-3xl font-bold text-foreground">
                                        {(prediction.risk_score * 100).toFixed(0)}%
                                    </p>
                                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-muted">
                                        <div
                                            className={`h-full rounded-full bg-gradient-to-r ${tone.chip} transition-[width] duration-1000 ease-out`}
                                            style={{ width: `${Math.max(Math.min(prediction.risk_score * 100, 100), 0)}%` }}
                                        />
                                    </div>
                                    <span
                                        className={`mt-3 inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold ${getRiskBadgeClass(
                                            prediction.risk_level
                                        )}`}
                                    >
                                        {formatRiskBadgeLabel(prediction.risk_level)}
                                    </span>
                                    <p className="mt-2 text-[11px] font-medium text-muted-foreground">
                                        Current XAI position
                                    </p>
                                </div>
                                <div
                                    className="absolute h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-4 border-background bg-primary shadow-[0_0_24px_rgba(59,130,246,0.45)] transition-all duration-700"
                                    style={{ left: `${orbitX}%`, top: `${orbitY}%` }}
                                />
                                <div
                                    className={`absolute left-1/2 top-1/2 h-[9.5rem] w-[9.5rem] -translate-x-1/2 -translate-y-1/2 rounded-full border ${tone.ring} opacity-55`}
                                    style={{ transform: 'translate(-50%, -50%) rotateX(62deg)' }}
                                />
                            </div>
                        </div>

                        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                            {scoreBars.map((bar, index) => (
                                <div
                                    key={bar.label}
                                    className="animate-in rounded-2xl border border-border/60 bg-background/90 p-4 shadow-sm fade-in-0 slide-in-from-bottom-4 duration-500"
                                    style={{ animationDelay: `${index * 90}ms` }}
                                >
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                        {bar.label}
                                    </p>
                                    <p className="mt-2 text-2xl font-semibold text-foreground">
                                        {bar.value !== null ? `${bar.value.toFixed(1)}/100` : '—'}
                                    </p>
                                    <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-muted/80">
                                        <div
                                            className={`h-full rounded-full bg-gradient-to-r ${bar.className} transition-[width] duration-1000 ease-out`}
                                            style={{ width: `${Math.max(Math.min(bar.value ?? 0, 100), 0)}%` }}
                                        />
                                    </div>
                                    <p className="mt-3 min-h-[2rem] text-xs font-medium leading-relaxed text-muted-foreground">
                                        {bar.helper}
                                    </p>
                                </div>
                            ))}
                            <div className="rounded-2xl border border-border/60 bg-background/90 p-4 shadow-sm">
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                    Cohort orbit
                                </p>
                                <p className="mt-2 text-xl font-semibold text-foreground">
                                    {cohortRiskPercentile !== null
                                        ? formatPercentile(cohortRiskPercentile, 0)
                                        : '—'}
                                </p>
                                <p className="mt-1 text-xs font-medium text-muted-foreground">
                                    Student risk position within the active cohort
                                </p>
                            </div>
                            <div className="rounded-2xl border border-border/60 bg-background/90 p-4 shadow-sm">
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                    Best lift
                                </p>
                                <p className="mt-2 text-xl font-semibold text-foreground">
                                    {topIntervention
                                        ? formatPercent(topIntervention.expected_risk_reduction * 100, 1)
                                        : '—'}
                                </p>
                                <p className="mt-1 text-xs font-medium text-muted-foreground">
                                    {topIntervention?.title ?? 'No ranked intervention available yet.'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="rounded-[1.5rem] border border-border/60 bg-background p-5 shadow-sm">
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
                                Intervention lift deck
                            </p>
                            <p className="mt-1 text-sm text-muted-foreground">
                                Highest-value scenarios from the current XAI profile.
                            </p>
                        </div>
                        <WandSparkles className="h-5 w-5 text-primary" />
                    </div>
                    <div className="space-y-4">
                        {bestInterventions.length === 0 ? (
                            <p className="text-sm text-muted-foreground">
                                No intervention scenarios are available yet.
                            </p>
                        ) : (
                            bestInterventions.map((intervention, index) => {
                                const currentRisk = prediction.risk_score * 100;
                                const projectedRisk = intervention.expected_new_risk_score * 100;
                                const shift = Math.max(currentRisk - projectedRisk, 0);
                                return (
                                    <div
                                        key={intervention.title}
                                        className="animate-in rounded-2xl border border-border/60 bg-muted/10 p-4 fade-in-0 slide-in-from-bottom-4 duration-500"
                                        style={{ animationDelay: `${index * 110}ms` }}
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                                                    Option {intervention.rank}
                                                </p>
                                                <p className="mt-1 text-base font-semibold text-foreground">
                                                    {intervention.title}
                                                </p>
                                            </div>
                                            <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-semibold text-muted-foreground">
                                                {intervention.effort} effort
                                            </span>
                                        </div>

                                        <div className="mt-4 space-y-3">
                                            <div className="grid gap-2 sm:grid-cols-3">
                                                <div className="rounded-xl bg-background/90 p-3">
                                                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                                        Current
                                                    </p>
                                                    <p className="mt-1 text-lg font-semibold text-foreground">
                                                        {formatPercent(currentRisk, 1)}
                                                    </p>
                                                </div>
                                                <div className="rounded-xl bg-background/90 p-3">
                                                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                                        Projected
                                                    </p>
                                                    <p className="mt-1 text-lg font-semibold text-foreground">
                                                        {formatPercent(projectedRisk, 1)}
                                                    </p>
                                                </div>
                                                <div className="rounded-xl bg-background/90 p-3">
                                                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                                        Shift
                                                    </p>
                                                    <p className="mt-1 text-lg font-semibold text-foreground">
                                                        {shift > 0.05 ? formatPercent(shift, 1) : 'No material shift'}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="rounded-2xl border border-border/50 bg-muted/20 p-3">
                                                <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                                    <span>Current</span>
                                                    <span>Projected</span>
                                                </div>
                                                <div className="mt-3 space-y-2">
                                                    <div className="space-y-1">
                                                        <div className="h-2.5 overflow-hidden rounded-full bg-muted">
                                                            <div
                                                                className="h-full rounded-full bg-gradient-to-r from-rose-400 to-rose-600 transition-[width] duration-700 ease-out"
                                                                style={{ width: `${Math.max(currentRisk, 8)}%` }}
                                                            />
                                                        </div>
                                                    </div>
                                                    <div className="space-y-1">
                                                        <div className="h-2.5 overflow-hidden rounded-full bg-muted">
                                                            <div
                                                                className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-teal-500 transition-[width] duration-1000 ease-out"
                                                                style={{ width: `${Math.max(projectedRisk, 8)}%` }}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center justify-between gap-3 text-sm">
                                                <span className="text-muted-foreground">
                                                    Predicted outcome
                                                </span>
                                                <span
                                                    className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getRiskBadgeClass(
                                                        intervention.expected_new_risk_level
                                                    )}`}
                                                >
                                                    {formatRiskBadgeLabel(intervention.expected_new_risk_level)}
                                                </span>
                                            </div>
                                            <p className="text-xs font-medium text-muted-foreground">
                                                {intervention.rationale}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>

                <div className="rounded-[1.5rem] border border-border/60 bg-background p-5 shadow-sm">
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
                                Cohort field
                            </p>
                            <p className="mt-1 text-sm text-muted-foreground">
                                Where this student sits versus peers and adjacent case outcomes.
                            </p>
                        </div>
                        <Layers3 className="h-5 w-5 text-primary" />
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                        <div className="rounded-2xl border border-border/60 bg-muted/10 p-4">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                        Cohort position
                                    </p>
                                    <p className="mt-1 text-sm text-muted-foreground">
                                        Based on the same XAI analysis basis.
                                    </p>
                                </div>
                                <Users className="h-4 w-4 text-primary" />
                            </div>
                            <div className="mt-4 space-y-3">
                                <div className="flex items-end justify-between gap-3">
                                    <div>
                                        <p className="text-3xl font-semibold text-foreground">
                                            {cohort ? cohort.cohort_size : 0}
                                        </p>
                                        <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                                            Cohort size
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-3xl font-semibold text-foreground">
                                            {cohortRiskPercentile !== null
                                                ? `${cohortRiskPercentile.toFixed(0)}%`
                                                : '—'}
                                        </p>
                                        <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                                            Risk percentile
                                        </p>
                                    </div>
                                </div>
                                <div className="h-3 overflow-hidden rounded-full bg-muted/80">
                                    <div
                                        className="h-full rounded-full bg-gradient-to-r from-primary via-sky-500 to-indigo-500 transition-[width] duration-1000 ease-out"
                                        style={{ width: `${Math.max(Math.min(cohortRiskPercentile ?? 0, 100), 0)}%` }}
                                    />
                                </div>
                                <p className="text-xs font-medium text-muted-foreground">
                                    {cohort?.summary ?? 'Cohort comparison is not available for this analysis yet.'}
                                </p>
                            </div>
                        </div>

                        <div className="rounded-2xl border border-border/60 bg-muted/10 p-4">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                        Case outcome skyline
                                    </p>
                                    <p className="mt-1 text-sm text-muted-foreground">
                                        Distribution of nearby case trajectories.
                                    </p>
                                </div>
                                <TrendingDown className="h-4 w-4 text-primary" />
                            </div>
                            <div className="mt-5 grid grid-cols-3 gap-3">
                                {[
                                    {
                                        label: 'Improving',
                                        value: trajectoryCounts.improving,
                                        className: 'from-emerald-400 via-emerald-500 to-teal-500',
                                    },
                                    {
                                        label: 'Stable',
                                        value: trajectoryCounts.stable,
                                        className: 'from-sky-400 via-blue-500 to-indigo-500',
                                    },
                                    {
                                        label: 'Worsening',
                                        value: trajectoryCounts.worsening,
                                        className: 'from-rose-400 via-rose-500 to-red-600',
                                    },
                                ].map((item, index) => {
                                    const height = `${Math.max((item.value / maxTrajectoryCount) * 100, item.value ? 28 : 8)}%`;
                                    return (
                                        <div key={item.label} className="flex flex-col items-center gap-3">
                                            <div className="flex h-32 w-full items-end justify-center rounded-2xl bg-muted/70 p-3">
                                                <div
                                                    className={`w-full rounded-t-2xl bg-gradient-to-t ${item.className} shadow-[0_10px_25px_rgba(15,23,42,0.15)] transition-[height] duration-1000 ease-out`}
                                                    style={{
                                                        height,
                                                        animationDelay: `${index * 120}ms`,
                                                    }}
                                                />
                                            </div>
                                            <div className="text-center">
                                                <p className="text-lg font-semibold text-foreground">{item.value}</p>
                                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                                    {item.label}
                                                </p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                            <div className="mt-4 rounded-2xl border border-border/60 bg-background/90 p-3">
                                <div className="flex items-center justify-between gap-3">
                                    <p className="text-sm font-semibold text-foreground">
                                        Case explorer coverage
                                    </p>
                                    <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-semibold text-muted-foreground">
                                        {totalCases} cases
                                    </span>
                                </div>
                                <p className="mt-2 text-xs font-medium text-muted-foreground">
                                    {caseExplorer?.summary ??
                                        'Case-based outcome explorer will appear when comparable student cases are available.'}
                                </p>
                            </div>
                        </div>

                        <div className="rounded-2xl border border-border/60 bg-muted/10 p-4">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                                        Trust signal
                                    </p>
                                    <p className="mt-1 text-sm text-muted-foreground">
                                        Combined fairness and stability readout for this explanation.
                                    </p>
                                </div>
                                <ShieldCheck className="h-4 w-4 text-primary" />
                            </div>
                            <div className="mt-4 grid grid-cols-2 gap-3">
                                <div className="rounded-2xl bg-background/90 p-3">
                                    <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                                        Fairness
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {fairness ? fairness.parity_score.toFixed(1) : '—'}
                                    </p>
                                </div>
                                <div className="rounded-2xl bg-background/90 p-3">
                                    <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                                        Stability
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {stability ? stability.stability_score.toFixed(1) : '—'}
                                    </p>
                                </div>
                            </div>
                            <p className="mt-4 text-xs font-medium text-muted-foreground">
                                {fairness && stability
                                    ? `${getFairnessHeadline(fairness.parity_score)}. ${getStabilityHeadline(
                                          stability.stability_score
                                      )}.`
                                    : fairness?.summary ?? stability?.summary ?? 'Trust signals are not available yet.'}
                            </p>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

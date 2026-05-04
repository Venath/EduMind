import { useEffect, useState } from 'react';
import {
    BarChart3,
    GitBranch,
    Loader2,
    Microscope,
    Scale,
    Sparkles,
    Users,
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

import { xaiService, type StudentInsightsResponse } from '../../core/services/xaiService';
import { formatRiskBadgeLabel, getRiskBadgeClass } from '../prediction-form/statusStyles';
import { InsightCockpitSection } from './InsightCockpitSection';
import type { StudentInsightsSectionProps } from './types';

function formatPercent(value?: number | null, digits = 0): string {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    return `${value.toFixed(digits)}%`;
}

function formatScore(value?: number | null): string {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    return value.toFixed(1);
}

function getDirectionCopy(direction: string): string {
    if (direction === 'above' || direction === 'better') {
        if (direction === 'better') {
            return 'Lower risk than cohort';
        }
        return 'Above cohort';
    }
    if (direction === 'below' || direction === 'worse') {
        if (direction === 'worse') {
            return 'Higher risk than cohort';
        }
        return 'Below cohort';
    }
    return 'Aligned with cohort';
}

function getFairnessStatusClass(status?: string | null): string {
    const normalized = (status ?? '').trim().toLowerCase();

    if (normalized === 'action') {
        return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300';
    }

    if (normalized === 'watch') {
        return 'border-yellow-200 bg-yellow-50 text-yellow-700 dark:border-yellow-900 dark:bg-yellow-950/60 dark:text-yellow-300';
    }

    return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300';
}

function formatFairnessStatus(status?: string | null): string {
    const normalized = (status ?? '').trim().toLowerCase();
    if (normalized === 'action') return 'Action';
    if (normalized === 'watch') return 'Watch';
    return 'Balanced';
}

function getStabilityClass(sensitivity?: string | null): string {
    const normalized = (sensitivity ?? '').trim().toLowerCase();

    if (normalized === 'high' || normalized.includes('low')) {
        return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300';
    }

    if (normalized === 'medium' || normalized.includes('moderate')) {
        return 'border-yellow-200 bg-yellow-50 text-yellow-700 dark:border-yellow-900 dark:bg-yellow-950/60 dark:text-yellow-300';
    }

    return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300';
}

function getTrajectoryClass(trajectory?: string | null): string {
    const normalized = (trajectory ?? '').trim().toLowerCase();

    if (normalized === 'improving') {
        return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300';
    }

    if (normalized === 'worsening') {
        return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300';
    }

    if (normalized === 'stable') {
        return 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950/60 dark:text-blue-300';
    }

    return 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300';
}

function formatTrajectory(trajectory?: string | null): string {
    const normalized = (trajectory ?? '').trim().toLowerCase();
    if (normalized === 'improving') return 'Improving';
    if (normalized === 'worsening') return 'Worsening';
    if (normalized === 'stable') return 'Stable';
    return 'Limited history';
}

function LoadingGrid() {
    return (
        <div className="lg:col-span-12 grid gap-6 xl:grid-cols-2">
            {['similar', 'interventions', 'cohort', 'fairness', 'stability', 'cases'].map((key) => (
                <Card key={key} className="border shadow-sm">
                    <CardHeader className="border-b bg-muted/30">
                        <div className="h-5 w-40 animate-pulse rounded bg-muted" />
                        <div className="h-4 w-52 animate-pulse rounded bg-muted" />
                    </CardHeader>
                    <CardContent className="space-y-3 p-6">
                        <div className="h-16 animate-pulse rounded-xl bg-muted/60" />
                        <div className="h-16 animate-pulse rounded-xl bg-muted/60" />
                        <div className="h-16 animate-pulse rounded-xl bg-muted/60" />
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}

export function StudentInsightsSection({
    prediction,
    formData,
    source,
    instituteId,
}: StudentInsightsSectionProps) {
    const [insights, setInsights] = useState<StudentInsightsResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isCancelled = false;

        async function loadInsights() {
            setIsLoading(true);
            setError(null);

            try {
                const nextInsights = await xaiService.getStudentInsights({
                    source,
                    institute_id: source === 'connected' ? instituteId : undefined,
                    request_payload: formData,
                    prediction,
                });

                if (!isCancelled) {
                    setInsights(nextInsights);
                }
            } catch (nextError) {
                if (!isCancelled) {
                    const message =
                        nextError instanceof Error
                            ? nextError.message
                            : 'Could not load integrated XAI insights';
                    setError(message);
                    setInsights(null);
                }
            } finally {
                if (!isCancelled) {
                    setIsLoading(false);
                }
            }
        }

        void loadInsights();

        return () => {
            isCancelled = true;
        };
    }, [formData, instituteId, prediction, source]);

    if (isLoading) {
        return <LoadingGrid />;
    }

    if (error) {
        return (
            <div className="lg:col-span-12">
                <Card className="border-amber-200 bg-amber-50 shadow-sm dark:border-amber-900 dark:bg-amber-950/40">
                    <CardContent className="flex items-center gap-3 p-5 text-sm text-amber-800 dark:text-amber-200">
                        <Loader2 className="h-4 w-4 shrink-0" />
                        {error}
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (!insights) {
        return null;
    }

    const cohort = insights.cohort_comparison;
    const fairness = insights.fairness_evaluation;
    const stability = insights.explanation_stability;
    const caseExplorer = insights.case_outcome_explorer;
    const cohortLabel =
        source === 'connected' ? 'Connected student cohort' : 'Temporary student benchmark';

    return (
        <div className="lg:col-span-12 space-y-6">
            <InsightCockpitSection prediction={prediction} insights={insights} source={source} />

            <div className="grid gap-6 xl:grid-cols-2">
            <Card className="border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="flex items-center gap-2 text-lg">
                        <Users className="h-5 w-5 text-primary" />
                        Similar Student Cases
                    </CardTitle>
                    <CardDescription>
                        Closest peer profiles based on current risk drivers and performance patterns.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    {insights.similar_cases.length === 0 ? (
                        <p className="text-sm text-muted-foreground">
                            No comparable cases are available yet for this student.
                        </p>
                    ) : (
                        insights.similar_cases.map((student) => (
                            <div
                                key={student.student_id}
                                className="rounded-2xl border bg-background p-4 shadow-sm"
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div>
                                        <p className="text-base font-semibold text-foreground">
                                            {student.student_id}
                                        </p>
                                        <p className="text-xs text-muted-foreground">
                                            Similarity score {formatPercent(student.similarity_score * 100, 1)}
                                        </p>
                                    </div>
                                    <span
                                        className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getRiskBadgeClass(
                                            student.risk_level
                                        )}`}
                                    >
                                        {formatRiskBadgeLabel(student.risk_level)}
                                    </span>
                                </div>
                                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                    <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                        Grade {formatScore(student.avg_grade)}%
                                    </span>
                                    <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                        Completion {formatPercent(student.completion_rate, 1)}
                                    </span>
                                    {student.learning_style ? (
                                        <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                            {student.learning_style}
                                        </span>
                                    ) : null}
                                    {student.engagement_level ? (
                                        <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                            {student.engagement_level} engagement
                                        </span>
                                    ) : null}
                                </div>
                                <p className="mt-3 text-sm text-muted-foreground">{student.explanation}</p>
                            </div>
                        ))
                    )}
                </CardContent>
            </Card>

            <Card className="border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="flex items-center gap-2 text-lg">
                        <Sparkles className="h-5 w-5 text-primary" />
                        Intervention Ranking
                    </CardTitle>
                    <CardDescription>
                        Ranked support actions based on simulated impact against the current XAI profile.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    {insights.interventions.map((intervention) => (
                        <div
                            key={intervention.title}
                            className="rounded-2xl border bg-background p-4 shadow-sm"
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <p className="text-sm font-medium text-primary">#{intervention.rank}</p>
                                    <p className="text-base font-semibold text-foreground">
                                        {intervention.title}
                                    </p>
                                </div>
                                <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-semibold text-muted-foreground">
                                    {intervention.effort} effort
                                </span>
                            </div>
                            <div className="mt-3 grid gap-2 sm:grid-cols-2">
                                <div className="rounded-xl bg-emerald-50 p-3 dark:bg-emerald-950/30">
                                    <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
                                        Expected Risk Reduction
                                    </p>
                                    <p className="mt-1 text-lg font-semibold text-emerald-700 dark:text-emerald-200">
                                        {formatPercent(intervention.expected_risk_reduction * 100, 1)}
                                    </p>
                                </div>
                                <div className="rounded-xl bg-muted p-3">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Simulated Outcome
                                    </p>
                                    <div className="mt-2 flex items-center gap-2">
                                        <span
                                            className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getRiskBadgeClass(
                                                intervention.expected_new_risk_level
                                            )}`}
                                        >
                                            {formatRiskBadgeLabel(intervention.expected_new_risk_level)}
                                        </span>
                                        <span className="text-sm text-muted-foreground">
                                            Prediction certainty {formatPercent(intervention.confidence * 100, 1)}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <p className="mt-3 text-sm text-muted-foreground">{intervention.rationale}</p>
                            <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                {intervention.evidence.map((item) => (
                                    <span
                                        key={item}
                                        className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground"
                                    >
                                        {item}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </CardContent>
            </Card>

            <Card className="border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="flex items-center gap-2 text-lg">
                        <BarChart3 className="h-5 w-5 text-primary" />
                        Cohort Comparison
                    </CardTitle>
                    <CardDescription>{cohortLabel} built from the same XAI analysis basis.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    {!cohort ? (
                        <p className="text-sm text-muted-foreground">
                            Cohort comparison is not available for this analysis yet.
                        </p>
                    ) : (
                        <>
                            <div className="grid gap-3 sm:grid-cols-2">
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Cohort Size
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {cohort.cohort_size}
                                    </p>
                                </div>
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Risk Percentile
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {formatPercent(cohort.risk_percentile, 1)}
                                    </p>
                                </div>
                            </div>
                            <p className="text-sm text-muted-foreground">{cohort.summary}</p>
                            <div className="space-y-3">
                                {cohort.metrics.map((metric) => (
                                    <div
                                        key={metric.label}
                                        className="rounded-2xl border bg-background p-4 shadow-sm"
                                    >
                                        <div className="flex items-center justify-between gap-3">
                                            <p className="font-medium text-foreground">{metric.label}</p>
                                            <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                                {getDirectionCopy(metric.direction)}
                                            </span>
                                        </div>
                                        <div className="mt-2 flex items-center justify-between gap-4 text-sm">
                                            <span className="text-muted-foreground">
                                                Student {formatScore(metric.student_value)}
                                            </span>
                                            <span className="text-muted-foreground">
                                                Cohort {formatScore(metric.cohort_average)}
                                            </span>
                                            <span className="font-medium text-foreground">
                                                {formatPercent(metric.percentile, 1)}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>

            <Card className="border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="flex items-center gap-2 text-lg">
                        <Scale className="h-5 w-5 text-primary" />
                        Fairness And Bias Evaluation
                    </CardTitle>
                    <CardDescription>
                        Distributional parity check across integrated learning, engagement, and performance groups.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    {!fairness ? (
                        <p className="text-sm text-muted-foreground">
                            Fairness diagnostics are not available for this analysis yet.
                        </p>
                    ) : (
                        <>
                            <div className="grid gap-3 sm:grid-cols-3">
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Parity Score
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {fairness.parity_score.toFixed(1)}
                                    </p>
                                </div>
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Cohort Avg Risk
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {formatPercent(fairness.overall_average_risk_score * 100, 1)}
                                    </p>
                                </div>
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Elevated Risk Rate
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {formatPercent(fairness.overall_elevated_risk_rate, 1)}
                                    </p>
                                </div>
                            </div>
                            <p className="text-sm text-muted-foreground">{fairness.summary}</p>
                            {fairness.alerts.length > 0 ? (
                                <div className="space-y-2">
                                    {fairness.alerts.map((alert) => (
                                        <div
                                            key={`${alert.title}-${alert.detail}`}
                                            className={`rounded-2xl border p-4 text-sm ${getFairnessStatusClass(
                                                alert.severity === 'high' ? 'action' : 'watch'
                                            )}`}
                                        >
                                            <p className="font-semibold">{alert.title}</p>
                                            <p className="mt-1">{alert.detail}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : null}
                            <div className="space-y-3">
                                {fairness.dimensions.map((dimension) => (
                                    <div
                                        key={`${dimension.dimension}-${dimension.current_group}`}
                                        className="rounded-2xl border bg-background p-4 shadow-sm"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="font-medium text-foreground">
                                                    {dimension.dimension}
                                                </p>
                                                <p className="text-sm text-muted-foreground">
                                                    {dimension.current_group}
                                                </p>
                                            </div>
                                            <span
                                                className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getFairnessStatusClass(
                                                    dimension.status
                                                )}`}
                                            >
                                                {formatFairnessStatus(dimension.status)}
                                            </span>
                                        </div>
                                        <div className="mt-3 grid gap-2 sm:grid-cols-3 text-sm">
                                            <div>
                                                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                                                    Group Avg Risk
                                                </p>
                                                <p className="mt-1 font-medium text-foreground">
                                                    {formatPercent(dimension.average_risk_score * 100, 1)}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                                                    Disparity
                                                </p>
                                                <p className="mt-1 font-medium text-foreground">
                                                    {formatPercent(dimension.disparity_score * 100, 1)}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                                                    Elevated Risk Rate
                                                </p>
                                                <p className="mt-1 font-medium text-foreground">
                                                    {formatPercent(dimension.elevated_risk_rate, 1)}
                                                </p>
                                            </div>
                                        </div>
                                        <p className="mt-3 text-sm text-muted-foreground">
                                            {dimension.note}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>

            <Card className="border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="flex items-center gap-2 text-lg">
                        <Microscope className="h-5 w-5 text-primary" />
                        Explanation Stability Score
                    </CardTitle>
                    <CardDescription>
                        Robustness check under small local changes to the current student inputs.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    {!stability ? (
                        <p className="text-sm text-muted-foreground">
                            Stability diagnostics are not available for this analysis yet.
                        </p>
                    ) : (
                        <>
                            <div className="grid gap-3 sm:grid-cols-3">
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Stability Score
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {stability.stability_score.toFixed(1)}
                                    </p>
                                </div>
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Consistency Rate
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {formatPercent(stability.consistency_rate, 1)}
                                    </p>
                                </div>
                                <div className="rounded-2xl bg-muted p-4">
                                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                        Avg Risk Shift
                                    </p>
                                    <p className="mt-1 text-2xl font-semibold text-foreground">
                                        {formatPercent(stability.average_risk_shift, 1)}
                                    </p>
                                </div>
                            </div>
                            <span
                                className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${getStabilityClass(
                                    stability.confidence_band
                                )}`}
                            >
                                {stability.confidence_band}
                            </span>
                            <p className="text-sm text-muted-foreground">{stability.summary}</p>
                            <div className="space-y-3">
                                {stability.sensitive_features.map((signal) => (
                                    <div
                                        key={signal.feature}
                                        className="rounded-2xl border bg-background p-4 shadow-sm"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="font-medium text-foreground">{signal.feature}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    Tested range {signal.tested_range}
                                                </p>
                                            </div>
                                            <span
                                                className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getStabilityClass(
                                                    signal.sensitivity
                                                )}`}
                                            >
                                                {signal.sensitivity}
                                            </span>
                                        </div>
                                        <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                            <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                                Max shift {formatPercent(signal.max_risk_shift, 1)}
                                            </span>
                                            <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                                Outcome changed {signal.outcome_changed ? 'Yes' : 'No'}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>

            <Card className="border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="flex items-center gap-2 text-lg">
                        <GitBranch className="h-5 w-5 text-primary" />
                        Case-Based Outcome Explorer
                    </CardTitle>
                    <CardDescription>
                        Outcome trajectories and takeaways from the strongest comparable cases.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    {!caseExplorer ? (
                        <p className="text-sm text-muted-foreground">
                            Comparable case outcomes are not available for this analysis yet.
                        </p>
                    ) : (
                        <>
                            <p className="text-sm text-muted-foreground">{caseExplorer.summary}</p>
                            <div className="space-y-4">
                                {caseExplorer.cases.map((caseItem) => (
                                    <div
                                        key={caseItem.student_id}
                                        className="rounded-2xl border bg-background p-4 shadow-sm"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="font-medium text-foreground">
                                                    {caseItem.student_id}
                                                </p>
                                                <p className="text-sm text-muted-foreground">
                                                    Similarity {formatPercent(caseItem.similarity_score, 1)}
                                                </p>
                                            </div>
                                            <span
                                                className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getTrajectoryClass(
                                                    caseItem.trajectory
                                                )}`}
                                            >
                                                {formatTrajectory(caseItem.trajectory)}
                                            </span>
                                        </div>
                                        <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                            <span
                                                className={`rounded-full border px-2.5 py-1 font-semibold ${getRiskBadgeClass(
                                                    caseItem.latest_risk_level
                                                )}`}
                                            >
                                                {formatRiskBadgeLabel(caseItem.latest_risk_level)}
                                            </span>
                                            <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                                Risk {formatPercent(caseItem.latest_risk_score * 100, 1)}
                                            </span>
                                            {caseItem.learning_style ? (
                                                <span className="rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                                                    {caseItem.learning_style}
                                                </span>
                                            ) : null}
                                        </div>
                                        <p className="mt-3 text-sm font-medium text-foreground">
                                            {caseItem.observed_outcome}
                                        </p>
                                        <p className="mt-2 text-sm text-muted-foreground">
                                            {caseItem.key_takeaway}
                                        </p>
                                        {caseItem.recommended_action ? (
                                            <div className="mt-3 rounded-xl bg-muted p-3 text-sm text-muted-foreground">
                                                Recommended action: {caseItem.recommended_action}
                                            </div>
                                        ) : null}
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
            </div>
        </div>
    );
}

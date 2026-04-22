import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Minus, TrendingDown, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import {
    xaiService,
    type RiskPredictionResponse,
    type RiskTimelineResponse,
    type StudentRiskRequest,
} from '../../core/services/xaiService';
import type { RiskTimelineSectionProps } from './types';

const TREND_META = {
    improving: {
        label: 'Improving',
        className: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300',
        icon: TrendingDown,
    },
    worsening: {
        label: 'Worsening',
        className: 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300',
        icon: TrendingUp,
    },
    stable: {
        label: 'Stable',
        className: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300',
        icon: Minus,
    },
    insufficient_data: {
        label: 'Single Analysis',
        className: 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-950/40 dark:text-slate-300',
        icon: Activity,
    },
} as const;

function getRiskLevelClass(riskLevel: string) {
    const normalized = riskLevel.toLowerCase();
    if (normalized.includes('safe')) {
        return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300';
    }
    if (normalized.includes('medium')) {
        return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300';
    }
    return 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300';
}

function formatTimestamp(value: string) {
    return new Date(value).toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
    });
}

function formatShortDate(value: string) {
    return new Date(value).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
    });
}

function getPointFillClass(riskLevel: string) {
    const normalized = riskLevel.toLowerCase();
    if (normalized.includes('safe')) {
        return 'fill-emerald-500';
    }
    if (normalized.includes('medium')) {
        return 'fill-amber-500';
    }
    return 'fill-rose-500';
}

function getDeltaSummary(
    currentPoint: RiskTimelineResponse['points'][number],
    previousPoint?: RiskTimelineResponse['points'][number]
) {
    if (!previousPoint) {
        return 'This is the earliest saved point for this student.';
    }

    const riskDelta = (currentPoint.risk_score - previousPoint.risk_score) * 100;
    const gradeDelta =
        currentPoint.avg_grade !== null &&
        currentPoint.avg_grade !== undefined &&
        previousPoint.avg_grade !== null &&
        previousPoint.avg_grade !== undefined
            ? currentPoint.avg_grade - previousPoint.avg_grade
            : null;
    const completionDelta =
        currentPoint.completion_rate !== null &&
        currentPoint.completion_rate !== undefined &&
        previousPoint.completion_rate !== null &&
        previousPoint.completion_rate !== undefined
            ? currentPoint.completion_rate - previousPoint.completion_rate
            : null;

    const riskDirection =
        Math.abs(riskDelta) < 0.1 ? 'unchanged' : riskDelta > 0 ? 'up' : 'down';

    return {
        riskDelta,
        gradeDelta,
        completionDelta,
        riskDirection,
    };
}

function buildPolyline(points: RiskTimelineResponse['points']) {
    if (points.length === 1) {
        return '12,60';
    }

    const step = 76 / (points.length - 1);
    return points
        .map((point, index) => {
            const x = 12 + step * index;
            const y = 60 - point.risk_score * 48;
            return `${x},${y}`;
        })
        .join(' ');
}

function buildAreaPolygon(points: RiskTimelineResponse['points']) {
    if (points.length === 1) {
        return '12,60 12,60 12,60';
    }

    const coordinates = points.map((point, index) => {
        const { x, y } = getPointCoordinates(points, index);
        return `${x},${y}`;
    });
    const firstX = getPointCoordinates(points, 0).x;
    const lastX = getPointCoordinates(points, points.length - 1).x;
    return `${firstX},60 ${coordinates.join(' ')} ${lastX},60`;
}

function getPointCoordinates(
    points: RiskTimelineResponse['points'],
    index: number
) {
    if (points.length === 1) {
        return { x: 12, y: 60 };
    }

    const step = 76 / (points.length - 1);
    return {
        x: 12 + step * index,
        y: 60 - points[index].risk_score * 48,
    };
}

function buildFallbackTimeline(
    prediction: RiskPredictionResponse,
    formData: StudentRiskRequest
): RiskTimelineResponse {
    return {
        student_id: prediction.student_id,
        total_points: 1,
        trend_direction: 'insufficient_data',
        timeline_basis: 'current_analysis',
        latest_risk_level: prediction.risk_level,
        latest_risk_score: prediction.risk_score,
        points: [
            {
                timestamp: prediction.timestamp,
                risk_level: prediction.risk_level,
                risk_score: prediction.risk_score,
                confidence:
                    prediction.confidence <= 1 ? prediction.confidence : prediction.confidence / 100,
                avg_grade: formData.avg_grade,
                completion_rate: formData.assessment_completion_rate * 100,
                key_driver:
                    'Showing the current analysis only. Run another analysis for this student later to build a saved trend.',
            },
        ],
    };
}

export function RiskTimelineSection({
    studentId,
    predictionId,
    source,
    prediction,
    formData,
}: RiskTimelineSectionProps) {
    const [timeline, setTimeline] = useState<RiskTimelineResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isFallbackTimeline, setIsFallbackTimeline] = useState(false);
    const [activePointIndex, setActivePointIndex] = useState<number>(0);
    const [isChartAnimated, setIsChartAnimated] = useState(false);

    useEffect(() => {
        let isCancelled = false;

        const loadTimeline = async () => {
            setIsLoading(true);
            setError(null);
            setIsFallbackTimeline(false);

            try {
                const response = await xaiService.getRiskTimeline(studentId, {
                    limit: 8,
                    source,
                });
                if (!isCancelled) {
                    setTimeline(response);
                    setIsFallbackTimeline(false);
                }
            } catch (loadError) {
                if (!isCancelled) {
                    const fallbackTimeline = buildFallbackTimeline(prediction, formData);
                    setTimeline(fallbackTimeline);
                    setIsFallbackTimeline(true);
                    setError(
                        loadError instanceof Error
                            ? loadError.message
                            : 'Could not load student timeline'
                    );
                }
            } finally {
                if (!isCancelled) {
                    setIsLoading(false);
                }
            }
        };

        if (studentId) {
            void loadTimeline();
        }

        return () => {
            isCancelled = true;
        };
    }, [formData, prediction, predictionId, source, studentId]);

    useEffect(() => {
        if (!timeline?.points.length) {
            return;
        }
        setActivePointIndex(timeline.points.length - 1);
    }, [timeline]);

    useEffect(() => {
        if (!timeline?.points.length) {
            return;
        }

        setIsChartAnimated(false);
        const frameId = window.requestAnimationFrame(() => {
            setIsChartAnimated(true);
        });

        return () => {
            window.cancelAnimationFrame(frameId);
        };
    }, [timeline]);

    if (isLoading) {
        return (
            <Card className="lg:col-span-12 border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="text-lg font-semibold">Risk Trend Timeline</CardTitle>
                    <CardDescription>Loading saved XAI history for this student.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 p-6">
                    <div className="h-40 animate-pulse rounded-xl bg-muted/40" />
                    <div className="grid gap-3 md:grid-cols-3">
                        <div className="h-24 animate-pulse rounded-xl bg-muted/40" />
                        <div className="h-24 animate-pulse rounded-xl bg-muted/40" />
                        <div className="h-24 animate-pulse rounded-xl bg-muted/40" />
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!timeline) {
        return (
            <Card className="lg:col-span-12 border shadow-sm">
                <CardHeader className="border-b bg-muted/30">
                    <CardTitle className="text-lg font-semibold">Risk Trend Timeline</CardTitle>
                    <CardDescription>Saved XAI history for this student could not be loaded.</CardDescription>
                </CardHeader>
                <CardContent className="p-6 text-sm text-muted-foreground">
                    {error || 'No saved timeline is available yet.'}
                </CardContent>
            </Card>
        );
    }

    const trendMeta =
        TREND_META[timeline.trend_direction as keyof typeof TREND_META] ||
        TREND_META.insufficient_data;
    const TrendIcon = trendMeta.icon;
    const timelineBasis = timeline.timeline_basis ?? (isFallbackTimeline ? 'current_analysis' : 'saved_history');
    const timelineDescription =
        timelineBasis === 'derived_history'
            ? 'Historical XAI snapshots derived from the student’s engagement records.'
            : timelineBasis === 'temporary_history'
                ? 'Saved history from the temporary-student analysis flow.'
                : timelineBasis === 'temporary_snapshot'
                    ? 'Only the latest temporary-student snapshot is available so far.'
                    : timelineBasis === 'current_analysis'
                        ? 'Showing the current analysis because no historical timeline is available yet.'
                        : 'Saved history from repeated XAI analyses for this student.';
    const timelineLabel =
        timelineBasis === 'derived_history'
            ? 'Engagement-Derived History'
            : timelineBasis === 'temporary_history'
                ? 'Temporary Student History'
                : timelineBasis === 'temporary_snapshot'
                    ? 'Latest Temporary Snapshot'
                    : timelineBasis === 'current_analysis'
                        ? 'Current Analysis'
                        : 'Saved XAI History';
    const safePointIndex = Math.min(
        Math.max(activePointIndex, 0),
        Math.max(timeline.points.length - 1, 0)
    );
    const activePoint = timeline.points[safePointIndex];
    const previousPoint = safePointIndex > 0 ? timeline.points[safePointIndex - 1] : undefined;
    const activeCoordinates = getPointCoordinates(timeline.points, safePointIndex);
    const deltaSummary = activePoint ? getDeltaSummary(activePoint, previousPoint) : null;
    const activeTooltipLeft = activePoint
        ? Math.min(Math.max(activeCoordinates.x, 20), 80)
        : 50;
    const activeTooltipTop = activePoint ? (activeCoordinates.y / 70) * 100 : 50;

    return (
        <Card className="lg:col-span-12 border shadow-sm">
            <CardHeader className="border-b bg-muted/30">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                            <Activity className="h-5 w-5 text-primary" />
                            Risk Trend Timeline
                        </CardTitle>
                        <CardDescription>{timelineDescription}</CardDescription>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <span className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
                            {timelineLabel}
                        </span>
                        <span
                            className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold ${trendMeta.className}`}
                        >
                            <TrendIcon className="h-3.5 w-3.5" />
                            {trendMeta.label}
                        </span>
                        <span className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
                            {timeline.total_points} Saved Analyses
                        </span>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-6 p-6">
                <div className="rounded-2xl border border-border/60 bg-muted/20 p-4">
                    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                Latest Stored Outcome
                            </p>
                            <div className="mt-2 flex flex-wrap items-center gap-3">
                                {timeline.latest_risk_level && (
                                    <span
                                        className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${getRiskLevelClass(timeline.latest_risk_level)}`}
                                    >
                                        {timeline.latest_risk_level}
                                    </span>
                                )}
                                {timeline.latest_risk_score !== null &&
                                    timeline.latest_risk_score !== undefined && (
                                        <span className="text-sm font-medium text-foreground">
                                            {(timeline.latest_risk_score * 100).toFixed(1)}% risk score
                                        </span>
                                    )}
                            </div>
                        </div>
                        {timeline.total_points < 2 && (
                            <p className="text-sm text-muted-foreground">
                                {isFallbackTimeline
                                    ? 'This student has no saved timeline yet. Future analyses will build the trend automatically.'
                                    : 'Save more analyses over time to expose a stronger risk pattern.'}
                            </p>
                        )}
                    </div>

                    {activePoint && (
                        <div
                            key={`${activePoint.timestamp}-${safePointIndex}`}
                            className="mb-4 grid animate-in gap-3 rounded-2xl border border-border/60 bg-background p-4 shadow-sm fade-in-0 slide-in-from-bottom-2 duration-300 md:grid-cols-[1.3fr_1fr_1fr_1fr]"
                        >
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                    Selected Analysis
                                </p>
                                <p className="mt-1 text-sm font-semibold text-foreground">
                                    {formatTimestamp(activePoint.timestamp)}
                                </p>
                                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                                    Hover or click another point to inspect that saved snapshot.
                                </p>
                            </div>
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                    Risk Score
                                </p>
                                <p className="mt-1 text-lg font-semibold text-foreground">
                                    {(activePoint.risk_score * 100).toFixed(1)}%
                                </p>
                                {deltaSummary && typeof deltaSummary === 'object' ? (
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        {deltaSummary.riskDirection === 'unchanged'
                                            ? 'No material change from previous point'
                                            : `Risk moved ${deltaSummary.riskDirection} by ${Math.abs(deltaSummary.riskDelta).toFixed(1)} pts`}
                                    </p>
                                ) : null}
                            </div>
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                    Average Grade
                                </p>
                                <p className="mt-1 text-lg font-semibold text-foreground">
                                    {activePoint.avg_grade !== null && activePoint.avg_grade !== undefined
                                        ? `${activePoint.avg_grade.toFixed(1)}%`
                                        : '—'}
                                </p>
                                {deltaSummary &&
                                typeof deltaSummary === 'object' &&
                                deltaSummary.gradeDelta !== null ? (
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        {deltaSummary.gradeDelta >= 0 ? '+' : ''}
                                        {deltaSummary.gradeDelta.toFixed(1)} pts from previous
                                    </p>
                                ) : null}
                            </div>
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                    Completion Rate
                                </p>
                                <p className="mt-1 text-lg font-semibold text-foreground">
                                    {activePoint.completion_rate !== null &&
                                    activePoint.completion_rate !== undefined
                                        ? `${activePoint.completion_rate.toFixed(0)}%`
                                        : '—'}
                                </p>
                                {deltaSummary &&
                                typeof deltaSummary === 'object' &&
                                deltaSummary.completionDelta !== null ? (
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        {deltaSummary.completionDelta >= 0 ? '+' : ''}
                                        {deltaSummary.completionDelta.toFixed(0)} pts from previous
                                    </p>
                                ) : null}
                            </div>
                            {activePoint.key_driver ? (
                                <div className="md:col-span-4 rounded-xl bg-muted/40 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
                                    {activePoint.key_driver}
                                </div>
                            ) : null}
                        </div>
                    )}

                    <div className="relative overflow-visible rounded-xl bg-background p-3">
                        {activePoint ? (
                            <div
                                className="pointer-events-none absolute z-10 hidden min-w-[10rem] max-w-[12rem] rounded-2xl border border-border/70 bg-background/95 px-3 py-2 shadow-lg backdrop-blur md:block"
                                style={{
                                    left: `clamp(5rem, ${activeTooltipLeft}%, calc(100% - 5rem))`,
                                    top: `${activeTooltipTop}%`,
                                    transform:
                                        'translate(-50%, calc(-100% - 0.75rem)) translateZ(0)',
                                    opacity: isChartAnimated ? 1 : 0,
                                    transition: 'left 320ms ease-out, top 320ms ease-out, opacity 240ms ease-out',
                                }}
                            >
                                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                                    Active point
                                </p>
                                <div className="mt-1 flex items-center justify-between gap-3">
                                    <span
                                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold ${getRiskLevelClass(activePoint.risk_level)}`}
                                    >
                                        {activePoint.risk_level}
                                    </span>
                                    <span className="text-xs font-semibold text-foreground">
                                        {(activePoint.risk_score * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <p className="mt-1 text-xs text-muted-foreground">
                                    {formatTimestamp(activePoint.timestamp)}
                                </p>
                            </div>
                        ) : null}

                        <svg
                            viewBox="0 0 100 70"
                            className="h-44 w-full overflow-visible"
                            role="img"
                            aria-label={`Risk trend over ${timeline.total_points} saved analyses`}
                        >
                            <defs>
                                <linearGradient id="riskTimelineFill" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stopColor="currentColor" stopOpacity="0.22" />
                                    <stop offset="100%" stopColor="currentColor" stopOpacity="0.02" />
                                </linearGradient>
                            </defs>
                            {[12, 24, 36, 48, 60].map((gridY, index) => (
                                <line
                                    key={gridY}
                                    x1="10"
                                    y1={gridY}
                                    x2="88"
                                    y2={gridY}
                                    stroke="currentColor"
                                    strokeDasharray={gridY === 60 ? '0' : '2 3'}
                                    className="text-border/80"
                                    style={{
                                        opacity: isChartAnimated ? 1 : 0,
                                        transition: 'opacity 320ms ease-out',
                                        transitionDelay: `${index * 70}ms`,
                                    }}
                                />
                            ))}
                            <line x1="10" y1="12" x2="10" y2="60" stroke="currentColor" className="text-border" />
                            <line x1="10" y1="60" x2="88" y2="60" stroke="currentColor" className="text-border" />
                            <polygon
                                points={buildAreaPolygon(timeline.points)}
                                fill="url(#riskTimelineFill)"
                                className="text-primary"
                                style={{
                                    opacity: isChartAnimated ? 1 : 0,
                                    transformOrigin: '50% 100%',
                                    transform: isChartAnimated ? 'scaleY(1)' : 'scaleY(0.82)',
                                    transition:
                                        'opacity 500ms ease-out, transform 700ms cubic-bezier(0.22, 1, 0.36, 1)',
                                }}
                            />
                            {activePoint && (
                                <line
                                    x1={activeCoordinates.x}
                                    y1="12"
                                    x2={activeCoordinates.x}
                                    y2="60"
                                    stroke="currentColor"
                                    strokeDasharray="2 2"
                                    className="text-muted-foreground/50"
                                    style={{ transition: 'x1 320ms ease-out, x2 320ms ease-out, opacity 240ms ease-out' }}
                                />
                            )}
                            <polyline
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2.5"
                                className="text-primary drop-shadow-[0_0_12px_rgba(59,130,246,0.22)]"
                                points={buildPolyline(timeline.points)}
                                pathLength={100}
                                strokeDasharray="100"
                                strokeDashoffset={isChartAnimated ? 0 : 100}
                                style={{ transition: 'stroke-dashoffset 900ms cubic-bezier(0.22, 1, 0.36, 1)' }}
                            />
                            {timeline.points.map((point, index) => {
                                const { x, y } = getPointCoordinates(timeline.points, index);
                                const isActive = index === safePointIndex;
                                return (
                                    <g key={`${point.timestamp}-${index}`}>
                                        {isActive ? (
                                            <>
                                                <circle
                                                    cx={x}
                                                    cy={y}
                                                    r="7.8"
                                                    className={`${getPointFillClass(point.risk_level)} animate-pulse opacity-10`}
                                                    style={{
                                                        transformOrigin: `${x}px ${y}px`,
                                                        animationDuration: '1.8s',
                                                    }}
                                                />
                                                <circle
                                                    cx={x}
                                                    cy={y}
                                                    r="10.2"
                                                    className="fill-transparent animate-spin"
                                                    stroke="currentColor"
                                                    strokeWidth="0.5"
                                                    strokeDasharray="1.6 2.4"
                                                    strokeOpacity="0.28"
                                                    style={{
                                                        animationDuration: '6s',
                                                        transformOrigin: `${x}px ${y}px`,
                                                    }}
                                                />
                                            </>
                                        ) : null}
                                        <circle
                                            cx={x}
                                            cy={y}
                                            r="7"
                                            className="fill-transparent cursor-pointer"
                                            onMouseEnter={() => setActivePointIndex(index)}
                                            onFocus={() => setActivePointIndex(index)}
                                            onClick={() => setActivePointIndex(index)}
                                            tabIndex={0}
                                            role="button"
                                            aria-label={`View saved analysis ${index + 1} for ${formatTimestamp(point.timestamp)}`}
                                        />
                                        <circle
                                            cx={x}
                                            cy={y}
                                            r={isActive ? '4.8' : '3.2'}
                                            className={`${getPointFillClass(point.risk_level)} transition-all duration-300`}
                                            stroke="currentColor"
                                            strokeWidth={isActive ? '1.5' : '0'}
                                            strokeOpacity={isActive ? '0.55' : '0'}
                                            style={{
                                                opacity: isChartAnimated ? 1 : 0,
                                                transformOrigin: `${x}px ${y}px`,
                                                transform: isChartAnimated ? 'scale(1)' : 'scale(0.7)',
                                                transition:
                                                    'opacity 300ms ease-out, transform 300ms ease-out, stroke-opacity 300ms ease-out',
                                                transitionDelay: `${index * 60}ms`,
                                            }}
                                        />
                                    </g>
                                );
                            })}
                        </svg>
                        <div
                            className="mt-3 grid gap-1"
                            style={{
                                gridTemplateColumns: `repeat(${Math.max(timeline.points.length, 1)}, minmax(0, 1fr))`,
                            }}
                        >
                            {timeline.points.map((point, index) => {
                                const isActive = index === safePointIndex;
                                return (
                                    <button
                                        key={`date-${point.timestamp}-${index}`}
                                        type="button"
                                        onMouseEnter={() => setActivePointIndex(index)}
                                        onFocus={() => setActivePointIndex(index)}
                                        onClick={() => setActivePointIndex(index)}
                                        className={`min-w-0 rounded-lg px-1 py-1 text-center text-[10px] font-medium leading-tight transition-colors sm:text-[11px] ${
                                            isActive
                                                ? 'bg-primary/10 text-primary'
                                                : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                                        } ${timeline.points.length > 6 && index % 2 === 1 ? 'translate-y-2' : ''}`}
                                        aria-label={`Select timeline date ${formatShortDate(point.timestamp)}`}
                                    >
                                        {formatShortDate(point.timestamp)}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>

                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                    {timeline.points.map((point, index) => (
                        <div
                            key={`${point.timestamp}-${index}`}
                            className={`animate-in cursor-pointer rounded-2xl border border-border/60 bg-background p-4 shadow-sm fade-in-0 zoom-in-95 transition-all duration-300 ${
                                index === safePointIndex
                                    ? 'ring-2 ring-primary/30 -translate-y-1'
                                    : 'hover:-translate-y-0.5 hover:border-primary/30'
                            }`}
                            onMouseEnter={() => setActivePointIndex(index)}
                            onClick={() => setActivePointIndex(index)}
                            style={{
                                transitionDelay: `${index * 40}ms`,
                                animationDelay: `${index * 70}ms`,
                            }}
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                        Analysis {index + 1}
                                    </p>
                                    <p className="mt-1 text-sm font-medium text-foreground">
                                        {formatTimestamp(point.timestamp)}
                                    </p>
                                </div>
                                <span
                                    className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${getRiskLevelClass(point.risk_level)}`}
                                >
                                    {point.risk_level}
                                </span>
                            </div>

                            <div className="mt-4 space-y-2 text-sm">
                                <div className="flex items-center justify-between text-muted-foreground">
                                    <span>Risk score</span>
                                    <span className="font-semibold text-foreground">
                                        {(point.risk_score * 100).toFixed(1)}%
                                    </span>
                                </div>
                                {point.avg_grade !== null && point.avg_grade !== undefined && (
                                    <div className="flex items-center justify-between text-muted-foreground">
                                        <span>Average grade</span>
                                        <span className="font-semibold text-foreground">
                                            {point.avg_grade.toFixed(1)}%
                                        </span>
                                    </div>
                                )}
                                {point.completion_rate !== null &&
                                    point.completion_rate !== undefined && (
                                        <div className="flex items-center justify-between text-muted-foreground">
                                            <span>Completion</span>
                                            <span className="font-semibold text-foreground">
                                                {point.completion_rate.toFixed(0)}%
                                            </span>
                                        </div>
                                    )}
                            </div>

                            {point.key_driver && (
                                <p className="mt-4 rounded-xl bg-muted/40 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
                                    {point.key_driver}
                                </p>
                            )}
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

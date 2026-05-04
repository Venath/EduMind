import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Sparkles, Target } from 'lucide-react';
import type { CounterfactualSectionProps } from './types';

const FEATURE_LABELS: Record<string, string> = {
    avg_grade: 'Average Grade',
    grade_consistency: 'Grade Consistency',
    grade_range: 'Grade Range',
    num_assessments: 'Assessments Completed',
    assessment_completion_rate: 'Completion Rate',
    low_engagement: 'Low Engagement Flag',
};

function formatFeatureLabel(feature: string): string {
    return FEATURE_LABELS[feature] ?? feature.replace(/_/g, ' ');
}

function formatFeatureValue(feature: string, value: string | number | boolean): string {
    if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
    }

    if (typeof value === 'number') {
        if (feature === 'assessment_completion_rate') {
            return `${(value * 100).toFixed(0)}%`;
        }
        if (feature === 'avg_grade' || feature === 'grade_consistency') {
            return `${value.toFixed(0)}%`;
        }
        if (feature === 'grade_range') {
            return `${value.toFixed(0)} pts`;
        }
        return `${value}`;
    }

    return value;
}

function getOutcomeBadgeClass(outcome: string): string {
    const normalized = outcome.toLowerCase();
    if (normalized.includes('safe')) {
        return 'border-green-200 bg-green-100 text-green-800 dark:border-green-900/60 dark:bg-green-950/50 dark:text-green-300';
    }
    if (normalized.includes('medium')) {
        return 'border-yellow-200 bg-yellow-100 text-yellow-800 dark:border-yellow-900/60 dark:bg-yellow-950/50 dark:text-yellow-300';
    }
    return 'border-red-200 bg-red-100 text-red-800 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-300';
}

export function CounterfactualSection({ counterfactual }: CounterfactualSectionProps) {
    if (!counterfactual) {
        return null;
    }

    const hasChanges = counterfactual.changes.length > 0;

    return (
        <Card className="lg:col-span-12 shadow-sm hover:shadow-md transition-shadow duration-200 border">
            <CardHeader className="pb-4 border-b bg-muted/30">
                <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                    <Sparkles className="h-5 w-5 text-primary" />
                    Counterfactual Path
                </CardTitle>
                <CardDescription>{counterfactual.summary}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 p-6">
                <div className="grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl border bg-background p-4">
                        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                            Current Outcome
                        </div>
                        <Badge
                            variant="outline"
                            className={`mt-3 ${getOutcomeBadgeClass(counterfactual.current_outcome)}`}
                        >
                            {counterfactual.current_outcome}
                        </Badge>
                    </div>
                    <div className="rounded-2xl border bg-background p-4">
                        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                            Target Outcome
                        </div>
                        <Badge
                            variant="outline"
                            className={`mt-3 ${getOutcomeBadgeClass(counterfactual.target_outcome)}`}
                        >
                            {counterfactual.target_outcome}
                        </Badge>
                    </div>
                    <div className="rounded-2xl border bg-background p-4">
                        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                            Estimated Result
                        </div>
                        <div className="mt-3 flex items-center gap-3">
                            <Target className="h-4 w-4 text-primary" />
                            <div>
                                <div className="font-semibold text-foreground">
                                    {counterfactual.estimated_risk_level ?? 'No change found'}
                                </div>
                                {typeof counterfactual.estimated_risk_score === 'number' && (
                                    <div className="text-sm text-muted-foreground">
                                        Risk score {(counterfactual.estimated_risk_score * 100).toFixed(1)}%
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {hasChanges ? (
                    <div className="grid gap-3">
                        {counterfactual.changes.map((change) => (
                            <div
                                key={change.feature}
                                className="rounded-2xl border bg-background p-4"
                            >
                                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                                    <div>
                                        <div className="text-sm font-semibold text-foreground">
                                            {formatFeatureLabel(change.feature)}
                                        </div>
                                        <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                                            <span>{formatFeatureValue(change.feature, change.current_value)}</span>
                                            <ArrowRight className="h-4 w-4" />
                                            <span className="font-medium text-foreground">
                                                {formatFeatureValue(change.feature, change.suggested_value)}
                                            </span>
                                        </div>
                                    </div>
                                    <Badge variant="secondary" className="w-fit">
                                        {change.direction}
                                    </Badge>
                                </div>
                                <p className="mt-3 text-sm text-muted-foreground">
                                    {change.rationale}
                                </p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="rounded-2xl border border-dashed bg-muted/20 p-5 text-sm text-muted-foreground">
                        No further feature changes are needed. This student is already in the safest band.
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

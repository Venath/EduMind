import { useMemo, useState } from 'react';
import { Progress } from '@/components/ui/progress';
import type { ProbabilitiesSectionProps } from './types';

export function ProbabilitiesSection({
    probabilities,
    riskLevel,
}: ProbabilitiesSectionProps) {
    const [showBreakdown, setShowBreakdown] = useState(false);

    const getBarColor = (key: string): string => {
        const keyLower = key.toLowerCase();
        if (keyLower.includes('safe')) return '!bg-green-600';
        if (keyLower.includes('medium')) return '!bg-yellow-500';
        return '!bg-red-600';
    };

    const entries = useMemo(
        () => Object.entries(probabilities),
        [probabilities]
    );

    const winningEntry = useMemo(() => {
        const normalizedRiskLevel = riskLevel.trim().toLowerCase();
        const matchedEntry = entries.find(([key]) => key.trim().toLowerCase() === normalizedRiskLevel);
        if (matchedEntry) {
            return matchedEntry;
        }

        return entries.reduce<[string, number] | null>((winner, entry) => {
            if (!winner || entry[1] > winner[1]) {
                return entry;
            }
            return winner;
        }, null);
    }, [entries, riskLevel]);

    if (!winningEntry) {
        return null;
    }

    const [winningLabel, winningValue] = winningEntry;

    return (
        <div className="py-2 space-y-5">
            <div className="rounded-2xl border border-border bg-muted/20 p-4">
                <div className="flex items-center justify-between gap-3 text-sm">
                    <div>
                        <div className="font-medium text-muted-foreground">Predicted Outcome</div>
                        <div className="mt-1 text-xl font-semibold text-foreground">
                            {winningLabel.replace(/_/g, ' ')}
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="font-medium text-muted-foreground">Confidence</div>
                        <div className="mt-1 text-2xl font-bold text-foreground">
                            {(winningValue * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
                <div className="mt-4">
                    <Progress
                        value={winningValue * 100}
                        className="h-3 bg-muted/50"
                        indicatorClassName={getBarColor(winningLabel)}
                        aria-label={`${winningLabel} confidence`}
                    />
                </div>
            </div>

            {entries.length > 1 && (
                <div className="space-y-3">
                    <button
                        type="button"
                        onClick={() => setShowBreakdown((current) => !current)}
                        className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                    >
                        {showBreakdown ? 'Hide probability breakdown' : 'View probability breakdown'}
                    </button>

                    {showBreakdown && (
                        <div className="space-y-5">
                            {entries.map(([key, value]) => (
                                <div key={key} className="space-y-2">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="font-medium text-muted-foreground capitalize">
                                            {key.replace(/_/g, ' ')}
                                        </span>
                                        <span className="font-bold text-foreground">
                                            {(value * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <Progress
                                        value={value * 100}
                                        className="h-2.5 bg-muted/50"
                                        indicatorClassName={getBarColor(key)}
                                        aria-label={`${key} probability`}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

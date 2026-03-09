import { Progress } from '@/components/ui/progress';
import type { ProbabilitiesSectionProps } from './types';

export function ProbabilitiesSection({ probabilities }: ProbabilitiesSectionProps) {
    const getBarColor = (key: string): string => {
        const keyLower = key.toLowerCase();
        if (keyLower.includes('safe')) return '!bg-green-600';
        if (keyLower.includes('medium')) return '!bg-yellow-500';
        return '!bg-red-600';
    };

    return (
        <div className="py-2 space-y-5">
            {Object.entries(probabilities).map(([key, value]) => (
                <div key={key} className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                        <span className="font-medium text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className="font-bold text-foreground">{(value * 100).toFixed(1)}%</span>
                    </div>
                    <Progress
                        value={value * 100}
                        className="h-2.5 bg-muted/50"
                        indicatorClassName={getBarColor(key).replace('bg-', 'bg-')} // Ensure we pass a color class
                        aria-label={`${key} probability`}
                    />
                </div>
            ))}
        </div>
    );
}

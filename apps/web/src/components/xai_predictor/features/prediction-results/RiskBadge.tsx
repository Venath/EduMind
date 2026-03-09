import { Badge } from '@/components/ui/badge';
import type { RiskBadgeProps } from './types';

export function RiskBadge({ riskLevel }: RiskBadgeProps) {
    const getBadgeStyles = () => {
        if (riskLevel === 'At-Risk') {
            return 'border border-red-200 bg-red-50 px-6 py-2 font-semibold text-red-700 shadow-sm hover:bg-red-100 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300 dark:hover:bg-red-950';
        }
        if (riskLevel === 'Medium Risk') {
            return 'border border-yellow-200 bg-yellow-50 px-6 py-2 font-semibold text-yellow-700 shadow-sm hover:bg-yellow-100 dark:border-yellow-900 dark:bg-yellow-950/60 dark:text-yellow-300 dark:hover:bg-yellow-950';
        }
        return 'border border-emerald-200 bg-emerald-50 px-6 py-2 font-semibold text-emerald-700 shadow-sm hover:bg-emerald-100 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300 dark:hover:bg-emerald-950';
    };

    return (
        <div className="text-center py-8 border-b">
            <Badge
                className={`${getBadgeStyles()} uppercase tracking-wider`}
                role="status"
                aria-label={`Risk level: ${riskLevel}`}
            >
                {riskLevel}
            </Badge>
        </div>
    );
}

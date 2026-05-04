export function getEngagementBadgeClass(level?: string | null): string {
    const normalized = (level ?? '').trim().toLowerCase();

    if (normalized.includes('high') || normalized.includes('safe')) {
        return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300';
    }

    if (normalized.includes('medium')) {
        return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/60 dark:text-amber-300';
    }

    if (normalized.includes('low')) {
        return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300';
    }

    return 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300';
}

export function getRiskBadgeClass(level?: string | null): string {
    const normalized = (level ?? '').trim().toLowerCase();

    if (normalized.includes('safe') || normalized === 'low') {
        return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-300';
    }

    if (normalized.includes('medium')) {
        return 'border-yellow-200 bg-yellow-50 text-yellow-700 dark:border-yellow-900 dark:bg-yellow-950/60 dark:text-yellow-300';
    }

    if (
        normalized.includes('high') ||
        normalized.includes('at-risk') ||
        normalized.includes('at risk')
    ) {
        return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/60 dark:text-red-300';
    }

    return 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300';
}

export function formatRiskBadgeLabel(level?: string | null): string {
    const normalized = (level ?? '').trim().toLowerCase();

    if (!normalized) {
        return 'Unknown';
    }

    if (normalized === 'safe') {
        return 'Safe';
    }

    if (normalized === 'medium' || normalized === 'medium risk') {
        return 'Medium Risk';
    }

    if (
        normalized === 'high' ||
        normalized === 'high risk' ||
        normalized === 'at-risk' ||
        normalized === 'at risk'
    ) {
        return 'At-Risk';
    }

    return level?.trim() || 'Unknown';
}

import { PageSkeleton } from '@/components/common/PageSkeleton';
import { createFileRoute } from '@tanstack/react-router';

interface AnalyticsSearch {
    student_id?: string;
}

export const Route = createFileRoute('/analytics')({
    pendingComponent: PageSkeleton,
    validateSearch: (search: Record<string, unknown>): AnalyticsSearch => ({
        student_id: typeof search.student_id === 'string' ? search.student_id : undefined,
    }),
});

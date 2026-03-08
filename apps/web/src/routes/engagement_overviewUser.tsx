import { PageSkeleton } from '@/components/common/PageSkeleton';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/engagement_overviewUser')({
    pendingComponent: PageSkeleton,
});

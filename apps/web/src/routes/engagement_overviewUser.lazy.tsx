import EngagementOverviewUser from '@/pages/EngagementOverviewUser';
import { createLazyFileRoute } from '@tanstack/react-router';

export const Route = createLazyFileRoute('/engagement_overviewUser')({
    component: EngagementOverviewUser,
});

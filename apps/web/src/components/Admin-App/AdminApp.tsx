import { useEffect, useState } from 'react';
import { useAuth } from '@/store/authStore';
import { AdminHero } from '../admin/AdminHero';
import { AnalyticsSection } from '../admin/AnalyticsSection';
import { CoursesSection } from '../admin/CoursesSection';
import { ResourcesSection } from '../admin/ResourcesSection';
import { StatsDashboard } from '../admin/StatsDashboard';

const ENGAGEMENT_API_URL =
  import.meta.env.VITE_ENGAGEMENT_TRACKER_API_URL ?? 'http://localhost:8005';
const LEARNING_STYLE_API_URL =
  import.meta.env.VITE_LEARNING_STYLE_API_URL ?? 'http://localhost:8006';
const XAI_API_URL =
  import.meta.env.VITE_XAI_API_URL ?? 'http://localhost:8004';

type EngagementStatsResponse = {
  total_students: number;
  avg_engagement_score: number;
};

type LearningStyleStatsResponse = {
  total_resources: number;
};

type XAIStatsResponse = {
  average_performance: number | null;
};

function AdminApp() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    students: 0,
    courses: 0,
    resources: 0,
    averagePerformance: 0
  });

  useEffect(() => {
    const loadStats = async () => {
      const instituteId = user?.institute_id ?? 'LMS_INST_A';

      try {
        const [engagementResponse, learningStyleResponse, xaiResponse] = await Promise.all([
          fetch(
            `${ENGAGEMENT_API_URL}/api/v1/stats?institute_id=${encodeURIComponent(instituteId)}`
          ),
          fetch(`${LEARNING_STYLE_API_URL}/api/v1/system/stats`),
          fetch(`${XAI_API_URL}/api/v1/academic-risk/stats`),
        ]);

        const engagementStats: EngagementStatsResponse | null = engagementResponse.ok
          ? await engagementResponse.json()
          : null;
        const learningStyleStats: LearningStyleStatsResponse | null = learningStyleResponse.ok
          ? await learningStyleResponse.json()
          : null;
        const xaiStats: XAIStatsResponse | null = xaiResponse.ok
          ? await xaiResponse.json()
          : null;

        setStats((current) => ({
          students: engagementStats?.total_students ?? current.students,
          courses: current.courses,
          resources: learningStyleStats?.total_resources ?? current.resources,
          averagePerformance:
            typeof xaiStats?.average_performance === 'number'
              ? Math.round(xaiStats.average_performance)
              : current.averagePerformance,
        }));
      } catch {
        setStats((current) => current);
      }
    };

    void loadStats();
  }, [user?.institute_id]);

  const scrollToSection = (sectionId: string) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-background">
      <AdminHero scrollToSection={scrollToSection} />
      <StatsDashboard stats={stats} />
      <CoursesSection />
      <ResourcesSection />
      <AnalyticsSection />
    </div>
  );
}

export default AdminApp;

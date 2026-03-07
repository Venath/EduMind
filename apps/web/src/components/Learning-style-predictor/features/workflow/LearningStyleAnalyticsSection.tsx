import type { LearningStyleType } from '../../core/types';
import type { StruggleTopicData } from '../../data/interfaces';
import {
    buildDistributionChartData,
    buildStruggleChartData,
    distributionChartOptions,
    struggleChartOptions,
} from '../../core/charts/learningStyleCharts';
import { useMemo } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import 'chart.js/auto';

interface LearningStyleAnalyticsSectionProps {
    styleDistribution: Record<LearningStyleType, number>;
    topStruggleTopics: StruggleTopicData[];
}

export function LearningStyleAnalyticsSection({
    styleDistribution,
    topStruggleTopics,
}: LearningStyleAnalyticsSectionProps) {
    const distributionChartData = useMemo(
        () => buildDistributionChartData(styleDistribution),
        [styleDistribution]
    );

    const struggleChartData = useMemo(
        () => buildStruggleChartData(topStruggleTopics),
        [topStruggleTopics]
    );

    return (
        <section className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-background dark:bg-slate-900 p-4 shadow-sm">
                <h3 className="mb-2 text-base font-bold text-slate-900 dark:text-slate-100">Learning Style Distribution</h3>
                <div className="h-72">
                    <Doughnut data={distributionChartData} options={distributionChartOptions} />
                </div>
            </div>

            {/* <div className="rounded-2xl border border-slate-200 bg-background dark:bg-slate-900 p-4 shadow-sm">
                <h3 className="mb-2 text-base font-bold text-slate-900 dark:text-slate-100">Top Struggle Topics</h3>
                <div className="h-72">
                    <Bar data={struggleChartData} options={struggleChartOptions} />
                </div>
            </div> */}
        </section>
    );
}

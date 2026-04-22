import type { RiskPredictionResponse, StudentRiskRequest } from '../../core/services/xaiService';
import type { ChangedMetric, InterventionPreset, MetricConfig, RiskChange } from './types';

export const metricConfigs: MetricConfig[] = [
    { field: 'avg_grade', label: 'Average Grade', unit: '%' },
    { field: 'grade_consistency', label: 'Grade Consistency', unit: '%' },
    { field: 'assessment_completion_rate', label: 'Completion Rate', unit: '%', multiplier: 100 },
    { field: 'num_assessments', label: 'Assessments', unit: '' },
    { field: 'studied_credits', label: 'Credits', unit: '' },
    { field: 'num_of_prev_attempts', label: 'Previous Attempts', unit: '' },
];

export function getRiskChange(
    currentPrediction: RiskPredictionResponse,
    simulatedPrediction: RiskPredictionResponse | null
): RiskChange | null {
    if (!simulatedPrediction) return null;

    const diff = simulatedPrediction.risk_score - currentPrediction.risk_score;
    return {
        value: Math.abs(diff * 100),
        isImprovement: diff < 0,
        percentage: diff
    };
}

export function getChangedMetrics(
    formData: StudentRiskRequest,
    scenarioData: StudentRiskRequest
): ChangedMetric[] {
    const changes: ChangedMetric[] = [];

    metricConfigs.forEach(({ field, label, unit, multiplier = 1 }) => {
        const original = formData[field] as number;
        const modified = scenarioData[field] as number;

        if (original !== modified) {
            changes.push({
                label,
                field,
                original: original * multiplier,
                modified: modified * multiplier,
                change: (modified - original) * multiplier,
                unit
            });
        }
    });

    return changes;
}

export const interventionPresets: InterventionPreset[] = [
    {
        id: 'tutoring-boost',
        title: 'Tutoring Boost',
        description: 'Lift grades and consistency with targeted tutoring support.',
        expectedImpact: 'Best when grade quality is the main risk driver.',
    },
    {
        id: 'completion-recovery',
        title: 'Completion Recovery',
        description: 'Push assessment completion and participation back into a safer band.',
        expectedImpact: 'Best when low engagement and incomplete work dominate the risk.',
    },
    {
        id: 'structured-study-plan',
        title: 'Structured Study Plan',
        description: 'Reduce volatility with steadier study behavior and more completed assessments.',
        expectedImpact: 'Best when consistency is weak and outcomes are unstable.',
    },
    {
        id: 'reassessment-support',
        title: 'Reassessment Support',
        description: 'Offset prior failures with stronger current performance and higher completion.',
        expectedImpact: 'Best when previous attempts are increasing current academic risk.',
    },
];

function clamp(value: number, min: number, max: number) {
    return Math.min(Math.max(value, min), max);
}

export function applyInterventionPreset(
    formData: StudentRiskRequest,
    presetId: string
): StudentRiskRequest {
    const next = { ...formData };

    switch (presetId) {
        case 'tutoring-boost':
            next.avg_grade = clamp(formData.avg_grade + 8, 0, 100);
            next.grade_consistency = clamp(formData.grade_consistency + 10, 0, 100);
            next.grade_range = clamp(formData.grade_range - 8, 0, 100);
            break;
        case 'completion-recovery':
            next.assessment_completion_rate = clamp(
                formData.assessment_completion_rate + 0.2,
                0,
                1
            );
            next.num_assessments = clamp(formData.num_assessments + 2, 0, 50);
            next.grade_consistency = clamp(formData.grade_consistency + 5, 0, 100);
            break;
        case 'structured-study-plan':
            next.grade_consistency = clamp(formData.grade_consistency + 12, 0, 100);
            next.grade_range = clamp(formData.grade_range - 10, 0, 100);
            next.num_assessments = clamp(formData.num_assessments + 1, 0, 50);
            next.studied_credits = clamp(formData.studied_credits + 15, 0, 240);
            break;
        case 'reassessment-support':
            next.avg_grade = clamp(formData.avg_grade + 6, 0, 100);
            next.assessment_completion_rate = clamp(
                formData.assessment_completion_rate + 0.15,
                0,
                1
            );
            next.num_assessments = clamp(formData.num_assessments + 1, 0, 50);
            next.grade_consistency = clamp(formData.grade_consistency + 6, 0, 100);
            break;
        default:
            return formData;
    }

    next.low_performance = next.avg_grade < 40 ? 1 : 0;
    next.low_engagement = next.assessment_completion_rate < 0.6 ? 1 : 0;
    next.has_previous_attempts = next.num_of_prev_attempts > 0 ? 1 : 0;

    return next;
}

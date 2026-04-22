import type { RiskPredictionResponse, StudentRiskRequest } from '../../core/services/xaiService';

export type PredictionResultsProps = {
    prediction: RiskPredictionResponse;
    formData: StudentRiskRequest;
    predictionSource: 'connected' | 'temporary';
    instituteId?: string;
    actionPlan: any[];
    theme: 'dark' | 'light';
    searchTerm: string;
    filterCategory: string;
    filterPriority: string;
    onSearchChange: (value: string) => void;
    onFilterCategoryChange: (value: string) => void;
    onFilterPriorityChange: (value: string) => void;
    onToggleComplete: (id: string) => void;
    onRemoveAction: (id: string) => void;
    onShowCustomize: () => void;
    onExportPDF: () => void;
    onShare: () => void;
    onPrint: () => void;
    onExportImage: () => void;
    onWhatIf: () => void;
    onReset: () => void;
    getProgress: () => number;
    setAriaAnnouncement: (message: string) => void;
};

export type QuickActionsProps = {
    onExportPDF: () => void;
    onShare: () => void;
    onPrint: () => void;
    onExportImage: () => void;
    onWhatIf: () => void;
    onReset: () => void;
    setAriaAnnouncement: (message: string) => void;
};

export type RiskBadgeProps = {
    riskLevel: string;
};

export type RiskGaugeProps = {
    riskScore: number;
    riskLevel: string;
    theme: 'dark' | 'light';
};

export type ProbabilitiesSectionProps = {
    probabilities: Record<string, number>;
    riskLevel: string;
};

export type CounterfactualSectionProps = {
    counterfactual: RiskPredictionResponse['counterfactual'];
};

export type RiskTimelineSectionProps = {
    studentId: string;
    predictionId: string;
    source: 'connected' | 'temporary';
    prediction: RiskPredictionResponse;
    formData: StudentRiskRequest;
};

export type StudentInsightsSectionProps = {
    prediction: RiskPredictionResponse;
    formData: StudentRiskRequest;
    source: 'connected' | 'temporary';
    instituteId?: string;
};

export type RiskFactor = {
    name: string;
    impact: number; // 0-100
    category: 'academic' | 'engagement' | 'behavioral';
};

export type RiskFactorsChartProps = {
    factors: RiskFactor[];
};
export type StudentMetrics = {
    academicPerformance: number; // 0-100
    attendance: number;
    engagement: number;
    assignmentCompletion: number;
    participationScore: number;
};

export type StudentMetricsChartProps = {
    metrics: StudentMetrics;
    classAverage?: StudentMetrics;
    theme: 'light' | 'dark';
};

export type TrendData = {
    metric: string;
    current: number;
    previous: number;
    trend: 'up' | 'down' | 'stable';
};

export type TrendIndicatorsProps = {
    trends: TrendData[];
};

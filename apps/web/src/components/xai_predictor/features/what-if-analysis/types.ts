import type { RiskPredictionResponse, StudentRiskRequest } from '../../core/services/xaiService';
export type WhatIfModalProps = {
    show: boolean;
    onClose: () => void;
    currentPrediction: RiskPredictionResponse;
    formData: StudentRiskRequest;
    onSimulate: (scenarioData: StudentRiskRequest) => Promise<RiskPredictionResponse>;
};
export type WhatIfModalHeaderProps = {
    onClose: () => void;
};
export type ChangedMetricsSummaryProps = {
    changedMetrics: ChangedMetric[];
};
export type RiskComparisonProps = {
    currentPrediction: RiskPredictionResponse;
    simulatedPrediction: RiskPredictionResponse | null;
    riskChange: RiskChange | null;
};
export type MetricSliderProps = {
    id: string;
    label: string;
    value: number;
    min: number;
    max: number;
    step: number;
    unit?: string;
    labels: string[];
    onChange: (value: number) => void;
    formatValue?: (value: number) => string;
};
export type ScenarioControlsProps = {
    scenarioData: StudentRiskRequest;
    onSliderChange: (field: keyof StudentRiskRequest, value: number) => void;
};
export type InterventionPreset = {
    id: string;
    title: string;
    description: string;
    expectedImpact: string;
};
export type InterventionPresetsProps = {
    presets: InterventionPreset[];
    selectedPresetId: string | null;
    onApplyPreset: (presetId: string) => void;
};
export type ModalActionsProps = {
    onReset: () => void;
    onSimulate: () => void;
    isSimulating: boolean;
    hasChanges: boolean;
};

// * Types for whatIfUtils
export type MetricConfig = {
    field: keyof StudentRiskRequest;
    label: string;
    unit: string;
    multiplier?: number;
};

export type ChangedMetric = {
    label: string;
    field: keyof StudentRiskRequest;
    original: number;
    modified: number;
    change: number;
    unit: string;
};

export type RiskChange = {
    value: number;
    isImprovement: boolean;
    percentage: number;
};

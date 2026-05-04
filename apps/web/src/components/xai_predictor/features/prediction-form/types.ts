import type { UseFormReturn } from 'react-hook-form';
import type { StudentRiskRequest } from '../../core/schemas/xai.schemas';

export type PredictionFormProps = {
    form: UseFormReturn<StudentRiskRequest>;
    onSubmit: (e: React.FormEvent) => void;
    onAnalyzeConnectedStudent: (studentId: string) => Promise<void>;
    onLoadTemporaryStudent: (studentId: string) => Promise<void>;
    activeMode: 'connected' | 'temporary';
    onActiveModeChange: (mode: 'connected' | 'temporary') => void;
    onClearDraft: () => void;
    isLoading: boolean;
    isHealthy: boolean;
    prefilledStudentId?: string;
    temporaryHistoryRefreshToken: number;
}

export type FormActionsProps = {
    isLoading: boolean;
    isHealthy: boolean;
    onClearDraft: () => void;
}

// Sections no longer need props as they use context
export type EngagementSectionProps = {}
export type HistoricalDataSectionProps = {}
export type AcademicPerformanceSectionProps = {}
export type StudentInfoSectionProps = {
    isAnalyzingConnectedStudent: boolean;
    onAnalyzeConnectedStudent: (studentId: string) => Promise<void>;
    prefilledStudentId?: string;
}

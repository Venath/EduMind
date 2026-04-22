/**
 * XAI Prediction Orchestrator
 * Refactored to use pure Zustand + Custom Hook (No Context)
 * UI Components imported directly (no wrappers)
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useSearch } from '@tanstack/react-router';
import { useForm } from 'react-hook-form';
import { useEffect, useState } from 'react';
import { useAuth } from '@/store/authStore';
import { useResultsActions } from '../core/hooks/useResultsActions';
import { xaiService } from '../core/services/xaiService';
import { useXAILogic } from '../core/hooks/useXAILogic';
import { StudentRiskRequestSchema, type StudentRiskRequest } from '../core/schemas/xai.schemas';
import { XAIOverviewSection } from '../features/dashboard/XAIOverviewSection';
import { PredictionForm } from '../features/prediction-form/PredictionForm';
import { PredictionResults } from '../features/prediction-results/PredictionResults';
import { ModelDownFallback } from '../ui/fallbacks/ModelDownFallback';
import { ErrorDisplay, XAILayout } from '../ui/layout/XAILayout';
import { XAIModals } from '../ui/modals-container/XAIModals';
import { PredictionResultsSkeleton } from '../ui/skeletons/PredictionResultsSkeleton';

export function XAIPredictionOrchestrator() {
    // Access logic from custom hook (replaces Context)
    const { prediction, modelHealth, toast, form: storeForm, actionPlan, ui, modal, filter, aria, store } = useXAILogic();
    const { user } = useAuth();
    const search = useSearch({ from: '/analytics' });
    const urlStudentId = (search as { student_id?: string }).student_id;
    const [activeMode, setActiveMode] = useState<'connected' | 'temporary'>('connected');
    const [connectedStudentContextId, setConnectedStudentContextId] = useState<string | undefined>(
        urlStudentId
    );
    const [predictionSource, setPredictionSource] = useState<'connected' | 'temporary'>(
        urlStudentId ? 'connected' : 'temporary'
    );
    const [isResolvingStudent, setIsResolvingStudent] = useState(false);
    const [isSubmittingTemporary, setIsSubmittingTemporary] = useState(false);
    const [isLoadingTemporaryRecord, setIsLoadingTemporaryRecord] = useState(false);
    const [temporaryHistoryRefreshToken, setTemporaryHistoryRefreshToken] = useState(0);

    // RHF Init
    const form = useForm<StudentRiskRequest>({
        resolver: zodResolver(StudentRiskRequestSchema),
        defaultValues: storeForm.formData, // Init with store values
    });

    const { getValues, handleSubmit, reset } = form;

    useEffect(() => {
        if (!urlStudentId) {
            return;
        }

        const nextFormData = {
            ...getValues(),
            student_id: urlStudentId,
        };

        prediction.reset();
        store.setActionPlan([]);
        storeForm.setFormData(nextFormData);
        reset(nextFormData);
        setActiveMode('connected');
        setConnectedStudentContextId(urlStudentId);
        setPredictionSource('connected');
        // Route-scoped entry should populate the student form section and clear stale results.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [urlStudentId]);

    const onSubmit = async (data: StudentRiskRequest) => {
        aria.announceLoading();
        setIsSubmittingTemporary(true);
        try {
            storeForm.setFormData(data); // Sync to store
            prediction.reset();
            store.setActionPlan([]);
            const response = await xaiService.predictTemporaryRisk(data);
            store.setCurrentPrediction(response);
            setActiveMode('temporary');
            setPredictionSource('temporary');
            setTemporaryHistoryRefreshToken((current) => current + 1);
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : `Failed to analyze temporary student ${data.student_id}`;
            toast.showError(message);
            aria.announceError();
        } finally {
            setIsSubmittingTemporary(false);
        }
    };

    const handleLoadTemporaryStudent = async (studentId: string) => {
        aria.announceLoading();
        setIsLoadingTemporaryRecord(true);
        try {
            prediction.reset();
            store.setActionPlan([]);
            const savedRecord = await xaiService.getTemporaryStudentRecord(studentId);
            storeForm.setFormData(savedRecord.request_payload);
            reset(savedRecord.request_payload);
            store.setCurrentPrediction(savedRecord.prediction);
            setActiveMode('temporary');
            setPredictionSource('temporary');
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : `Failed to load temporary student ${studentId}`;
            toast.showError(message);
            aria.announceError();
        } finally {
            setIsLoadingTemporaryRecord(false);
        }
    };

    const handleAnalyzeConnectedStudent = async (studentId: string) => {
        aria.announceLoading();
        setIsResolvingStudent(true);
        try {
            prediction.reset();
            store.setActionPlan([]);
            const derivedRequest = await xaiService.getConnectedStudentRequest(studentId);
            storeForm.setFormData(derivedRequest);
            reset(derivedRequest);
            setActiveMode('connected');
            setConnectedStudentContextId(studentId);
            setPredictionSource('connected');
            await prediction.predictAsync(derivedRequest);
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : `Failed to analyze student ${studentId}`;
            toast.showError(message);
            aria.announceError();
        } finally {
            setIsResolvingStudent(false);
        }
    };

    const resolvedPrediction = store.currentPrediction ?? prediction.prediction;
    const activePrediction =
        predictionSource === 'connected' && connectedStudentContextId
            ? resolvedPrediction?.student_id === connectedStudentContextId
                ? resolvedPrediction
                : null
            : resolvedPrediction;
    const isBusy =
        prediction.isLoading ||
        isResolvingStudent ||
        isSubmittingTemporary ||
        isLoadingTemporaryRecord;
    const systemStatus = modelHealth.isLoading
        ? 'checking'
        : modelHealth.isHealthy
            ? 'healthy'
            : modelHealth.isError
                ? 'offline'
                : 'degraded';
    const systemMessage = modelHealth.isHealthy
        ? 'XAI prediction service is operational'
        : modelHealth.isLoading
            ? 'Checking XAI prediction service status'
            : modelHealth.error instanceof Error
                ? modelHealth.error.message
                : 'XAI prediction service is unavailable';
    const summaryStudentId = activePrediction?.student_id || storeForm.formData.student_id;

    // Results actions hook
    const resultsActions = useResultsActions({
        removeAction: actionPlan.removeAction,
        showSuccess: toast.showSuccess,
        showInfo: toast.showInfo,
        reset: () => {
            prediction.reset();
            reset(storeForm.formData); // Reset RHF to store defaults
        },
        announceReset: aria.announceReset,
        openWhatIfModal: ui.openWhatIfModal
    });

    // Handle Clear Draft logic (which was passed to FormState)
    const handleClearDraft = () => {
        storeForm.clearDraft();
        reset(storeForm.formData); // RHF reset
    };

    // Model down fallback - early return
    if (!modelHealth.isHealthy && !modelHealth.isModelLoaded) {
        return (
            <ModelDownFallback
                onRetry={modelHealth.refetch}
                modelStatus={modelHealth.health?.status || 'unknown'}
            />
        );
    }

    // Main render
    return (
        <XAILayout
            theme={ui.theme}
            ariaAnnouncement={aria.ariaAnnouncement}
            toast={toast.toast}
            onToggleTheme={ui.toggleTheme}
        >
            <XAIOverviewSection
                systemStatus={systemStatus}
                systemMessage={systemMessage}
                currentStudentId={summaryStudentId}
                latestRiskLevel={activePrediction?.risk_level}
                confidence={activePrediction?.confidence}
                modelLoaded={modelHealth.isModelLoaded}
            />

            <ErrorDisplay error={prediction.isError ? prediction.error : null} />

            {/* Loading State */}
            {isBusy && (
                <div role="status" aria-label="Loading prediction results">
                    <PredictionResultsSkeleton />
                </div>
            )}

            {/* Form State */}
            {!isBusy && (
                <PredictionForm
                    form={form}
                    onSubmit={handleSubmit(onSubmit)}
                    onAnalyzeConnectedStudent={handleAnalyzeConnectedStudent}
                    onLoadTemporaryStudent={handleLoadTemporaryStudent}
                    activeMode={activeMode}
                    onActiveModeChange={setActiveMode}
                    onClearDraft={handleClearDraft}
                    isLoading={isBusy}
                    isHealthy={modelHealth.isHealthy}
                    prefilledStudentId={connectedStudentContextId}
                    temporaryHistoryRefreshToken={temporaryHistoryRefreshToken}
                />
            )}

            {/* Results State */}
            {activePrediction && !isBusy && (
                <PredictionResults
                    prediction={activePrediction}
                    formData={storeForm.formData}
                    predictionSource={predictionSource}
                    instituteId={user?.institute_id}
                    actionPlan={actionPlan.actionPlan}
                    theme={ui.theme}
                    searchTerm={filter.searchTerm}
                    filterCategory={filter.filterCategory}
                    filterPriority={filter.filterPriority}
                    onSearchChange={filter.setSearchTerm}
                    onFilterCategoryChange={filter.setFilterCategory}
                    onFilterPriorityChange={filter.setFilterPriority}
                    onToggleComplete={actionPlan.toggleComplete}
                    onRemoveAction={resultsActions.handleRemoveAction}
                    onShowCustomize={modal.openModal}
                    onExportPDF={ui.handleExportPDF}
                    onShare={ui.handleShare}
                    onPrint={ui.handleExportPDF}
                    onExportImage={resultsActions.handleExportImage}
                    onWhatIf={resultsActions.handleWhatIf}
                    onReset={resultsActions.handleReset}
                    getProgress={actionPlan.getProgress}
                    setAriaAnnouncement={aria.setAriaAnnouncement}
                />
            )}

            {/* Modals */}
            <XAIModals />
        </XAILayout>
    );
}

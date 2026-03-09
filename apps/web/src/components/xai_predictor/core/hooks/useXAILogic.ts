import type { LoadingState } from '@/components/common/types/LoadingState';
import { LOADING_STATES } from '@/components/common/types/LoadingState';
import { eventBus, PREDICTION_EVENTS, type PredictionErrorEvent, type PredictionStartedEvent, type PredictionSuccessEvent } from '@/lib/events/eventBus';
import { useXAIStore } from '@/store/xai';
import { useCallback, useEffect, useState } from 'react';
import { generateDynamicActionPlan } from '../../utils/generateDynamicActionPlan';
import { xaiPredictionRepository } from '../repositories/xaiPredictionRepository';
import type { RiskPredictionResponse, StudentRiskRequest } from '../services/xaiService';
import { xaiService } from '../services/xaiService';
import { useModelHealth } from './useModelHealth';
import { useStudentRiskPrediction } from './useStudentRiskPrediction';

// Default form data to ensure all fields exist
const DEFAULT_FORM_DATA: StudentRiskRequest = {
    student_id: '',
    avg_grade: 70,
    grade_consistency: 85,
    grade_range: 30,
    num_assessments: 8,
    assessment_completion_rate: 0.8,
    studied_credits: 60,
    num_of_prev_attempts: 0,
    low_performance: 0,
    low_engagement: 0,
    has_previous_attempts: 0,
};

interface ToastState {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
}

export function useXAILogic(options?: { enablePersistence?: boolean; enableEvents?: boolean }) {
    const { enablePersistence = true, enableEvents = true } = options || {};

    // Zustand store for all UI state
    const store = useXAIStore();

    // Local toast state (ephemeral, doesn't need global state)
    const [toast, setToast] = useState<ToastState>({
        show: false,
        message: '',
        type: 'info',
    });

    // Loading state machine
    const [loadingState, setLoadingState] = useState<LoadingState>(LOADING_STATES.IDLE);

    // Local aria state
    const [ariaAnnouncement, setAriaAnnouncement] = useState('');

    // React Query hooks for async operations
    const prediction = useStudentRiskPrediction();
    const modelHealth = useModelHealth();
    const activePrediction = store.currentPrediction ?? prediction.prediction;

    // Toast functions
    const showToast = useCallback((message: string, type: ToastState['type'] = 'info') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast(prev => ({ ...prev, show: false })), 3000);
    }, []);

    const showSuccess = useCallback((message: string) => showToast(message, 'success'), [showToast]);
    const showError = useCallback((message: string) => showToast(message, 'error'), [showToast]);
    const showInfo = useCallback((message: string) => showToast(message, 'info'), [showToast]);

    // Auto-generate action plan when prediction completes
    // Use the active prediction so loaded temporary history and manual submissions
    // produce the same action-plan state as a fresh connected prediction.
    useEffect(() => {
        if (activePrediction?.prediction_id) {
            const dynamicPlan = generateDynamicActionPlan(
                activePrediction,
                store.actionPlan || [] // Pass existing plan to preserve completion state
            );
            console.log('[useXAILogic] Generated action plan:', {
                predictionId: activePrediction.prediction_id,
                actionCount: dynamicPlan.length,
                actions: dynamicPlan.map(a => a.title)
            });
            store.setActionPlan(dynamicPlan);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activePrediction?.prediction_id]); // Only re-run when prediction ID changes


    // Ensure formData always has all fields with fallback defaults
    const safeFormData: StudentRiskRequest = {
        ...DEFAULT_FORM_DATA,
        ...(store.formData || {}),
    };

    // Form object - delegates to Zustand store
    const form = {
        formData: safeFormData,
        setFormData: store.setFormData,
        updateFormData: store.updateFormData,
        clearDraft: store.clearDraft,
        resetForm: store.resetForm,
    };

    // Action plan object - delegates to Zustand store
    const actionPlan = {
        actionPlan: store.actionPlan || [],
        addAction: store.addAction,
        removeAction: store.removeAction,
        toggleComplete: store.toggleActionComplete,
        getProgress: store.getProgress,
        getFilteredActions: store.getFilteredActions,
    };

    // Filter object - delegates to Zustand store
    const safeFilters = store.filters || { priorities: [], categories: [], showCompleted: true };
    const filter = {
        searchTerm: store.searchQuery || '',
        setSearchTerm: store.setSearchQuery,
        filterCategory: safeFilters.categories[0] || 'all',
        setFilterCategory: (cat: string) => store.updateFilters({ categories: cat && cat !== 'all' ? [cat] : [] }),
        filterPriority: safeFilters.priorities[0] || 'all',
        setFilterPriority: (priority: string) => store.updateFilters({ priorities: priority && priority !== 'all' ? [priority] : [] }),
    };

    // Modal object - delegates to Zustand store
    const safeNewActionItem = store.newActionItem || { title: '', description: '', priority: 'standard', category: 'academic' };
    const modal = {
        showCustomizeModal: store.isCustomActionModalOpen || false,
        newActionItem: safeNewActionItem,
        openModal: () => store.setCustomActionModalOpen(true),
        closeModal: () => {
            store.setCustomActionModalOpen(false);
            store.resetNewActionItem();
        },
        updateTitle: (title: string) => store.updateNewActionItem('title', title),
        updateDescription: (desc: string) => store.updateNewActionItem('description', desc),
        updatePriority: (priority: string) => store.updateNewActionItem('priority', priority as 'critical' | 'high' | 'medium' | 'standard'),
        updateCategory: (category: string) => store.updateNewActionItem('category', category as 'academic' | 'engagement' | 'time-management' | 'support'),
        addCustomAction: () => {
            store.submitNewAction();
            showSuccess('Custom action added to your plan');
        },
    };

    // UI object - delegates to Zustand store
    const ui = {
        theme: store.theme || 'light',
        toggleTheme: () => {
            const newTheme = (store.theme || 'light') === 'light' ? 'dark' : 'light';
            store.setTheme(newTheme);
            showInfo(`Switched to ${newTheme} mode`);
        },
        shareLink: store.shareLink || '',
        showShareModal: store.isShareModalOpen || false,
        showWhatIfModal: store.isWhatIfModalOpen || false,
        openWhatIfModal: () => {
            console.log('[useXAILogic ui] openWhatIfModal called');
            console.log('[useXAILogic ui] Current isWhatIfModalOpen:', store.isWhatIfModalOpen);
            console.log('[useXAILogic ui] Store object:', store);
            console.log('[useXAILogic ui] Calling store.setWhatIfModalOpen(true)');
            store.setWhatIfModalOpen(true);
            console.log('[useXAILogic ui] After calling setter, isWhatIfModalOpen:', store.isWhatIfModalOpen);
        },
        closeWhatIfModal: () => store.setWhatIfModalOpen(false),
        closeShareModal: () => store.setShareModalOpen(false),
        handleShare: () => {
            if (!prediction.prediction) return;
            const data = {
                studentId: safeFormData.student_id,
                riskLevel: prediction.prediction.risk_level,
                riskScore: prediction.prediction.risk_score,
                confidence: prediction.prediction.confidence,
                timestamp: new Date().toISOString()
            };
            const encoded = btoa(JSON.stringify(data));
            const link = `${window.location.origin}${window.location.pathname}?share = ${encoded} `;
            store.setShareLink(link);
            store.setShareModalOpen(true);
        },
        copyToClipboard: async () => {
            try {
                await navigator.clipboard.writeText(store.shareLink || '');
                showSuccess('Link copied to clipboard!');
            } catch {
                showError('Failed to copy link');
            }
        },
        handleExportPDF: async () => {
            if (prediction.prediction) {
                const { exportPredictionToPDF } = await import('../../utils/exportPDF');
                exportPredictionToPDF(prediction.prediction, safeFormData, store.actionPlan || []);
                showSuccess('Report ready to save as PDF');
            }
        },
        simulateScenario: async (scenarioData: StudentRiskRequest): Promise<RiskPredictionResponse> => {
            const startTime = Date.now();
            try {
                // Emit start event
                if (enableEvents) {
                    await eventBus.emit<PredictionStartedEvent>(PREDICTION_EVENTS.STARTED, {
                        type: 'xai',
                        timestamp: new Date().toISOString(),
                        studentId: scenarioData.student_id,
                    });
                }

                const result = await xaiService.predictRisk(scenarioData);

                // Save to repository if enabled
                if (enablePersistence) {
                    await xaiPredictionRepository.save(result);
                }

                // Emit success event
                if (enableEvents) {
                    await eventBus.emit<PredictionSuccessEvent>(PREDICTION_EVENTS.SUCCESS, {
                        type: 'xai',
                        timestamp: new Date().toISOString(),
                        studentId: scenarioData.student_id,
                        duration: Date.now() - startTime,
                    });
                }

                showSuccess('Scenario simulated successfully!');
                return result;
            } catch (error) {
                // Emit error event
                if (enableEvents) {
                    await eventBus.emit<PredictionErrorEvent>(PREDICTION_EVENTS.ERROR, {
                        type: 'xai',
                        timestamp: new Date().toISOString(),
                        studentId: scenarioData.student_id,
                        error: error instanceof Error ? error : new Error('Unknown error'),
                        duration: Date.now() - startTime,
                    });
                }

                showError('Failed to simulate scenario');
                throw new Error('Simulation failed');
            }
        },
    };

    // Aria object
    const aria = {
        ariaAnnouncement,
        setAriaAnnouncement,
        announceLoading: () => setAriaAnnouncement('Analyzing student data. Please wait.'),
        announceError: () => setAriaAnnouncement('Prediction failed. Please try again.'),
        announceReset: () => setAriaAnnouncement('Prediction cleared. Ready for new prediction.'),
    };

    // Toast object
    const toastObj = {
        toast,
        showToast,
        showSuccess,
        showError,
        showInfo,
        hideToast: () => setToast(prev => ({ ...prev, show: false })),
    };

    // History loader
    const loadHistory = useCallback(async (studentId: string) => {
        if (!enablePersistence) return [];
        return xaiPredictionRepository.getHistory(studentId);
    }, [enablePersistence]);

    return {
        prediction: {
            ...prediction,
            prediction: activePrediction
        },
        modelHealth,
        toast: toastObj,
        form,
        actionPlan,
        ui,
        modal,
        filter,
        aria,
        loadingState,
        loadHistory,
        store, // Direct access to Zustand store
    };
}

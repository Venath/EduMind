import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Sliders } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { RiskPredictionResponse, StudentRiskRequest } from '../../core/services/xaiService';
import { ChangedMetricsSummary } from './ChangedMetricsSummary';
import { InterventionPresets } from './InterventionPresets';
import { ModalActions } from './ModalActions';
import { RiskComparison } from './RiskComparison';
import { ScenarioControls } from './ScenarioControls';
import { ScenarioHint } from './ScenarioHint';
import { ScenarioIntro } from './ScenarioIntro';
import type { WhatIfModalProps } from './types';
import {
    applyInterventionPreset,
    getChangedMetrics,
    getRiskChange,
    interventionPresets,
} from './whatIfUtils';

export function WhatIfModal({
    show,
    onClose,
    currentPrediction,
    formData,
    onSimulate
}: WhatIfModalProps) {
    const [scenarioData, setScenarioData] = useState<StudentRiskRequest>(formData);
    const [simulatedPrediction, setSimulatedPrediction] = useState<RiskPredictionResponse | null>(null);
    const [isSimulating, setIsSimulating] = useState(false);
    const [selectedPresetId, setSelectedPresetId] = useState<string | null>(null);

    // Update state when formData changes (reset on open usually handled by parent or effect, but here we init state)
    // Note: In a real app, you might want a useEffect to sync scenarioData with formData when modal opens
    // Update state when formData changes (reset on open usually handled by parent or effect, but here we init state)
    // Note: In a real app, you might want a useEffect to sync scenarioData with formData when modal opens
    useEffect(() => {
        if (show) {
            setScenarioData(formData);
            setSimulatedPrediction(null);
            setSelectedPresetId(null);
        }
    }, [show]); // Only reset when modal opens (prevents reset on parent rerenders causing formData ref change)

    const handleSliderChange = (field: keyof StudentRiskRequest, value: number) => {
        setScenarioData(prev => ({ ...prev, [field]: value }));
        setSimulatedPrediction(null);
        setSelectedPresetId(null);
    };

    const handleApplyPreset = (presetId: string) => {
        setScenarioData(applyInterventionPreset(formData, presetId));
        setSelectedPresetId(presetId);
        setSimulatedPrediction(null);
    };

    const handleSimulate = async () => {
        setIsSimulating(true);
        try {
            const result = await onSimulate(scenarioData);
            setSimulatedPrediction(result);
        } catch (error) {
            console.error('Simulation failed:', error);
        } finally {
            setIsSimulating(false);
        }
    };

    const handleReset = () => {
        setScenarioData(formData);
        setSimulatedPrediction(null);
        setSelectedPresetId(null);
    };

    const riskChange = getRiskChange(currentPrediction, simulatedPrediction);
    const changedMetrics = getChangedMetrics(formData, scenarioData);
    const hasChanges = changedMetrics.length > 0;

    return (
        <Dialog open={show} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader className="pb-4 border-b">
                        <DialogTitle className="flex items-center gap-2 text-2xl font-bold">
                            <Sliders className="h-6 w-6" />
                            What-If And Intervention Simulator
                        </DialogTitle>
                    </DialogHeader>

                <div className="space-y-8 py-4 px-1">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* Left Column: Visualizations & Results */}
                        <div className="space-y-6">
                            <ScenarioIntro />
                            <ChangedMetricsSummary changedMetrics={changedMetrics} />
                            <RiskComparison
                                currentPrediction={currentPrediction}
                                simulatedPrediction={simulatedPrediction}
                                riskChange={riskChange}
                            />
                            {!hasChanges && <ScenarioHint />}
                        </div>

                        {/* Right Column: Controls */}
                        <div className="space-y-6">
                            <InterventionPresets
                                presets={interventionPresets}
                                selectedPresetId={selectedPresetId}
                                onApplyPreset={handleApplyPreset}
                            />
                            <ScenarioControls
                                scenarioData={scenarioData}
                                onSliderChange={handleSliderChange}
                            />
                        </div>
                    </div>

                    <ModalActions
                        onReset={handleReset}
                        onSimulate={handleSimulate}
                        isSimulating={isSimulating}
                        hasChanges={hasChanges}
                    />
                </div>
            </DialogContent>
        </Dialog>
    );
}

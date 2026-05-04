import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, LayoutDashboard, TrendingUp } from 'lucide-react';
import { ActionPlanSection } from '../action-plan/ActionPlanSection';
import { CounterfactualSection } from './CounterfactualSection';
import { ProbabilitiesSection } from './ProbabilitiesSection';
import { QuickActions } from './QuickActions';
import { RiskBadge } from './RiskBadge';
import { RiskFactorsChart } from './RiskFactorsChart';
import { RiskGauge } from './RiskGauge';
import { StudentInsightsSection } from './StudentInsightsSection';
import { RiskTimelineSection } from './RiskTimelineSection';
import type { PredictionResultsProps } from './types';

export function PredictionResults({
    prediction,
    predictionSource,
    formData,
    instituteId,
    actionPlan,
    searchTerm,
    filterCategory,
    filterPriority,
    onSearchChange,
    onFilterCategoryChange,
    onFilterPriorityChange,
    onToggleComplete,
    onRemoveAction,
    onShowCustomize,
    onExportPDF,
    onShare,
    onPrint,
    onExportImage,
    onWhatIf,
    onReset,
    getProgress,
    setAriaAnnouncement
}: PredictionResultsProps) {
    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header with Quick Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b pb-6">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
                        <LayoutDashboard className="h-8 w-8 text-primary" />
                        Prediction Analysis
                    </h2>
                    <p className="text-muted-foreground mt-2 text-lg">
                        Comprehensive risk assessment and AI-driven insights for student success.
                    </p>
                    <p className="mt-2 text-sm font-medium text-primary">
                        Student ID: {prediction.student_id}
                    </p>
                </div>
                <QuickActions
                    onExportPDF={onExportPDF}
                    onShare={onShare}
                    onPrint={onPrint}
                    onExportImage={onExportImage}
                    onWhatIf={onWhatIf}
                    onReset={onReset}
                    setAriaAnnouncement={setAriaAnnouncement}
                />
            </div>

            {/* Main Dashboard Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* 1. Risk Overview Score (Left Column) */}
                <Card className="lg:col-span-4 shadow-sm hover:shadow-md transition-shadow duration-200 border">
                    <CardHeader className="pb-4 border-b bg-muted/30">
                        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                            <TrendingUp className="h-5 w-5 text-primary" />
                            Risk Score
                        </CardTitle>
                        <CardDescription>Overall assessment of student risk</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center p-8 space-y-8">
                        <div className="w-full flex justify-center">
                            {(() => {
                                console.log('PredictionResults - Full prediction object:', prediction);
                                console.log('PredictionResults - risk_score value:', prediction.risk_score);
                                console.log('PredictionResults - risk_score type:', typeof prediction.risk_score);
                                return (
                                    <RiskGauge
                                        riskScore={prediction.risk_score}
                                        riskLevel={prediction.risk_level}
                                        probabilities={prediction.probabilities}
                                    />
                                );
                            })()}
                        </div>
                        <RiskBadge riskLevel={prediction.risk_level} />
                    </CardContent>
                </Card>

                {/* 2. Key Factors & Probabilities (Right Column) */}
                <Card className="lg:col-span-8 shadow-sm hover:shadow-md transition-shadow duration-200 border">
                    <CardHeader className="pb-4 border-b bg-muted/30">
                        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                            <AlertTriangle className="h-5 w-5 text-primary" />
                            Risk Analysis
                        </CardTitle>
                        <CardDescription>Breakdown of contributing factors and outcome probabilities</CardDescription>
                    </CardHeader>
                    <CardContent className="p-6">
                        <div className="grid gap-8 md:grid-cols-2 h-full">
                            <div className="space-y-4">
                                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Top Risk Factors</h4>
                                <RiskFactorsChart
                                    factors={(prediction.top_risk_factors || []).map(f => ({
                                        name: f.feature,
                                        impact: f.value * 100,
                                        category: (f.feature.toLowerCase().includes('grade') || f.feature.toLowerCase().includes('score') || f.feature.toLowerCase().includes('gpa')) ? 'academic' :
                                            (f.feature.toLowerCase().includes('attendance') || f.feature.toLowerCase().includes('login')) ? 'engagement' : 'behavioral'
                                    }))}
                                />
                            </div>
                            <div className="space-y-4 border-t pt-6 md:border-t-0 md:border-l md:pt-0 md:pl-8">
                                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Outcome Likelihood</h4>
                                <ProbabilitiesSection
                                    probabilities={prediction.probabilities}
                                    riskLevel={prediction.risk_level}
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <CounterfactualSection counterfactual={prediction.counterfactual} />

                <RiskTimelineSection
                    studentId={prediction.student_id}
                    predictionId={prediction.prediction_id}
                    source={predictionSource}
                    prediction={prediction}
                    formData={formData}
                />

                <StudentInsightsSection
                    prediction={prediction}
                    formData={formData}
                    source={predictionSource}
                    instituteId={instituteId}
                />

                {/* 3. Personalized Action Plan (Full Width Below) */}
                <div className="lg:col-span-12">
                    <ActionPlanSection
                        prediction={prediction}
                        actionPlan={actionPlan}
                        searchTerm={searchTerm}
                        filterCategory={filterCategory}
                        filterPriority={filterPriority}
                        onSearchChange={onSearchChange}
                        onFilterCategoryChange={onFilterCategoryChange}
                        onFilterPriorityChange={onFilterPriorityChange}
                        onToggleComplete={onToggleComplete}
                        onRemoveAction={onRemoveAction}
                        onShowCustomize={onShowCustomize}
                        getProgress={getProgress}
                        setAriaAnnouncement={setAriaAnnouncement}
                    />
                </div>
            </div>
        </div>
    );
}

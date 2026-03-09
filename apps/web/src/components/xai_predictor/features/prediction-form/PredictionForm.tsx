import { Database } from 'lucide-react';
import { FormProvider } from 'react-hook-form';
import { useState } from 'react';
import { AcademicPerformanceSection } from './AcademicPerformanceSection';
import { EngagementSection } from './EngagementSection';
import { FormActions } from './FormActions';
import { HistoricalDataSection } from './HistoricalDataSection';
import { StudentInfoSection } from './StudentInfoSection';
import { TemporaryStudentHistorySection } from './TemporaryStudentHistorySection';
import type { PredictionFormProps } from './types';

// Icons imports (some were in original file, keeping them if used in header)
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, GraduationCap, History, User } from 'lucide-react';

export function PredictionForm({
    form,
    onSubmit,
    onAnalyzeConnectedStudent,
    onLoadTemporaryStudent,
    onClearDraft,
    isLoading,
    isHealthy,
    prefilledStudentId,
    temporaryHistoryRefreshToken,
}: PredictionFormProps) {
    const [showTemporaryForm, setShowTemporaryForm] = useState(false);

    return (
        <FormProvider {...form}>
            <form onSubmit={onSubmit} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Form Header */}
                <div className="border-b pb-6">
                    <div className="flex items-center gap-3 mb-2">
                        <Database className="h-8 w-8 text-primary" />
                        <h2 className="text-3xl font-bold tracking-tight">Student Risk Analysis</h2>
                    </div>
                    <p className="text-muted-foreground text-lg">
                        Search an existing student record or open the temporary students form.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column */}
                    <div className="space-y-8">
                        <Card className="shadow-sm border-muted">
                            <CardHeader className="pb-4 border-b">
                                <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                                    <User className="h-5 w-5 text-primary" />
                                    Student Information
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-6">
                                <StudentInfoSection
                                    isAnalyzingConnectedStudent={isLoading}
                                    onAnalyzeConnectedStudent={onAnalyzeConnectedStudent}
                                    prefilledStudentId={prefilledStudentId}
                                    showTemporaryForm={showTemporaryForm}
                                    onToggleTemporaryForm={() =>
                                        setShowTemporaryForm((current) => !current)
                                    }
                                />
                            </CardContent>
                        </Card>

                        {showTemporaryForm ? (
                            <Card className="shadow-sm border-muted">
                                <CardHeader className="pb-4 border-b">
                                    <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                                        <GraduationCap className="h-5 w-5 text-primary" />
                                        Academic Performance
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="pt-6">
                                    <AcademicPerformanceSection />
                                </CardContent>
                            </Card>
                        ) : null}
                    </div>

                    {/* Right Column */}
                    <div className="space-y-8">
                        {showTemporaryForm ? (
                            <>
                                <Card className="shadow-sm border-muted">
                                    <CardHeader className="pb-4 border-b">
                                        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                                            <Activity className="h-5 w-5 text-primary" />
                                            Engagement Metrics
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="pt-6">
                                        <EngagementSection />
                                    </CardContent>
                                </Card>

                                <Card className="shadow-sm border-muted">
                                    <CardHeader className="pb-4 border-b">
                                        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                                            <History className="h-5 w-5 text-primary" />
                                            Historical Data
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="pt-6">
                                        <HistoricalDataSection />
                                    </CardContent>
                                </Card>

                                <TemporaryStudentHistorySection
                                    isLoadingPrediction={isLoading}
                                    onOpenStudent={onLoadTemporaryStudent}
                                    refreshToken={temporaryHistoryRefreshToken}
                                />
                            </>
                        ) : (
                            <Card className="border-dashed border-slate-300 bg-slate-50/70 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
                                <CardContent className="flex min-h-[220px] flex-col items-center justify-center gap-3 p-8 text-center">
                                    <div className="inline-flex rounded-full bg-indigo-100 px-2.5 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">
                                        Temporary Student Flow
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                                        Open the manual form when you need a one-off analysis
                                    </h3>
                                    <p className="max-w-md text-sm text-slate-600 dark:text-slate-400">
                                        Manual entries are stored separately in the temporary student database and do not affect searched student records.
                                    </p>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </div>

                {/* Form Footer */}
                {showTemporaryForm ? (
                    <div className="sticky bottom-0 z-10 mx-auto mt-6 flex max-w-full justify-center border-t bg-background p-4 shadow-lg -mx-6 -mb-6">
                        <div className="w-full max-w-4xl">
                            <FormActions
                                isLoading={isLoading}
                                isHealthy={isHealthy}
                                onClearDraft={onClearDraft}
                            />
                        </div>
                    </div>
                ) : null}
            </form>
        </FormProvider>
    );
}

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { GraduationCap } from 'lucide-react';
import { useFormContext } from 'react-hook-form';
import type { StudentRiskRequest } from '../../core/schemas/xai.schemas';
import { ConnectedStudentSearchSection } from './ConnectedStudentSearchSection';
import type { StudentInfoSectionProps } from './types';

export function StudentInfoSection({
    isAnalyzingConnectedStudent,
    onAnalyzeConnectedStudent,
    prefilledStudentId,
    showTemporaryForm,
    onToggleTemporaryForm,
}: StudentInfoSectionProps) {
    const { register, formState: { errors } } = useFormContext<StudentRiskRequest>();
    return (
        <div className="space-y-4">
            <ConnectedStudentSearchSection
                isAnalyzing={isAnalyzingConnectedStudent}
                onAnalyzeStudent={onAnalyzeConnectedStudent}
                prefilledStudentId={prefilledStudentId}
                showTemporaryForm={showTemporaryForm}
                onToggleTemporaryForm={onToggleTemporaryForm}
            />

            {showTemporaryForm ? (
                <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-900/70">
                    <div className="mb-3 inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                        Temporary Student Form
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label htmlFor="student_id" className="flex items-center gap-2 font-semibold">
                                <GraduationCap size={16} className="text-emerald-600 dark:text-emerald-300" />
                                Student ID
                            </Label>
                            <Input
                                id="student_id"
                                {...register('student_id')}
                                placeholder="Enter a temporary student ID"
                                className="bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary dark:bg-slate-950"
                            />
                            {errors.student_id ? <p className="text-sm text-destructive">{errors.student_id.message}</p> : null}
                            <span className="block text-sm text-muted-foreground italic">
                                Unique identifier for the temporary student record
                            </span>
                        </div>
                    </div>
                </div>
            ) : null}
        </div>
    );
}

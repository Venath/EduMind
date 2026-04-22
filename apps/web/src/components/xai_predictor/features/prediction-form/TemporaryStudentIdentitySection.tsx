import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FileSpreadsheet } from 'lucide-react';
import { useFormContext } from 'react-hook-form';
import type { StudentRiskRequest } from '../../core/schemas/xai.schemas';

export function TemporaryStudentIdentitySection() {
    const {
        register,
        formState: { errors },
    } = useFormContext<StudentRiskRequest>();

    return (
        <section className="rounded-2xl border border-slate-200 bg-background p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950/70">
            <div className="mb-3">
                <div className="mb-2 inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                    Temporary Student
                </div>
                <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-slate-50">
                    <FileSpreadsheet className="h-4 w-4 text-emerald-600 dark:text-emerald-300" />
                    Temporary Student Form
                </h2>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                    Use this form for one-off XAI analysis without loading an existing student
                    record.
                </p>
            </div>

            <div className="grid gap-1.5">
                <Label
                    htmlFor="student_id"
                    className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
                >
                    Temporary Student ID
                </Label>
                <Input
                    id="student_id"
                    {...register('student_id')}
                    placeholder="Enter a temporary student ID"
                    className="h-11 rounded-xl border-slate-300 bg-background text-sm text-slate-900 placeholder:text-slate-500 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-emerald-400 dark:focus:ring-emerald-950"
                />
                {errors.student_id ? (
                    <p className="text-sm text-destructive">{errors.student_id.message}</p>
                ) : null}
                <span className="block text-sm text-muted-foreground">
                    This ID is stored only in the temporary-student XAI flow.
                </span>
            </div>
        </section>
    );
}

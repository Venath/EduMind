import { AlertCircle, CheckCircle } from 'lucide-react';
import type { ErrorDisplayProps, LayoutProps } from './types';

/**
 * Main layout wrapper with header, theme toggle, and toast
 */
export function XAILayout({ theme, ariaAnnouncement, toast, children }: LayoutProps) {
    return (
        <div
            className={`min-h-screen bg-[radial-gradient(circle_at_8%_0%,rgba(79,70,229,0.13),transparent_38%),radial-gradient(circle_at_92%_0%,rgba(6,182,212,0.13),transparent_40%),#f1f5f9] px-4 pb-10 pt-24 text-foreground dark:bg-[radial-gradient(circle_at_8%_0%,rgba(99,102,241,0.18),transparent_38%),radial-gradient(circle_at_92%_0%,rgba(34,211,238,0.12),transparent_40%),#020617] sm:px-6 lg:px-8 ${theme}`}
        >
            {/* ARIA live region */}
            <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
                {ariaAnnouncement}
            </div>


            {/* Theme Toggle - Removed for forced light mode */}


            {/* Toast */}
            {toast.show && (
                <div
                    className={`fixed top-24 right-4 z-[100] flex items-center gap-2 rounded-lg px-6 py-3 shadow-lg ${toast.type === 'success' ? 'bg-green-600 text-white dark:bg-green-500 dark:text-slate-950' :
                        toast.type === 'error' ? 'bg-destructive text-destructive-foreground' :
                            'bg-blue-600 text-white dark:bg-blue-500 dark:text-slate-950'
                        }`}
                    role="alert"
                    aria-live="assertive"
                >
                    <CheckCircle size={18} />
                    <span className="font-medium">{toast.message}</span>
                </div>
            )}

            {/* Content */}
            <div className="mx-auto max-w-7xl space-y-4">
                {children}
            </div>
        </div>
    );
}

export function ErrorDisplay({ error }: ErrorDisplayProps) {
    if (!error) return null;

    return (
        <div
            className="mb-4 flex items-center gap-3 rounded-xl border border-red-300 bg-red-50 px-5 py-4 font-semibold text-red-700 shadow-sm dark:border-red-900 dark:bg-red-950/60 dark:text-red-300"
            role="alert"
        >
            <AlertCircle size={20} />
            {error instanceof Error ? error.message : 'An error occurred'}
        </div>
    );
}

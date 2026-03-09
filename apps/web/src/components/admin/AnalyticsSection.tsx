import { Button } from '@/components/ui/button';
import { useNavigate } from '@tanstack/react-router';
import { BarChart, BrainCircuit, Users } from 'lucide-react';

export function AnalyticsSection() {
    const navigate = useNavigate();

    return (
        <section id="analytics" className="py-20 bg-background">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl p-8 sm:p-12 text-white overflow-hidden relative">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
                    <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />

                    <div className="relative z-10 text-center space-y-8">
                        <div className="space-y-4">
                            <h2 className="text-3xl font-bold">Learning Analytics Hub</h2>
                            <p className="text-slate-300 max-w-2xl mx-auto">
                                Comprehensive insights into student performance, engagement, and learning patterns.
                                Leverage AI-driven analytics to optimize outcomes.
                            </p>
                        </div>

                        <div className="flex flex-wrap justify-center gap-4">
                            <Button
                                size="lg"
                                variant="secondary"
                                onClick={() => navigate({ to: "/learning-style" })}
                                className="h-auto py-4 px-6 flex flex-col items-center gap-2 min-w-[160px]"
                            >
                                <BrainCircuit className="w-6 h-6 text-purple-600" />
                                <span>Learning Style Predictor</span>
                            </Button>

                            <Button
                                size="lg"
                                variant="secondary"
                                onClick={() => navigate({ to: "/engagement" })}
                                className="h-auto py-4 px-6 flex flex-col items-center gap-2 min-w-[160px]"
                            >
                                <Users className="w-6 h-6 text-blue-600" />
                                <span>Engagement Tracker</span>
                            </Button>

                            <Button
                                size="lg"
                                variant="secondary"
                                onClick={() => navigate({ to: "/analytics" })}
                                className="h-auto py-4 px-6 flex flex-col items-center gap-2 min-w-[160px]"
                            >
                                <BarChart className="w-6 h-6 text-emerald-600" />
                                <span>XAI Predictor</span>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

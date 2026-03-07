import { Loader2, Sparkles } from 'lucide-react';
import { MAX_RECOMMENDATIONS, MIN_RECOMMENDATIONS } from '../../core/constants/uiConfig';

interface RecommendationsStepProps {
    topicFilter: string;
    maxRecommendations: number;
    generatedRecommendations: string[];
    recommendationsRequested: boolean;
    isGeneratingRecommendations: boolean;
    recommendationError: string | null;
    onTopicFilterChange: (value: string) => void;
    onMaxRecommendationsChange: (value: number) => void;
    onGenerateRecommendations: () => Promise<void>;
}

export function RecommendationsStep({
    topicFilter,
    maxRecommendations,
    generatedRecommendations,
    recommendationsRequested,
    isGeneratingRecommendations,
    recommendationError,
    onTopicFilterChange,
    onMaxRecommendationsChange,
    onGenerateRecommendations,
}: RecommendationsStepProps) {
    return (
        <section className="rounded-2xl border border-slate-200 bg-background dark:bg-slate-900 p-4 shadow-sm" id="step3Card">
            <div className="mb-3">
                <div className="mb-2 inline-flex rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200 px-2.5 py-1 text-xs font-semibold">Step 3</div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Personalized Recommendations</h2>
                <p className="text-sm text-slate-600 dark:text-slate-300">Adjust options, then click the button to generate recommendations from the backend.</p>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="grid gap-1.5">
                    <label htmlFor="topicFilter" className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">Topic (Optional)</label>
                    <input
                        id="topicFilter"
                        type="text"
                        className="h-11 w-full rounded-xl border border-slate-300 bg-background dark:bg-slate-900 px-3 text-sm text-slate-900 dark:text-slate-100 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                        value={topicFilter}
                        onChange={(event) => onTopicFilterChange(event.target.value)}
                        placeholder="e.g., Python Loops, Data Structures"
                    />
                </div>

                <div className="grid gap-1.5">
                    <label htmlFor="maxRecommendationsRange" className="text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">Number of Recommendations</label>
                    <div className="flex items-center gap-3">
                        <input
                            id="maxRecommendationsRange"
                            type="range"
                            min={MIN_RECOMMENDATIONS}
                            max={MAX_RECOMMENDATIONS}
                            value={maxRecommendations}
                            className="h-2 w-full cursor-pointer accent-indigo-600"
                            onChange={(event) => onMaxRecommendationsChange(Number(event.target.value))}
                        />
                        <span className="inline-flex min-w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200 px-2 py-1 text-xs font-semibold" id="sliderValue">
                            {maxRecommendations}
                        </span>
                    </div>
                </div>
            </div>

            <div className="mt-4">
                <button
                    type="button"
                    className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0"
                    onClick={() => void onGenerateRecommendations()}
                    disabled={isGeneratingRecommendations}
                >
                    {isGeneratingRecommendations ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
                    <span>{isGeneratingRecommendations ? 'Generating...' : 'Get Recommendations'}</span>
                </button>
            </div>

            <div id="recommendationsDisplay" className="mt-4">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Your Personalized Resources</h3>
                    <span className="text-xs font-semibold text-slate-600 dark:text-slate-300" id="recommendationsCount">
                        {recommendationsRequested ? `${generatedRecommendations.length} resources found` : 'Not generated yet'}
                    </span>
                </div>

                {recommendationError ? (
                    <div className="mt-3 rounded-xl border border-red-300 bg-red-50 p-3 text-sm font-medium text-red-700">
                        {recommendationError}
                    </div>
                ) : null}

                {!recommendationsRequested ? (
                    <div className="mt-3 rounded-xl border border-slate-300 bg-slate-50 dark:bg-slate-800 p-3 text-sm font-medium text-slate-700 dark:text-slate-200">
                        Move the slider or set a topic, then click <span className="font-bold">Get Recommendations</span>.
                    </div>
                ) : null}

                {recommendationsRequested && generatedRecommendations.length > 0 ? (
                    <div id="recommendationsList" className="mt-3 grid gap-2">
                        {generatedRecommendations.map((recommendation, index) => (
                            <article key={`${recommendation}-${index}`} className="flex items-start gap-2 rounded-xl border border-indigo-200 bg-indigo-50/50 dark:bg-indigo-900/50 p-3">
                                <span className="inline-grid h-6 w-6 shrink-0 place-items-center rounded-full bg-indigo-600 text-xs font-semibold text-white dark:bg-indigo-400 dark:text-indigo-900">{index + 1}</span>
                                <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-100">{recommendation}</p>
                            </article>
                        ))}
                    </div>
                ) : null}

                {recommendationsRequested && generatedRecommendations.length === 0 && !recommendationError ? (
                    <div className="mt-3 rounded-xl border border-amber-300 bg-amber-50 dark:bg-amber-900 p-3 text-sm font-medium text-amber-800 dark:text-amber-200">
                        {topicFilter.trim()
                            ? 'No recommendations matched the current topic filter. Clear the topic field and click Get Recommendations again to see all.'
                            : 'No recommendations were returned. Ensure the student has a profile and learning resources exist, then try Get Recommendations again.'}
                    </div>
                ) : null}
            </div>
        </section>
    );
}

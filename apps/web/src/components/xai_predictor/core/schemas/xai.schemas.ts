import { z } from 'zod';

/**
 * Zod Schema for Student Risk Request
 * Validates student data before sending to API
 */
export const StudentRiskRequestSchema = z.object({
    student_id: z.string().min(1, 'Student ID is required'),
    avg_grade: z.number().min(0).max(100),
    grade_consistency: z.number().min(0).max(100),
    grade_range: z.number().min(0).max(100),
    num_assessments: z.number().int().min(0),
    assessment_completion_rate: z.number().min(0).max(1),
    studied_credits: z.number().min(0),
    num_of_prev_attempts: z.number().int().min(0),
    low_performance: z.number().int().min(0).max(1),
    low_engagement: z.number().int().min(0).max(1),
    has_previous_attempts: z.number().int().min(0).max(1),
});


/**
 * Zod Schema for Risk Factor
 * Using preprocess to handle cases where API returns invalid values
 */
export const RiskFactorSchema = z.object({
    feature: z.string(),
    value: z.preprocess(
        (val) => {
            // Handle null, undefined, or non-numeric strings
            if (val === null || val === undefined || val === '') return 0;
            const num = Number(val);
            // If conversion results in NaN, default to 0
            return isNaN(num) ? 0 : num;
        },
        z.number()
    ),
    impact: z.string(),
});

export const CounterfactualChangeSchema = z.object({
    feature: z.string(),
    current_value: z.union([z.string(), z.number(), z.boolean()]),
    suggested_value: z.union([z.string(), z.number(), z.boolean()]),
    direction: z.string(),
    delta: z.number().nullable().optional(),
    rationale: z.string(),
});

export const CounterfactualExplanationSchema = z.object({
    current_outcome: z.string(),
    target_outcome: z.string(),
    achievable: z.boolean(),
    summary: z.string(),
    estimated_risk_level: z.string().nullable().optional(),
    estimated_risk_score: z.number().min(0).max(1).nullable().optional(),
    estimated_confidence: z.number().min(0).max(1).nullable().optional(),
    changes: z.array(CounterfactualChangeSchema),
});

/**
 * Zod Schema for Risk Prediction Response
 * Validates API response data and filters out invalid risk factors
 */
export const RiskPredictionResponseSchema = z.object({
    student_id: z.string(),
    risk_level: z.string(),
    risk_score: z.number().min(0).max(1),
    confidence: z.number().min(0).max(100),
    probabilities: z.object({
        Safe: z.number(),
        'Medium Risk': z.number().optional(),
        'At-Risk': z.number(),
    }),
    recommendations: z.array(z.string()),
    top_risk_factors: z.array(RiskFactorSchema).transform((factors) =>
        // Filter out any factors with value of 0 (which were NaN)
        factors.filter(f => f.value !== 0 || f.feature !== '')
    ),
    counterfactual: CounterfactualExplanationSchema.nullable().optional(),
    prediction_id: z.string(),
    timestamp: z.string(),
});

/**
 * Zod Schema for Health Response
 */
export const HealthResponseSchema = z.object({
    status: z.string(),
    service: z.string(),
    version: z.string(),
    model_loaded: z.boolean(),
    environment: z.string().optional(),
});

export const ConnectedStudentSummarySchema = z.object({
    student_id: z.string(),
    engagement_score: z.number().min(0).max(100),
    engagement_level: z.string(),
    engagement_trend: z.string().nullable().optional(),
    risk_level: z.string(),
    risk_probability: z.number().min(0).max(1).nullable().optional(),
    learning_style: z.string().nullable().optional(),
    avg_completion_rate: z.number().min(0).max(100).nullable().optional(),
    has_learning_profile: z.boolean(),
    last_updated: z.string().nullable().optional(),
});

export const ConnectedStudentSearchResponseSchema = z.object({
    query: z.string(),
    total: z.number().int().min(0),
    limit: z.number().int().min(1),
    institute_id: z.string(),
    students: z.array(ConnectedStudentSummarySchema),
});

export const TemporaryStudentSummarySchema = z.object({
    student_id: z.string(),
    avg_grade: z.number().min(0).max(100),
    latest_risk_level: z.string().nullable().optional(),
    latest_risk_score: z.number().min(0).max(1).nullable().optional(),
    latest_confidence: z.number().min(0).max(100).nullable().optional(),
    updated_at: z.string().nullable().optional(),
});

export const TemporaryStudentListResponseSchema = z.object({
    query: z.string(),
    total: z.number().int().min(0),
    limit: z.number().int().min(1),
    students: z.array(TemporaryStudentSummarySchema),
});

export const TemporaryStudentRecordSchema = z.object({
    student_id: z.string(),
    request_payload: StudentRiskRequestSchema,
    prediction: RiskPredictionResponseSchema.nullable(),
    created_at: z.string().nullable().optional(),
    updated_at: z.string().nullable().optional(),
});

export const RiskTimelinePointSchema = z.object({
    timestamp: z.string(),
    risk_level: z.string(),
    risk_score: z.number().min(0).max(1),
    confidence: z.number().min(0).max(1).nullable().optional(),
    avg_grade: z.number().min(0).max(100).nullable().optional(),
    completion_rate: z.number().min(0).max(100).nullable().optional(),
    key_driver: z.string().nullable().optional(),
});

export const RiskTimelineResponseSchema = z.object({
    student_id: z.string(),
    total_points: z.number().int().min(0),
    trend_direction: z.string(),
    timeline_basis: z.string().default('saved_history'),
    latest_risk_level: z.string().nullable().optional(),
    latest_risk_score: z.number().min(0).max(1).nullable().optional(),
    points: z.array(RiskTimelinePointSchema),
});

export const SimilarStudentCaseSchema = z.object({
    student_id: z.string(),
    similarity_score: z.number().min(0).max(1),
    risk_level: z.string(),
    risk_score: z.number().min(0).max(1),
    avg_grade: z.number().min(0).max(100),
    completion_rate: z.number().min(0).max(100),
    learning_style: z.string().nullable().optional(),
    engagement_level: z.string().nullable().optional(),
    explanation: z.string(),
});

export const RankedInterventionSchema = z.object({
    title: z.string(),
    rank: z.number().int().min(1),
    effort: z.string(),
    confidence: z.number().min(0).max(1),
    expected_risk_reduction: z.number().min(0).max(1),
    expected_new_risk_level: z.string(),
    expected_new_risk_score: z.number().min(0).max(1),
    rationale: z.string(),
    evidence: z.array(z.string()),
});

export const CohortMetricComparisonSchema = z.object({
    label: z.string(),
    student_value: z.number(),
    cohort_average: z.number(),
    percentile: z.number().min(0).max(100),
    direction: z.string(),
});

export const CohortComparisonSchema = z.object({
    cohort_size: z.number().int().min(0),
    summary: z.string(),
    average_risk_score: z.number().min(0).max(1).nullable().optional(),
    average_avg_grade: z.number().min(0).max(100).nullable().optional(),
    average_completion_rate: z.number().min(0).max(100).nullable().optional(),
    risk_percentile: z.number().min(0).max(100).nullable().optional(),
    performance_percentile: z.number().min(0).max(100).nullable().optional(),
    completion_percentile: z.number().min(0).max(100).nullable().optional(),
    metrics: z.array(CohortMetricComparisonSchema),
});

export const FairnessAlertSchema = z.object({
    severity: z.string(),
    title: z.string(),
    detail: z.string(),
});

export const FairnessDimensionCheckSchema = z.object({
    dimension: z.string(),
    current_group: z.string(),
    group_size: z.number().int().min(0),
    average_risk_score: z.number().min(0).max(1),
    cohort_average_risk_score: z.number().min(0).max(1),
    disparity_score: z.number().min(-1).max(1),
    elevated_risk_rate: z.number().min(0).max(100),
    status: z.string(),
    note: z.string(),
});

export const FairnessEvaluationSchema = z.object({
    parity_score: z.number().min(0).max(100),
    summary: z.string(),
    overall_average_risk_score: z.number().min(0).max(1),
    overall_elevated_risk_rate: z.number().min(0).max(100),
    dimensions: z.array(FairnessDimensionCheckSchema),
    alerts: z.array(FairnessAlertSchema),
});

export const StabilityFeatureSignalSchema = z.object({
    feature: z.string(),
    tested_range: z.string(),
    max_risk_shift: z.number().min(0).max(100),
    outcome_changed: z.boolean(),
    sensitivity: z.string(),
});

export const ExplanationStabilityEvaluationSchema = z.object({
    stability_score: z.number().min(0).max(100),
    consistency_rate: z.number().min(0).max(100),
    average_risk_shift: z.number().min(0).max(100),
    confidence_band: z.string(),
    summary: z.string(),
    sensitive_features: z.array(StabilityFeatureSignalSchema),
});

export const CaseOutcomeExplorerEntrySchema = z.object({
    student_id: z.string(),
    similarity_score: z.number().min(0).max(100),
    trajectory: z.string(),
    observed_outcome: z.string(),
    latest_risk_level: z.string(),
    latest_risk_score: z.number().min(0).max(1),
    learning_style: z.string().nullable().optional(),
    recommended_action: z.string().nullable().optional(),
    key_takeaway: z.string(),
});

export const CaseOutcomeExplorerSchema = z.object({
    summary: z.string(),
    cases: z.array(CaseOutcomeExplorerEntrySchema),
});

export const StudentInsightsRequestSchema = z.object({
    source: z.enum(['connected', 'temporary']),
    institute_id: z.string().optional(),
    request_payload: StudentRiskRequestSchema,
    prediction: RiskPredictionResponseSchema,
});

export const StudentInsightsResponseSchema = z.object({
    student_id: z.string(),
    source: z.enum(['connected', 'temporary']),
    similar_cases: z.array(SimilarStudentCaseSchema),
    interventions: z.array(RankedInterventionSchema),
    cohort_comparison: CohortComparisonSchema.nullable().optional(),
    fairness_evaluation: FairnessEvaluationSchema.nullable().optional(),
    explanation_stability: ExplanationStabilityEvaluationSchema.nullable().optional(),
    case_outcome_explorer: CaseOutcomeExplorerSchema.nullable().optional(),
});

/**
 * Inferred TypeScript types from Zod schemas
 * These ensure type safety across the application
 */
export type StudentRiskRequest = z.infer<typeof StudentRiskRequestSchema>;
export type RiskFactor = z.infer<typeof RiskFactorSchema>;
export type CounterfactualChange = z.infer<typeof CounterfactualChangeSchema>;
export type CounterfactualExplanation = z.infer<typeof CounterfactualExplanationSchema>;
export type RiskPredictionResponse = z.infer<typeof RiskPredictionResponseSchema>;
export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type ConnectedStudentSummary = z.infer<typeof ConnectedStudentSummarySchema>;
export type ConnectedStudentSearchResponse = z.infer<typeof ConnectedStudentSearchResponseSchema>;
export type TemporaryStudentSummary = z.infer<typeof TemporaryStudentSummarySchema>;
export type TemporaryStudentListResponse = z.infer<typeof TemporaryStudentListResponseSchema>;
export type TemporaryStudentRecord = z.infer<typeof TemporaryStudentRecordSchema>;
export type RiskTimelinePoint = z.infer<typeof RiskTimelinePointSchema>;
export type RiskTimelineResponse = z.infer<typeof RiskTimelineResponseSchema>;
export type SimilarStudentCase = z.infer<typeof SimilarStudentCaseSchema>;
export type RankedIntervention = z.infer<typeof RankedInterventionSchema>;
export type CohortMetricComparison = z.infer<typeof CohortMetricComparisonSchema>;
export type CohortComparison = z.infer<typeof CohortComparisonSchema>;
export type FairnessAlert = z.infer<typeof FairnessAlertSchema>;
export type FairnessDimensionCheck = z.infer<typeof FairnessDimensionCheckSchema>;
export type FairnessEvaluation = z.infer<typeof FairnessEvaluationSchema>;
export type StabilityFeatureSignal = z.infer<typeof StabilityFeatureSignalSchema>;
export type ExplanationStabilityEvaluation = z.infer<typeof ExplanationStabilityEvaluationSchema>;
export type CaseOutcomeExplorerEntry = z.infer<typeof CaseOutcomeExplorerEntrySchema>;
export type CaseOutcomeExplorer = z.infer<typeof CaseOutcomeExplorerSchema>;
export type StudentInsightsRequest = z.infer<typeof StudentInsightsRequestSchema>;
export type StudentInsightsResponse = z.infer<typeof StudentInsightsResponseSchema>;

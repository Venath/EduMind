import { z } from 'zod';

export const LearningStyleHealthResponseSchema = z.object({
    status: z.string(),
    message: z.string().optional(),
    service: z.string().optional(),
});

export const LearningStylePredictionApiSchema = z.object({
    student_id: z.string(),
    predicted_style: z.string(),
    confidence: z.number(),
    confidence_level: z.string().optional(),
    probabilities: z.record(z.string(), z.number()).default({}),
    days_tracked: z.number().int().nonnegative(),
    model_version: z.string().optional(),
    predicted_at: z.string(),
});

export const LearningStyleStudentSummaryApiSchema = z.object({
    student_id: z.string(),
});

export const LearningStyleStudentProfileApiSchema = z.object({
    student_id: z.string(),
    avg_completion_rate: z.number().default(0),
    days_tracked: z.number().int().nonnegative().default(0),
    preferred_difficulty: z.string().default('Medium'),
});

export const LearningStyleSystemStatsApiSchema = z.object({
    total_students: z.number().int().nonnegative(),
    total_resources: z.number().int().nonnegative(),
    total_recommendations: z.number().int().nonnegative(),
    recommendation_completion_rate: z.number().nonnegative(),
    learning_style_distribution: z.record(z.string(), z.number()).default({}),
    most_common_struggle_topics: z.array(
        z.object({
            topic: z.string(),
            count: z.number().int().nonnegative(),
        })
    ).default([]),
});

export const LearningStyleRecommendationApiSchema = z.object({
    reason: z.string().optional(),
    resource: z.object({
        title: z.string().optional(),
        topic: z.string().optional(),
    }).optional(),
});

export const LearningStyleRecommendationsApiSchema = z.array(LearningStyleRecommendationApiSchema);

export const LearningStyleGenerateRecommendationsApiSchema = z.object({
    recommendations: z.array(LearningStyleRecommendationApiSchema),
    total_recommendations: z.number().int().nonnegative(),
});

export type LearningStyleHealthResponse = z.infer<typeof LearningStyleHealthResponseSchema>;
export type LearningStylePredictionApiResponse = z.infer<typeof LearningStylePredictionApiSchema>;
export type LearningStyleStudentSummaryApiResponse = z.infer<typeof LearningStyleStudentSummaryApiSchema>;
export type LearningStyleStudentProfileApiResponse = z.infer<typeof LearningStyleStudentProfileApiSchema>;
export type LearningStyleSystemStatsApiResponse = z.infer<typeof LearningStyleSystemStatsApiSchema>;
export type LearningStyleRecommendationApiResponse = z.infer<typeof LearningStyleRecommendationApiSchema>;
export type LearningStyleGenerateRecommendationsApiResponse = z.infer<typeof LearningStyleGenerateRecommendationsApiSchema>;

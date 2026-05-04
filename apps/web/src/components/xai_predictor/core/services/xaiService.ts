/**
 * XAI Prediction Service
 * Handles all API calls to the XAI backend service with validation
 */

import type { IXAIService } from '../../data/interfaces';
import { XAIError } from '../errors/XAIError';
import {
    ConnectedStudentSearchResponseSchema,
    HealthResponseSchema,
    RiskTimelineResponseSchema,
    RiskPredictionResponseSchema,
    StudentRiskRequestSchema,
    StudentInsightsRequestSchema,
    StudentInsightsResponseSchema,
    TemporaryStudentListResponseSchema,
    TemporaryStudentRecordSchema,
    type ConnectedStudentSearchResponse,
    type HealthResponse,
    type RiskTimelineResponse,
    type RiskPredictionResponse,
    type StudentRiskRequest,
    type StudentInsightsRequest,
    type StudentInsightsResponse,
    type TemporaryStudentListResponse,
    type TemporaryStudentRecord,
} from '../schemas/xai.schemas';

const API_BASE_URL = import.meta.env.VITE_XAI_API_URL || 'http://localhost:8004';

class XAIService implements IXAIService {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Check if the service is healthy
     */
    async checkHealth(): Promise<HealthResponse> {
        try {
            const response = await fetch(`${this.baseURL}/health`);

            if (!response.ok) {
                throw new XAIError(`Health check failed: ${response.statusText}`, {
                    statusCode: response.status,
                    userMessage: 'Unable to check model health. The service may be down.',
                });
            }

            const data = await response.json();

            // Validate response with Zod
            const validatedData = HealthResponseSchema.parse(data);
            return validatedData;
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Predict academic risk for a student
     */
    async predictRisk(studentData: StudentRiskRequest): Promise<RiskPredictionResponse> {
        return this.postPrediction('/api/v1/academic-risk/predict', studentData);
    }

    /**
     * Predict academic risk for a temporary/manual student submission.
     */
    async predictTemporaryRisk(studentData: StudentRiskRequest): Promise<RiskPredictionResponse> {
        return this.postPrediction(
            '/api/v1/academic-risk/temporary-students/predict',
            studentData
        );
    }

    private async postPrediction(
        path: string,
        studentData: StudentRiskRequest
    ): Promise<RiskPredictionResponse> {
        try {
            // Validate request data with Zod
            const validatedRequest = StudentRiskRequestSchema.parse(studentData);

            console.log('XAIService - Sending request to API:', validatedRequest);

            const response = await fetch(`${this.baseURL}${path}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(validatedRequest),
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Prediction failed', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();

            // Debug logging - see raw API response
            console.log('XAIService - Raw API response:', data);
            console.log('XAIService - Raw risk_score from API:', data.risk_score);
            console.log('XAIService - risk_score type:', typeof data.risk_score);

            // Validate response with Zod
            const validatedData = RiskPredictionResponseSchema.parse(data);

            console.log('XAIService - Validated data:', validatedData);
            console.log('XAIService - Validated risk_score:', validatedData.risk_score);

            return validatedData;
        } catch (error) {
            console.error('XAIService - Error in predictRisk:', error);
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Search students available through connected backend services
     */
    async searchStudents(
        query: string,
        options?: { limit?: number; instituteId?: string }
    ): Promise<ConnectedStudentSearchResponse> {
        try {
            const params = new URLSearchParams();
            params.set('query', query);
            params.set('limit', String(options?.limit ?? 8));
            if (options?.instituteId) {
                params.set('institute_id', options.instituteId);
            }

            const response = await fetch(
                `${this.baseURL}/api/v1/academic-risk/students/search?${params.toString()}`
            );

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Student search failed', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();
            return ConnectedStudentSearchResponseSchema.parse(data);
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Build the academic-risk request for a connected student
     */
    async getConnectedStudentRequest(
        studentId: string,
        options?: { days?: number }
    ): Promise<StudentRiskRequest> {
        try {
            const params = new URLSearchParams();
            params.set('days', String(options?.days ?? 14));

            const response = await fetch(
                `${this.baseURL}/api/v1/academic-risk/students/${encodeURIComponent(studentId)}/request?${params.toString()}`
            );

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Could not build student analysis request', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();
            return StudentRiskRequestSchema.parse(data);
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * List saved temporary student records from the dedicated temp DB.
     */
    async getTemporaryStudents(options?: {
        query?: string;
        limit?: number;
    }): Promise<TemporaryStudentListResponse> {
        try {
            const params = new URLSearchParams();
            params.set('query', options?.query ?? '');
            params.set('limit', String(options?.limit ?? 8));

            const response = await fetch(
                `${this.baseURL}/api/v1/academic-risk/temporary-students?${params.toString()}`
            );

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Could not load temporary students', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();
            return TemporaryStudentListResponseSchema.parse(data);
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Get one saved temporary student record with its latest prediction.
     */
    async getTemporaryStudentRecord(studentId: string): Promise<TemporaryStudentRecord> {
        try {
            const response = await fetch(
                `${this.baseURL}/api/v1/academic-risk/temporary-students/${encodeURIComponent(studentId)}`
            );

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Could not load temporary student record', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();
            return TemporaryStudentRecordSchema.parse(data);
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Get persisted XAI risk history for one student.
     */
    async getRiskTimeline(
        studentId: string,
        options?: { limit?: number; source?: 'auto' | 'connected' | 'temporary' }
    ): Promise<RiskTimelineResponse> {
        try {
            const params = new URLSearchParams();
            params.set('limit', String(options?.limit ?? 8));
            params.set('source', options?.source ?? 'auto');

            const response = await fetch(
                `${this.baseURL}/api/v1/academic-risk/students/${encodeURIComponent(studentId)}/timeline?${params.toString()}`
            );

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Could not load student risk timeline', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();
            return RiskTimelineResponseSchema.parse(data);
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    async getStudentInsights(payload: StudentInsightsRequest): Promise<StudentInsightsResponse> {
        try {
            const validatedPayload = StudentInsightsRequestSchema.parse(payload);

            const response = await fetch(`${this.baseURL}/api/v1/academic-risk/insights`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(validatedPayload),
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Could not load integrated XAI insights', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();
            return StudentInsightsResponseSchema.parse(data);
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Batch predict for multiple students
     */
    async batchPredict(students: StudentRiskRequest[]): Promise<RiskPredictionResponse[]> {
        try {
            // Validate all student data
            const validatedStudents = students.map(student =>
                StudentRiskRequestSchema.parse(student)
            );

            const response = await fetch(`${this.baseURL}/api/v1/academic-risk/batch-predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ students: validatedStudents }),
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new XAIError(error.detail || 'Batch prediction failed', {
                    statusCode: response.status,
                    details: error,
                });
            }

            const data = await response.json();

            // Validate response array
            const validatedData = data.map((item: unknown) =>
                RiskPredictionResponseSchema.parse(item)
            );

            return validatedData;
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }

    /**
     * Get model information
     */
    async getModelInfo() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/model/info`);

            if (!response.ok) {
                throw new XAIError(`Failed to get model info: ${response.statusText}`, {
                    statusCode: response.status,
                });
            }

            return response.json();
        } catch (error) {
            if (error instanceof XAIError) {
                throw error;
            }
            throw XAIError.fromUnknown(error);
        }
    }
}

// Export singleton instance
export const xaiService = new XAIService();

// Export class for testing
export default XAIService;

// Re-export types from schemas
export type {
    ConnectedStudentSearchResponse,
    ConnectedStudentSummary,
    HealthResponse,
    RiskFactor,
    RiskPredictionResponse,
    StudentRiskRequest,
    StudentInsightsRequest,
    StudentInsightsResponse,
    TemporaryStudentListResponse,
    TemporaryStudentRecord,
    TemporaryStudentSummary,
    RiskTimelinePoint,
    RiskTimelineResponse,
} from '../schemas/xai.schemas';

/**
 * XAI Prediction Service
 * Handles all API calls to the XAI backend service
 */

const API_BASE_URL = import.meta.env.VITE_XAI_API_URL || 'http://localhost:8000';

export interface StudentRiskRequest {
    student_id: string;
    avg_grade: number;
    grade_consistency: number;
    grade_range: number;
    num_assessments: number;
    assessment_completion_rate: number;
    studied_credits: number;
    num_of_prev_attempts: number;
    low_performance: number;
    low_engagement: number;
    has_previous_attempts: number;
}

export interface RiskFactor {
    feature: string;
    value: number;
    impact: string;
}

export interface RiskPredictionResponse {
    student_id: string;
    risk_level: string;
    risk_score: number;
    confidence: number;
    probabilities: {
        Safe: number;
        'Medium Risk'?: number;
        'At-Risk': number;
    };
    recommendations: string[];
    top_risk_factors: RiskFactor[];
    prediction_id: string;
    timestamp: string;
}

export interface HealthResponse {
    status: string;
    service: string;
    version: string;
    model_loaded: boolean;
    environment?: string;
}

class XAIService {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Check if the service is healthy
     */
    async checkHealth(): Promise<HealthResponse> {
        const response = await fetch(`${this.baseURL}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.statusText}`);
        }
        return response.json();
    }

    /**
     * Predict academic risk for a student
     */
    async predictRisk(studentData: StudentRiskRequest): Promise<RiskPredictionResponse> {
        const response = await fetch(`${this.baseURL}/api/v1/academic-risk/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(studentData),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || 'Prediction failed');
        }

        return response.json();
    }

    /**
     * Batch predict for multiple students
     */
    async batchPredict(students: StudentRiskRequest[]): Promise<RiskPredictionResponse[]> {
        const response = await fetch(`${this.baseURL}/api/v1/academic-risk/batch-predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ students }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || 'Batch prediction failed');
        }

        return response.json();
    }

    /**
     * Get model information
     */
    async getModelInfo() {
        const response = await fetch(`${this.baseURL}/api/v1/model/info`);
        if (!response.ok) {
            throw new Error(`Failed to get model info: ${response.statusText}`);
        }
        return response.json();
    }
}

// Export singleton instance
export const xaiService = new XAIService();

// Export class for testing
export default XAIService;

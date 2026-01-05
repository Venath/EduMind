/**
 * Shared API types for frontend and backend communication.
 * This file can be imported by both frontend and backend to ensure type safety.
 */

// ============================================
// Common Types
// ============================================

export type RiskLevel = 'low' | 'medium' | 'high';

export type PredictionType = 'ml_model' | 'heuristic' | 'blended';

// ============================================
// Prediction API Types
// ============================================

export interface PredictionRequest {
  student_id: string;
  total_clicks?: number;
  days_active?: number;
  avg_score?: number;
  studied_credits?: number;
  num_of_prev_attempts?: number;
  previous_gpa?: number;
  entrance_score?: number;
  previous_education?: string;
  expected_weekly_hours?: number;
}

export interface PredictionResult {
  predicted_class: string;
  probability: number;
  risk_level: RiskLevel;
}

export interface FeatureContribution {
  feature: string;
  value: number;
  contribution: number;
  impact: 'positive' | 'negative';
}

export interface ExplanationResult {
  feature_contributions: FeatureContribution[];
  top_positive_factors: string[];
  top_negative_factors: string[];
  shap_values?: Record<string, number>;
  base_value?: number;
}

export interface PredictionResponse {
  prediction: PredictionResult;
  explanation: ExplanationResult;
  recommendations: string[];
}

// ============================================
// Academic Risk API Types
// ============================================

export interface AcademicRiskRequest {
  student_id: string;
  code_module?: string;
  code_presentation?: string;
  total_clicks: number;
  days_active: number;
  avg_score: number;
  studied_credits?: number;
  num_of_prev_attempts?: number;
}

export interface AcademicRiskResponse {
  student_id: string;
  risk_level: RiskLevel;
  risk_probability: number;
  confidence: number;
  prediction_details: {
    model_prediction: number;
    threshold_used: number;
  };
  feature_importance: Record<string, number>;
  risk_factors: string[];
  recommendations: string[];
  timestamp: string;
}

// ============================================
// Smart Prediction API Types
// ============================================

export interface DataQuality {
  status: 'sufficient' | 'partial' | 'insufficient';
  ml_ready: boolean;
  completeness_score: number;
  missing_for_ml: {
    clicks_needed: number;
    days_active_needed: number;
  };
  message: string;
}

export interface SmartPredictionRequest extends PredictionRequest {
  code_module?: string;
  code_presentation?: string;
  days_before_start?: number;
}

export interface SmartPredictionResponse {
  student_id: string;
  risk_level: RiskLevel;
  risk_probability: number;
  confidence: number;
  prediction_type: PredictionType;
  data_quality: DataQuality;
  risk_factors: string[];
  protective_factors: string[];
  recommendations: string[];
  feature_importance?: Record<string, number>;
  timestamp: string;
  note: string;
}

// ============================================
// User API Types
// ============================================

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'instructor' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ============================================
// Course API Types
// ============================================

export interface Course {
  id: string;
  code: string;
  name: string;
  description: string;
  credits: number;
  instructor_id: string;
  created_at: string;
}

// ============================================
// Assessment API Types
// ============================================

export interface Assessment {
  id: string;
  course_id: string;
  title: string;
  type: 'quiz' | 'assignment' | 'exam';
  max_score: number;
  due_date: string;
  created_at: string;
}

export interface StudentAssessment {
  id: string;
  student_id: string;
  assessment_id: string;
  score: number;
  submitted_at: string;
  is_late: boolean;
}

// ============================================
// Engagement API Types
// ============================================

export interface EngagementMetrics {
  student_id: string;
  total_clicks: number;
  days_active: number;
  avg_session_duration: number;
  last_login: string;
  resources_accessed: number;
}

// ============================================
// Health Check Types
// ============================================

export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  service: string;
  version?: string;
  timestamp?: string;
}

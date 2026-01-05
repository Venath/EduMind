import { useState, useEffect, useRef } from 'react';
import { xaiService, type StudentRiskRequest, type RiskPredictionResponse } from '../services/xaiService';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
} from 'chart.js';
import { 
  AlertTriangle, 
  CheckCircle, 
  Target, 
  TrendingDown, 
  TrendingUp, 
  Activity, 
  Lightbulb, 
  GraduationCap, 
  Brain,
  Users,
  BarChart,
  Clock,
  BookOpen,
  Calendar,
  ArrowUp,
  ArrowDown,
  Zap
} from 'lucide-react';
import { Bar, Doughnut, Radar } from 'react-chartjs-2';
import './XAIPrediction.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale
);

const XAIPrediction = () => {
  const [formData, setFormData] = useState<StudentRiskRequest>({
    student_id: '',
    avg_grade: 70,
    grade_consistency: 85,
    grade_range: 30,
    num_assessments: 8,
    assessment_completion_rate: 0.8,
    studied_credits: 60,
    num_of_prev_attempts: 0,
    low_performance: 0,
    low_engagement: 0,
    has_previous_attempts: 0,
  });

  const [prediction, setPrediction] = useState<RiskPredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const data = await xaiService.predictRisk(formData);
      setPrediction(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (riskScore: number): 'safe' | 'medium' | 'at-risk' => {
    if (riskScore < 40) return 'safe';
    if (riskScore < 70) return 'medium';
    return 'at-risk';
  };

  const getRiskColorFromLevel = (riskLevel: string) => {
    const levelLower = riskLevel.toLowerCase();
    if (levelLower.includes('safe')) {
      return '#43e97b'; // Green
    } else if (levelLower.includes('medium')) {
      return '#fbbf24'; // Yellow
    } else {
      return '#f5576c'; // Red
    }
  };

  const getRiskColor = (riskScore: number) => {
    const level = getRiskLevel(riskScore);
    switch (level) {
      case 'safe':
        return '#43e97b'; // Green
      case 'medium':
        return '#fbbf24'; // Yellow
      case 'at-risk':
        return '#f5576c'; // Red
      default:
        return '#667eea';
    }
  };

  const getProgressBarGradient = (riskScore: number) => {
    const level = getRiskLevel(riskScore);
    switch (level) {
      case 'safe':
        return '#22c55e'; // Solid green
      case 'medium':
        return '#f59e0b'; // Solid yellow/orange
      case 'at-risk':
        return '#ef4444'; // Solid red
      default:
        return '#667eea';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'critical':
        return '#dc2626';
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#22c55e';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="xai-prediction-container">
      <div className="xai-header">
        <h1>
          <GraduationCap className="header-icon" size={40} />
          Academic Risk Prediction
        </h1>
        <p>AI-powered early warning system for student success</p>
      </div>

      <div className="xai-content">
        {error && <div className="error-message">{error}</div>}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Analyzing student data...</p>
          </div>
        )}

        {!loading && !prediction && (
          <div className="xai-form">
            <div className="form-header">
              <div className="form-header-icon">
                <Brain size={32} />
              </div>
              <div>
                <h2>Student Risk Assessment</h2>
                <p>Complete the form below to predict academic risk level</p>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="section-title">
                <Users size={20} />
                <span>Student Information</span>
              </div>
              
              <div className="form-grid">
                <div className="form-group">
                  <label>
                    <GraduationCap size={16} />
                    Student ID
                  </label>
                  <input
                    type="text"
                    name="student_id"
                    value={formData.student_id}
                    onChange={handleInputChange}
                    required
                    placeholder="Enter student ID (e.g., student_12345)"
                  />
                </div>
              </div>

              <div className="section-title">
                <BarChart size={20} />
                <span>Academic Performance</span>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>
                    <TrendingDown size={16} />
                    Average Grade
                  </label>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      name="avg_grade"
                      value={formData.avg_grade}
                      onChange={handleInputChange}
                      min="0"
                      max="100"
                      step="0.1"
                      required
                      placeholder="0-100"
                    />
                    <span className="input-suffix">%</span>
                  </div>
                  <span className="input-hint">Current: {formData.avg_grade}%</span>
                </div>

                <div className="form-group">
                  <label>
                    <Activity size={16} />
                    Grade Consistency
                  </label>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      name="grade_consistency"
                      value={formData.grade_consistency}
                      onChange={handleInputChange}
                      min="0"
                      max="100"
                      step="0.1"
                      required
                      placeholder="0-100"
                    />
                    <span className="input-suffix">%</span>
                  </div>
                  <span className="input-hint">Performance stability score</span>
                </div>

                <div className="form-group">
                  <label>
                    <ArrowUp size={16} />
                    Grade Range
                  </label>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      name="grade_range"
                      value={formData.grade_range}
                      onChange={handleInputChange}
                      min="0"
                      max="100"
                      step="0.1"
                      required
                      placeholder="0-100"
                    />
                    <span className="input-suffix">pts</span>
                  </div>
                  <span className="input-hint">Highest - Lowest grade</span>
                </div>

                <div className="form-group">
                  <label>
                    <CheckCircle size={16} />
                    Number of Assessments
                  </label>
                  <input
                    type="number"
                    name="num_assessments"
                    value={formData.num_assessments}
                    onChange={handleInputChange}
                    min="0"
                    required
                    placeholder="Total assessments"
                  />
                  <span className="input-hint">Completed assessments</span>
                </div>
              </div>

              <div className="section-title">
                <Target size={20} />
                <span>Engagement Metrics</span>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>
                    <Clock size={16} />
                    Completion Rate
                  </label>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      name="assessment_completion_rate"
                      value={formData.assessment_completion_rate}
                      onChange={handleInputChange}
                      min="0"
                      max="1"
                      step="0.01"
                      required
                      placeholder="0.0 - 1.0"
                    />
                    <span className="input-suffix">{(formData.assessment_completion_rate * 100).toFixed(0)}%</span>
                  </div>
                  <span className="input-hint">Decimal value (0 = 0%, 1 = 100%)</span>
                </div>

                <div className="form-group">
                  <label>
                    <BookOpen size={16} />
                    Studied Credits
                  </label>
                  <input
                    type="number"
                    name="studied_credits"
                    value={formData.studied_credits}
                    onChange={handleInputChange}
                    min="0"
                    required
                    placeholder="Total credits"
                  />
                  <span className="input-hint">Course credits enrolled</span>
                </div>
              </div>

              <div className="section-title">
                <Calendar size={20} />
                <span>Historical Data</span>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>
                    <AlertTriangle size={16} />
                    Previous Attempts
                  </label>
                  <input
                    type="number"
                    name="num_of_prev_attempts"
                    value={formData.num_of_prev_attempts}
                    onChange={handleInputChange}
                    min="0"
                    required
                    placeholder="0"
                  />
                  <span className="input-hint">Number of retakes</span>
                </div>

                <div className="form-group">
                  <label>
                    <TrendingDown size={16} />
                    Low Performance Flag
                  </label>
                  <select
                    name="low_performance"
                    value={formData.low_performance}
                    onChange={(e) => setFormData(prev => ({ ...prev, low_performance: parseInt(e.target.value) }))}
                    required
                  >
                    <option value={0}>No - Grade ≥ 40%</option>
                    <option value={1}>Yes - Grade &lt; 40%</option>
                  </select>
                  <span className="input-hint">Below 40% threshold</span>
                </div>

                <div className="form-group">
                  <label>
                    <Activity size={16} />
                    Low Engagement Flag
                  </label>
                  <select
                    name="low_engagement"
                    value={formData.low_engagement}
                    onChange={(e) => setFormData(prev => ({ ...prev, low_engagement: parseInt(e.target.value) }))}
                    required
                  >
                    <option value={0}>No - Active participation</option>
                    <option value={1}>Yes - Limited participation</option>
                  </select>
                  <span className="input-hint">Low assessment completion</span>
                </div>

                <div className="form-group">
                  <label>
                    <Clock size={16} />
                    Has Previous Attempts
                  </label>
                  <select
                    name="has_previous_attempts"
                    value={formData.has_previous_attempts}
                    onChange={(e) => setFormData(prev => ({ ...prev, has_previous_attempts: parseInt(e.target.value) }))}
                    required
                  >
                    <option value={0}>No - First attempt</option>
                    <option value={1}>Yes - Has retaken courses</option>
                  </select>
                  <span className="input-hint">Failed courses previously</span>
                </div>
              </div>

              <button type="submit" className="submit-button" disabled={loading}>
                <Brain size={20} />
                {loading ? 'Analyzing Student Data...' : 'Predict Academic Risk'}
              </button>
            </form>
          </div>
        )}

        {prediction && (
          <div className="results-container">
            <div className="result-header">
              <span
                className={`risk-badge ${
                  prediction.risk_level === 'At-Risk' 
                    ? 'risk-at-risk' 
                    : prediction.risk_level === 'Medium Risk'
                    ? 'risk-medium'
                    : 'risk-safe'
                }`}
              >
                {prediction.risk_level}
              </span>
            </div>

            <div className="risk-score-section">
              <div className="risk-gauge">
                <Doughnut
                  data={{
                    labels: ['Risk Score', 'Safe Zone'],
                    datasets: [
                      {
                        data: [prediction.risk_score * 100, 100 - prediction.risk_score * 100],
                        backgroundColor: [
                          getRiskColorFromLevel(prediction.risk_level),
                          'rgba(255, 255, 255, 0.05)',
                        ],
                        borderWidth: 0,
                      },
                    ],
                  }}
                  options={{
                    cutout: '75%',
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: { display: false },
                      tooltip: { enabled: false },
                    },
                  }}
                />
                <div className="risk-gauge-overlay">
                  <div className="risk-gauge-value">
                    {(prediction.risk_score * 100).toFixed(0)}%
                  </div>
                  <div className="risk-gauge-label">Risk Score</div>
                </div>
              </div>
            </div>

            <div className="probabilities">
              <h3>Prediction Probabilities</h3>
              {Object.entries(prediction.probabilities).map(([key, value]) => {
                const keyLower = key.toLowerCase();
                let riskValue: number;
                if (keyLower.includes('safe')) {
                  riskValue = 20; // Green
                } else if (keyLower.includes('medium')) {
                  riskValue = 55; // Yellow
                } else {
                  riskValue = 85; // Red
                }
                
                return (
                  <div key={key} className="probability-item">
                    <div className="probability-label">
                      <span>{key}</span>
                      <span>{(value * 100).toFixed(1)}%</span>
                    </div>
                    <div className="probability-bar-container">
                      <div
                        className="probability-bar-modern"
                        style={{
                          width: `${value * 100}%`,
                          background: getProgressBarGradient(riskValue),
                        }}
                      >
                        <span className="probability-value">{(value * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="recommendations">
              <div className="section-header-modern">
                <div className="section-header-content">
                  <Lightbulb className="section-icon-large" size={32} />
                  <div>
                    <h3>Personalized Action Plan</h3>
                    <p className="section-subtitle">Follow these evidence-based recommendations to improve academic performance</p>
                  </div>
                </div>
                <div className="plan-progress">
                  <span className="progress-text">{prediction.recommendations.length} Action Items</span>
                </div>
              </div>

              <div className="action-plan-timeline">
                {prediction.recommendations.map((rec, idx) => {
                  const getPriorityLevel = (index: number) => {
                    if (index < 2) return { level: 'Critical', color: '#ef4444', icon: <Zap size={18} /> };
                    if (index < 4) return { level: 'High', color: '#f59e0b', icon: <AlertTriangle size={18} /> };
                    if (index < 6) return { level: 'Medium', color: '#3b82f6', icon: <Clock size={18} /> };
                    return { level: 'Standard', color: '#22c55e', icon: <CheckCircle size={18} /> };
                  };

                  const getCategoryIcon = (index: number) => {
                    const icons = [<BookOpen size={20} />, <Users size={20} />, <Calendar size={20} />, <Target size={20} />];
                    return icons[index % icons.length];
                  };

                  const priority = getPriorityLevel(idx);

                  return (
                    <div key={idx} className="action-item-wrapper">
                      <div className="action-item-timeline">
                        <div className="timeline-dot" style={{ background: priority.color }}>
                          <span className="step-number">{idx + 1}</span>
                        </div>
                        {idx < prediction.recommendations.length - 1 && <div className="timeline-line" />}
                      </div>
                      
                      <div className="action-item-card">
                        <div className="action-card-header">
                          <div className="action-category">
                            <div className="category-icon" style={{ background: `${priority.color}15`, color: priority.color }}>
                              {getCategoryIcon(idx)}
                            </div>
                            <span className="category-label">Step {idx + 1}</span>
                          </div>
                          <div className="priority-badge" style={{ background: `${priority.color}20`, color: priority.color, borderColor: `${priority.color}40` }}>
                            {priority.icon}
                            <span>{priority.level}</span>
                          </div>
                        </div>
                        
                        <div className="action-card-body">
                          <p className="action-description">{rec}</p>
                        </div>
                        
                        <div className="action-card-footer">
                          <button className="action-btn-complete">
                            <CheckCircle size={16} />
                            <span>Mark Complete</span>
                          </button>
                          <div className="action-meta">
                            <Clock size={14} />
                            <span>Track Progress</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="action-plan-summary">
                <div className="summary-card">
                  <AlertTriangle size={20} />
                  <span><strong>{prediction.recommendations.filter((_, i) => i < 2).length}</strong> Critical Actions</span>
                </div>
                <div className="summary-card">
                  <Clock size={20} />
                  <span><strong>{prediction.recommendations.filter((_, i) => i >= 2 && i < 4).length}</strong> High Priority</span>
                </div>
                <div className="summary-card">
                  <Target size={20} />
                  <span><strong>{prediction.recommendations.filter((_, i) => i >= 4).length}</strong> Standard Tasks</span>
                </div>
              </div>
            </div>

            <div className="risk-factors">
              <div className="section-header-modern">
                <div className="section-header-content">
                  <Target className="section-icon-large" size={32} />
                  <div>
                    <h3>Key Risk Indicators</h3>
                    <p className="section-subtitle">Critical factors affecting academic performance with actionable insights</p>
                  </div>
                </div>
                <div className="plan-progress">
                  <span className="progress-text">{prediction.top_risk_factors.length} Factors Identified</span>
                </div>
              </div>

              <div className="risk-factors-grid">
                {prediction.top_risk_factors.map((factor, idx) => {
                  const getImpactIcon = (impact: string) => {
                    switch (impact.toLowerCase()) {
                      case 'critical':
                        return <AlertTriangle size={24} />;
                      case 'high':
                        return <AlertTriangle size={24} />;
                      case 'medium':
                        return <TrendingDown size={24} />;
                      case 'low':
                        return <Activity size={24} />;
                      case 'strength':
                        return <CheckCircle size={24} />;
                      case 'neutral':
                        return <Activity size={24} />;
                      default:
                        return <Activity size={24} />;
                    }
                  };
                  
                  const getImpactColor = (impact: string) => {
                    switch (impact.toLowerCase()) {
                      case 'critical':
                        return '#dc2626';
                      case 'high':
                        return '#ef4444';
                      case 'medium':
                        return '#f59e0b';
                      case 'low':
                        return '#3b82f6';
                      case 'strength':
                        return '#22c55e';
                      case 'neutral':
                        return '#64748b';
                      default:
                        return '#3b82f6';
                    }
                  };

                  const getImpactLabel = (impact: string) => {
                    switch (impact.toLowerCase()) {
                      case 'critical':
                        return 'Critical';
                      case 'high':
                        return 'High Risk';
                      case 'medium':
                        return 'Medium Risk';
                      case 'low':
                        return 'Monitor';
                      case 'strength':
                        return 'Strength';
                      case 'neutral':
                        return 'Baseline';
                      default:
                        return impact;
                    }
                  };

                  // Calculate benchmark comparison
                  const getBenchmark = (feature: string, value: number) => {
                    const benchmarks: Record<string, number> = {
                      'avg_grade': 70,
                      'grade_consistency': 85,
                      'assessment_completion_rate': 0.75,
                      'num_assessments': 8,
                      'low_engagement': 0,
                      'low_performance': 0
                    };
                    return benchmarks[feature] || 50;
                  };

                  const getRecommendation = (feature: string, impact: string) => {
                    // For strengths, show maintenance advice
                    if (impact.toLowerCase() === 'strength') {
                      const strengthAdvice: Record<string, string> = {
                        'avg_grade': 'Excellent academic performance! Keep up the consistent study habits',
                        'grade_consistency': 'Outstanding consistency! Continue your effective learning approach',
                        'assessment_completion_rate': 'Great work ethic! Maintain this dedication to complete all tasks',
                        'num_assessments': 'Strong engagement! Keep actively participating in assessments',
                        'engagement_level': 'Excellent engagement! Your active participation is a key strength'
                      };
                      return strengthAdvice[feature] || 'Maintain this positive performance';
                    }

                    // For risks, show improvement advice
                    const recommendations: Record<string, string> = {
                      'low_engagement': 'Increase participation in discussions, attend office hours, join study groups',
                      'num_assessments': 'Complete all assignments on time, use practice quizzes, seek extra credit',
                      'assessment_completion_rate': 'Set reminders, create a study schedule, prioritize deadlines',
                      'avg_grade': 'Focus on weak subjects, get tutoring, review feedback regularly',
                      'grade_consistency': 'Maintain steady study habits, avoid cramming, balance workload',
                      'studied_credits': 'Consider course load adjustment, balance difficulty levels',
                      'low_performance': 'Identify struggling areas, attend workshops, use learning resources',
                      'previous_attempts': 'Learn from past mistakes, use different study strategies, seek mentoring'
                    };
                    return recommendations[feature] || 'Focus on improving this area for better outcomes';
                  };

                  const numValue = typeof factor.value === 'number' ? factor.value : parseFloat(String(factor.value)) || 0;
                  const benchmark = getBenchmark(factor.feature, numValue);
                  const percentage = Math.min(100, Math.max(0, (numValue / (benchmark * 1.5)) * 100));
                  const isAboveBenchmark = numValue >= benchmark;

                  return (
                    <div key={idx} className="risk-factor-card-enhanced">
                      <div className="risk-card-header">
                        <div className="risk-factor-icon" style={{ color: getImpactColor(factor.impact) }}>
                          {getImpactIcon(factor.impact)}
                        </div>
                        <div className="risk-header-content">
                          <h4 className="risk-factor-name-modern">
                            {factor.feature.replace(/_/g, ' ').split(' ').map(word => 
                              word.charAt(0).toUpperCase() + word.slice(1)
                            ).join(' ')}
                          </h4>
                          <div className="risk-rank-badge">
                            #{idx + 1} {factor.impact.toLowerCase() === 'strength' ? 'Key Strength' : 'Risk Factor'}
                          </div>
                        </div>
                        <div className="impact-badge" style={{ background: `${getImpactColor(factor.impact)}20`, color: getImpactColor(factor.impact), borderColor: `${getImpactColor(factor.impact)}40` }}>
                          {getImpactLabel(factor.impact)}
                        </div>
                      </div>

                      <div className="risk-card-body">
                        <div className="risk-metrics-row">
                          <div className="risk-metric-large">
                            <span className="metric-label">Current Value</span>
                            <span className="metric-value-large">{typeof factor.value === 'number' ? factor.value.toFixed(2) : factor.value}</span>
                          </div>
                          <div className="risk-metric-large">
                            <span className="metric-label">Benchmark</span>
                            <span className="metric-value-large benchmark-value">{benchmark.toFixed(2)}</span>
                          </div>
                          <div className="risk-metric-large">
                            <span className="metric-label">Status</span>
                            <div className="status-indicator" style={{ color: isAboveBenchmark ? '#22c55e' : '#ef4444' }}>
                              {isAboveBenchmark ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                              <span>{isAboveBenchmark ? 'Above' : 'Below'}</span>
                            </div>
                          </div>
                        </div>

                        <div className="progress-bar-container">
                          <div className="progress-bar-header">
                            <span className="progress-label">Performance Level</span>
                            <span className="progress-percentage">{percentage.toFixed(0)}%</span>
                          </div>
                          <div className="progress-bar-track">
                            <div 
                              className="progress-bar-fill" 
                              style={{ 
                                width: `${percentage}%`,
                                background: `linear-gradient(90deg, ${getImpactColor(factor.impact)}cc, ${getImpactColor(factor.impact)})`
                              }}
                            />
                            <div className="benchmark-marker" style={{ left: '66.67%' }}>
                              <div className="marker-line" />
                              <span className="marker-label">Target</span>
                            </div>
                          </div>
                        </div>

                        <div className="risk-recommendation">
                          <div className="recommendation-header">
                            <Lightbulb size={16} />
                            <span>{factor.impact.toLowerCase() === 'strength' ? 'Strength Maintenance' : 'Action Required'}</span>
                          </div>
                          <p>{getRecommendation(factor.feature, factor.impact)}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Analytics Dashboard Section */}
            <div className="charts-dashboard">
              <h3>Analytics Dashboard</h3>
              
              <div className="charts-grid-large">
                {/* Probability Distribution Chart */}
                <div className="chart-card-large">
                  <h4>Risk Probability Distribution</h4>
                  <div className="chart-container-tall">
                    <Bar
                      data={{
                        labels: Object.keys(prediction.probabilities),
                        datasets: [
                          {
                            label: 'Probability (%)',
                            data: Object.values(prediction.probabilities).map(v => v * 100),
                            backgroundColor: [
                              '#22c55e',
                              '#f59e0b',
                              '#ef4444',
                            ],
                            borderRadius: 12,
                            barThickness: 60,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { display: false },
                          tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            padding: 16,
                            titleFont: { size: 14 },
                            bodyFont: { size: 13 },
                            callbacks: {
                              label: (context) => `${context.parsed.y.toFixed(1)}%`,
                            },
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { 
                              color: 'rgba(255, 255, 255, 0.1)',
                              lineWidth: 1,
                            },
                            ticks: { 
                              color: '#a0aec0',
                              font: { size: 12 },
                              callback: (value) => value + '%',
                            },
                          },
                          x: {
                            grid: { display: false },
                            ticks: { 
                              color: '#fff',
                              font: { size: 13, weight: '600' },
                            },
                          },
                        },
                      }}
                    />
                  </div>
                </div>

                {/* Student Metrics Comparison */}
                <div className="chart-card-large">
                  <h4>Student Performance Metrics</h4>
                  <div className="chart-container-tall">
                    <Bar
                      data={{
                        labels: [
                          'Grade',
                          'Consistency',
                          'Completion',
                          'Assessments',
                        ],
                        datasets: [
                          {
                            label: 'Current Student',
                            data: [
                              formData.avg_grade,
                              formData.grade_consistency,
                              formData.assessment_completion_rate * 100,
                              (formData.num_assessments / 15) * 100, // Normalized to 100
                            ],
                            backgroundColor: getRiskColor(prediction.risk_score * 100),
                            borderRadius: 12,
                            barThickness: 40,
                          },
                          {
                            label: 'Safe Threshold',
                            data: [70, 85, 75, 60],
                            backgroundColor: 'rgba(34, 197, 94, 0.3)',
                            borderRadius: 12,
                            barThickness: 40,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: true,
                            position: 'top',
                            labels: {
                              color: '#fff',
                              padding: 15,
                              font: { size: 12 },
                            },
                          },
                          tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            padding: 16,
                            callbacks: {
                              label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(1)}`,
                            },
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { 
                              color: 'rgba(255, 255, 255, 0.1)',
                            },
                            ticks: { 
                              color: '#a0aec0',
                              font: { size: 12 },
                            },
                          },
                          x: {
                            grid: { display: false },
                            ticks: { 
                              color: '#fff',
                              font: { size: 12 },
                            },
                          },
                        },
                      }}
                    />
                  </div>
                </div>

                {/* Risk Gauge Visualization */}
                <div className="chart-card-large">
                  <h4>Risk Score Breakdown</h4>
                  <div className="chart-container-doughnut">
                    <Doughnut
                      data={{
                        labels: Object.keys(prediction.probabilities),
                        datasets: [
                          {
                            data: Object.values(prediction.probabilities).map(v => v * 100),
                            backgroundColor: [
                              '#22c55e',
                              '#f59e0b',
                              '#ef4444',
                            ],
                            borderWidth: 4,
                            borderColor: '#1a1a2e',
                            hoverOffset: 8,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                              color: '#fff',
                              padding: 20,
                              font: { size: 13 },
                              generateLabels: (chart) => {
                                const data = chart.data;
                                if (data.labels && data.datasets[0].data) {
                                  return data.labels.map((label, i) => ({
                                    text: `${label}: ${(data.datasets[0].data[i] as number).toFixed(1)}%`,
                                    fillStyle: data.datasets[0].backgroundColor?.[i] as string,
                                    hidden: false,
                                    index: i,
                                  }));
                                }
                                return [];
                              },
                            },
                          },
                          tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            padding: 16,
                            callbacks: {
                              label: (context) => `${context.label}: ${context.parsed.toFixed(1)}%`,
                            },
                          },
                        },
                      }}
                    />
                  </div>
                </div>

                {/* Feature Importance Radar */}
                <div className="chart-card-large">
                  <h4>Performance Profile</h4>
                  <div className="chart-container-radar">
                    <Radar
                      data={{
                        labels: [
                          'Grade',
                          'Consistency',
                          'Completion',
                          'Assessments',
                          'Credits',
                        ],
                        datasets: [
                          {
                            label: 'Student Profile',
                            data: [
                              formData.avg_grade,
                              formData.grade_consistency,
                              formData.assessment_completion_rate * 100,
                              (formData.num_assessments / 15) * 100,
                              (formData.studied_credits / 120) * 100,
                            ],
                            backgroundColor: `${getRiskColor(prediction.risk_score * 100)}30`,
                            borderColor: getRiskColor(prediction.risk_score * 100),
                            borderWidth: 3,
                            pointBackgroundColor: getRiskColor(prediction.risk_score * 100),
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                          },
                          {
                            label: 'Safe Threshold',
                            data: [70, 85, 75, 60, 50],
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            borderColor: '#22c55e',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            pointBackgroundColor: '#22c55e',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 4,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: true,
                            position: 'top',
                            labels: {
                              color: '#fff',
                              padding: 15,
                              font: { size: 12 },
                            },
                          },
                          tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            padding: 16,
                          },
                        },
                        scales: {
                          r: {
                            beginAtZero: true,
                            max: 100,
                            grid: { 
                              color: 'rgba(255, 255, 255, 0.15)',
                              lineWidth: 1,
                            },
                            angleLines: { 
                              color: 'rgba(255, 255, 255, 0.15)',
                              lineWidth: 1,
                            },
                            ticks: { 
                              color: '#a0aec0',
                              backdropColor: 'transparent',
                              font: { size: 11 },
                              stepSize: 20,
                            },
                            pointLabels: { 
                              color: '#fff',
                              font: { size: 13, weight: '600' },
                            },
                          },
                        },
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default XAIPrediction;

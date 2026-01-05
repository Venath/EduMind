import {
    ArcElement,
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    RadialLinearScale,
    Title,
    Tooltip,
} from 'chart.js';
import {
    Activity,
    AlertCircle,
    AlertTriangle,
    ArrowDown,
    ArrowUp,
    Award,
    BarChart,
    BookOpen,
    Brain,
    Calendar,
    CheckCircle,
    Circle,
    Clock,
    Copy,
    Download,
    ExternalLink,
    Filter,
    GraduationCap,
    Image,
    Lightbulb,
    Mail,
    MessageCircle,
    Moon,
    Printer,
    QrCode,
    Save,
    Search,
    Settings,
    Share2,
    Sliders,
    Sun,
    Target,
    Target as TargetIcon,
    TrendingDown,
    Users,
    X,
    Zap
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Bar, Doughnut, Radar } from 'react-chartjs-2';
import { xaiService, type RiskPredictionResponse, type StudentRiskRequest } from '../services/xaiService';
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

interface ActionItem {
    id: string;
    title: string;
    description: string;
    priority: 'critical' | 'high' | 'medium' | 'standard';
    category: 'academic' | 'engagement' | 'time-management' | 'support';
    isCompleted: boolean;
    isCustom?: boolean;
}

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
    const [actionPlan, setActionPlan] = useState<ActionItem[]>([]);
    const [showCustomizeModal, setShowCustomizeModal] = useState(false);
    const [showShareModal, setShowShareModal] = useState(false);
    const [showWhatIfModal, setShowWhatIfModal] = useState(false);
    const [shareLink, setShareLink] = useState('');
    const [theme, setTheme] = useState<'dark' | 'light'>('dark');
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [filterCategory, setFilterCategory] = useState<string>('all');
    const [filterPriority, setFilterPriority] = useState<string>('all');
    const [whatIfData, setWhatIfData] = useState<StudentRiskRequest | null>(null);
    const [whatIfPrediction, setWhatIfPrediction] = useState<RiskPredictionResponse | null>(null);
    const [newActionItem, setNewActionItem] = useState({
        title: '',
        description: '',
        priority: 'standard' as const,
        category: 'academic' as const
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'number' ? parseFloat(value) : value,
        }));
    };

    const generateActionPlan = (riskLevel: string): ActionItem[] => {
        if (riskLevel === 'Safe') {
            return [
                { id: '1', title: 'Maintain Excellence', description: 'Continue your current study habits and maintain consistent performance across all modules', priority: 'standard', category: 'academic', isCompleted: false },
                { id: '2', title: 'Peer Mentoring', description: 'Share your success strategies with struggling peers through study groups or tutoring', priority: 'medium', category: 'engagement', isCompleted: false },
                { id: '3', title: 'Advanced Challenges', description: 'Explore additional learning materials, research papers, and advanced topics in your field', priority: 'standard', category: 'academic', isCompleted: false },
                { id: '4', title: 'Leadership Opportunities', description: 'Take on leadership roles in group projects, class presentations, and student organizations', priority: 'medium', category: 'engagement', isCompleted: false },
                { id: '5', title: 'Aim for Distinction', description: 'Set goals to achieve distinction-level grades (80%+) in all remaining modules', priority: 'high', category: 'academic', isCompleted: false },
                { id: '6', title: 'Build Your Portfolio', description: 'Work on side projects, research, or internships to enhance your academic portfolio', priority: 'medium', category: 'engagement', isCompleted: false }
            ];
        } else if (riskLevel === 'Medium Risk') {
            return [
                { id: '1', title: 'Weekly Academic Check-ins', description: 'Schedule weekly meetings with your tutor to review progress and address concerns immediately', priority: 'high', category: 'support', isCompleted: false },
                { id: '2', title: 'Structured Study Schedule', description: 'Create and follow a daily study timetable with specific goals for each 2-hour session', priority: 'high', category: 'time-management', isCompleted: false },
                { id: '3', title: 'Join Study Groups', description: 'Participate in peer study groups 2-3 times per week for collaborative learning and support', priority: 'medium', category: 'engagement', isCompleted: false },
                { id: '4', title: 'Complete All Assessments', description: 'Prioritize completing all assignments on time, even if perfection isn\'t possible initially', priority: 'critical', category: 'academic', isCompleted: false },
                { id: '5', title: 'Improve Weak Areas', description: 'Identify subjects where you scored below 60% and dedicate 3+ hours weekly to improvement', priority: 'high', category: 'academic', isCompleted: false },
                { id: '6', title: 'Use Learning Resources', description: 'Access library resources, online tutorials, academic workshops, and supplementary materials', priority: 'medium', category: 'academic', isCompleted: false },
                { id: '7', title: 'Active Class Participation', description: 'Attend all classes, ask questions, and engage actively with course materials and discussions', priority: 'high', category: 'engagement', isCompleted: false }
            ];
        } else {
            return [
                { id: '1', title: 'URGENT: Emergency Academic Advisor Meeting', description: 'Schedule immediate meeting with academic advisor to create a comprehensive intervention plan', priority: 'critical', category: 'support', isCompleted: false },
                { id: '2', title: 'Intensive Tutoring Sessions', description: 'Attend mandatory tutoring sessions 3-4 times per week for all struggling subjects', priority: 'critical', category: 'support', isCompleted: false },
                { id: '3', title: 'Daily Study Commitment', description: 'Dedicate minimum 3-4 hours daily to focused study with regular 10-minute breaks', priority: 'critical', category: 'time-management', isCompleted: false },
                { id: '4', title: 'Complete Overdue Work', description: 'Immediately prioritize and complete all missing or late assignments - negotiate extensions if needed', priority: 'critical', category: 'academic', isCompleted: false },
                { id: '5', title: 'Attend All Classes', description: 'Ensure 100% attendance in all lectures, labs, tutorials, and mandatory sessions', priority: 'critical', category: 'engagement', isCompleted: false },
                { id: '6', title: 'Academic Skills Workshop', description: 'Enroll in academic skills workshops for time management, study techniques, exam preparation', priority: 'high', category: 'support', isCompleted: false },
                { id: '7', title: 'Weekly Progress Reports', description: 'Submit weekly progress reports to your academic advisor showing all completed work and improvements', priority: 'high', category: 'academic', isCompleted: false },
                { id: '8', title: 'Seek Counseling Support', description: 'If personal issues are affecting studies, schedule counseling sessions immediately', priority: 'medium', category: 'support', isCompleted: false },
                { id: '9', title: 'Create Recovery Plan', description: 'Work with advisor to create detailed recovery plan with specific grades needed to pass', priority: 'critical', category: 'academic', isCompleted: false }
            ];
        }
    };

    const toggleActionComplete = (id: string) => {
        setActionPlan(prev =>
            prev.map(item =>
                item.id === id ? { ...item, isCompleted: !item.isCompleted } : item
            )
        );
    };

    const deleteActionItem = (id: string) => {
        setActionPlan(prev => prev.filter(item => item.id !== id));
    };

    const addCustomAction = () => {
        if (newActionItem.title.trim()) {
            const customAction: ActionItem = {
                id: Date.now().toString(),
                ...newActionItem,
                isCompleted: false,
                isCustom: true
            };
            setActionPlan(prev => [...prev, customAction]);
            setNewActionItem({
                title: '',
                description: '',
                priority: 'standard',
                category: 'academic'
            });
            setShowCustomizeModal(false);
        }
    };

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'academic': return BookOpen;
            case 'engagement': return Users;
            case 'time-management': return Calendar;
            case 'support': return Target;
            default: return BookOpen;
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'critical': return '#ef4444';
            case 'high': return '#f59e0b';
            case 'medium': return '#3b82f6';
            default: return '#22c55e';
        }
    };

    const showToastMessage = (message: string) => {
        setToastMessage(message);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
    };

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
        showToastMessage(`Switched to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    };

    const exportToPDF = () => {
        if (!prediction) return;

        // Create printable version
        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Academic Risk Report - ${formData.student_id}</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: Arial, sans-serif; padding: 40px; color: #333; }
          .header { text-align: center; margin-bottom: 40px; border-bottom: 3px solid #667eea; padding-bottom: 20px; }
          .header h1 { color: #667eea; font-size: 28px; margin-bottom: 10px; }
          .risk-badge { display: inline-block; padding: 10px 20px; border-radius: 8px; font-weight: bold; margin: 20px 0; }
          .risk-safe { background: #d1fae5; color: #065f46; }
          .risk-medium { background: #fef3c7; color: #92400e; }
          .risk-high { background: #fee2e2; color: #991b1b; }
          .section { margin: 30px 0; }
          .section h2 { color: #667eea; margin-bottom: 15px; font-size: 20px; }
          .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
          .info-item { background: #f3f4f6; padding: 15px; border-radius: 8px; }
          .info-label { font-weight: bold; color: #4b5563; font-size: 12px; margin-bottom: 5px; }
          .info-value { font-size: 18px; color: #111827; }
          .action-item { background: #f9fafb; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }
          .action-title { font-weight: bold; margin-bottom: 5px; }
          .priority { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 10px; }
          .priority-critical { background: #fee2e2; color: #991b1b; }
          .priority-high { background: #fef3c7; color: #92400e; }
          .priority-medium { background: #dbeafe; color: #1e40af; }
          .priority-standard { background: #d1fae5; color: #065f46; }
          .footer { margin-top: 50px; text-align: center; color: #6b7280; font-size: 12px; border-top: 1px solid #e5e7eb; padding-top: 20px; }
          @media print { body { padding: 20px; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>🎓 Academic Risk Assessment Report</h1>
          <p>Student ID: <strong>${formData.student_id}</strong></p>
          <p>Generated: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}</p>
        </div>
        
        <div class="section">
          <h2>Risk Assessment</h2>
          <div class="risk-badge risk-${prediction.risk_level === 'Safe' ? 'safe' : prediction.risk_level === 'Medium Risk' ? 'medium' : 'high'}">
            ${prediction.risk_level} - ${prediction.confidence.toFixed(2)}% Confidence
          </div>
          <p><strong>Risk Score:</strong> ${prediction.risk_score.toFixed(2)}%</p>
        </div>

        <div class="section">
          <h2>Student Metrics</h2>
          <div class="info-grid">
            <div class="info-item"><div class="info-label">Average Grade</div><div class="info-value">${formData.avg_grade}%</div></div>
            <div class="info-item"><div class="info-label">Grade Consistency</div><div class="info-value">${formData.grade_consistency}%</div></div>
            <div class="info-item"><div class="info-label">Assessments Completed</div><div class="info-value">${formData.num_assessments}</div></div>
            <div class="info-item"><div class="info-label">Completion Rate</div><div class="info-value">${(formData.assessment_completion_rate * 100).toFixed(0)}%</div></div>
            <div class="info-item"><div class="info-label">Credits Studied</div><div class="info-value">${formData.studied_credits}</div></div>
            <div class="info-item"><div class="info-label">Previous Attempts</div><div class="info-value">${formData.num_of_prev_attempts}</div></div>
          </div>
        </div>

        <div class="section">
          <h2>Personalized Action Plan (${actionPlan.length} items)</h2>
          ${actionPlan.map((action, idx) => `
            <div class="action-item">
              <div class="action-title">
                <span class="priority priority-${action.priority}">${action.priority.toUpperCase()}</span>
                ${idx + 1}. ${action.title}
              </div>
              <p>${action.description}</p>
              <small style="color: #6b7280;">Category: ${action.category.replace('-', ' ')}</small>
            </div>
          `).join('')}
        </div>

        <div class="footer">
          <p><strong>EduMind Academic Risk Prediction System</strong></p>
          <p>Powered by XGBoost ML Model | Generated on ${new Date().toLocaleDateString()}</p>
        </div>
      </body>
      </html>
    `);

        printWindow.document.close();
        setTimeout(() => {
            printWindow.print();
            showToastMessage('Report ready to save as PDF');
        }, 250);
    };

    const handlePrint = () => {
        exportToPDF();
    };

    const handleShare = () => {
        if (!prediction) return;

        const data = {
            studentId: formData.student_id,
            riskLevel: prediction.risk_level,
            riskScore: prediction.risk_score,
            confidence: prediction.confidence,
            timestamp: new Date().toISOString()
        };

        const encoded = btoa(JSON.stringify(data));
        const link = `${window.location.origin}${window.location.pathname}?share=${encoded}`;
        setShareLink(link);
        setShowShareModal(true);
    };

    const copyToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(shareLink);
            showToastMessage('Link copied to clipboard!');
        } catch (err) {
            showToastMessage('Failed to copy link');
        }
    };

    const downloadQRCode = () => {
        showToastMessage('QR Code downloaded!');
    };

    // New Features Functions

    // Filter actions based on search and filters
    const getFilteredActions = () => {
        return actionPlan.filter(action => {
            const matchesSearch = action.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                action.description.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesCategory = filterCategory === 'all' || action.category === filterCategory;
            const matchesPriority = filterPriority === 'all' || action.priority === filterPriority;
            return matchesSearch && matchesCategory && matchesPriority;
        });
    };

    // Calculate progress percentage
    const getProgressPercentage = () => {
        if (actionPlan.length === 0) return 0;
        return Math.round((actionPlan.filter(a => a.isCompleted).length / actionPlan.length) * 100);
    };

    // Auto-save form data
    const saveFormDraft = () => {
        localStorage.setItem('xai_form_draft', JSON.stringify(formData));
        showToastMessage('Draft saved automatically');
    };

    // Load saved draft
    const loadFormDraft = () => {
        const saved = localStorage.getItem('xai_form_draft');
        if (saved) {
            setFormData(JSON.parse(saved));
            showToastMessage('Draft loaded');
        }
    };

    // Clear draft
    const clearDraft = () => {
        localStorage.removeItem('xai_form_draft');
        showToastMessage('Draft cleared');
    };

    // Screenshot export
    const exportAsImage = () => {
        showToastMessage('Screenshot feature coming soon! Use browser screenshot for now.');
        // In production, use html2canvas library
    };

    // What-If Simulator
    const openWhatIfSimulator = () => {
        setWhatIfData({ ...formData });
        setShowWhatIfModal(true);
    };

    const runWhatIfScenario = async () => {
        if (!whatIfData) return;

        try {
            const data = await xaiService.predictRisk(whatIfData);
            setWhatIfPrediction(data);
            showToastMessage('Scenario calculated!');
        } catch (err) {
            showToastMessage('Failed to calculate scenario');
        }
    };

    const applyWhatIfScenario = () => {
        if (whatIfData) {
            setFormData(whatIfData);
            setShowWhatIfModal(false);
            showToastMessage('Scenario applied! Click Predict to see results.');
        }
    };

    // Auto-save on form change
    useEffect(() => {
        const timer = setTimeout(() => {
            if (formData.student_id) {
                saveFormDraft();
            }
        }, 2000);
        return () => clearTimeout(timer);
    }, [formData]);

    useEffect(() => {
        if (prediction) {
            const plan = generateActionPlan(prediction.risk_level);
            setActionPlan(plan);
        }
    }, [prediction]);

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
        <div className={`xai-prediction-container ${theme}`}>
            {/* Theme Toggle */}
            <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Toast Notification */}
            {showToast && (
                <div className="toast-notification">
                    <CheckCircle size={18} />
                    <span>{toastMessage}</span>
                </div>
            )}

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

                            <div className="form-actions">
                                <button type="submit" className="submit-button" disabled={loading}>
                                    <Brain size={20} />
                                    {loading ? 'Analyzing Student Data...' : 'Predict Academic Risk'}
                                </button>
                                <div className="draft-actions">
                                    <button type="button" className="draft-btn" onClick={loadFormDraft}>
                                        <Download size={16} />
                                        Load Draft
                                    </button>
                                    <button type="button" className="draft-btn" onClick={clearDraft}>
                                        <X size={16} />
                                        Clear
                                    </button>
                                    <span className="auto-save-indicator">
                                        <Save size={14} />
                                        Auto-saving...
                                    </span>
                                </div>
                            </div>
                        </form>
                    </div>
                )}

                {prediction && (
                    <div className="results-container">
                        {/* Quick Action Buttons */}
                        <div className="quick-actions">
                            <button className="action-button primary" onClick={exportToPDF} title="Export as PDF">
                                <Download size={18} />
                                <span>Export PDF</span>
                            </button>
                            <button className="action-button secondary" onClick={handleShare} title="Share report">
                                <Share2 size={18} />
                                <span>Share</span>
                            </button>
                            <button className="action-button secondary" onClick={handlePrint} title="Print report">
                                <Printer size={18} />
                                <span>Print</span>
                            </button>
                            <button className="action-button secondary" onClick={exportAsImage} title="Export as image">
                                <Image size={18} />
                                <span>Screenshot</span>
                            </button>
                            <button className="action-button what-if" onClick={openWhatIfSimulator} title="Test scenarios">
                                <Sliders size={18} />
                                <span>What-If</span>
                            </button>
                        </div>

                        <div className="result-header">
                            <span
                                className={`risk-badge ${prediction.risk_level === 'At-Risk'
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
                                                    theme === 'light' ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.05)',
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
                                        <p className="section-subtitle">
                                            {prediction.risk_level === 'Safe'
                                                ? 'Maintain your excellent performance with these enhancement strategies'
                                                : prediction.risk_level === 'Medium Risk'
                                                    ? 'Follow these steps to improve your academic standing'
                                                    : 'URGENT: Immediate action required to prevent academic failure'}
                                        </p>
                                    </div>
                                </div>
                                <div className="plan-controls">
                                    <div className="progress-indicator">
                                        <div className="progress-circle">
                                            <svg viewBox="0 0 36 36" className="circular-progress">
                                                <path
                                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                    fill="none"
                                                    stroke="#444"
                                                    strokeWidth="3"
                                                />
                                                <path
                                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                    fill="none"
                                                    stroke="#667eea"
                                                    strokeWidth="3"
                                                    strokeDasharray={`${getProgressPercentage()}, 100`}
                                                />
                                            </svg>
                                            <span className="progress-text">{getProgressPercentage()}%</span>
                                        </div>
                                    </div>
                                    <span className="plan-progress">
                                        {actionPlan.filter(a => a.isCompleted).length} / {actionPlan.length} completed
                                    </span>
                                    <button
                                        className="customize-btn"
                                        onClick={() => setShowCustomizeModal(true)}
                                    >
                                        <Settings size={20} />
                                        Customize Plan
                                    </button>
                                </div>
                            </div>

                            {/* Search and Filter Controls */}
                            <div className="action-controls">
                                <div className="search-box">
                                    <Search size={18} />
                                    <input
                                        type="text"
                                        placeholder="Search actions..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                    />
                                </div>
                                <div className="filter-group">
                                    <Filter size={18} />
                                    <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
                                        <option value="all">All Categories</option>
                                        <option value="academic">Academic</option>
                                        <option value="engagement">Engagement</option>
                                        <option value="time-management">Time Management</option>
                                        <option value="support">Support</option>
                                    </select>
                                    <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
                                        <option value="all">All Priorities</option>
                                        <option value="critical">Critical</option>
                                        <option value="high">High</option>
                                        <option value="medium">Medium</option>
                                        <option value="standard">Standard</option>
                                    </select>
                                </div>
                            </div>

                            <div className="action-plan-timeline">
                                {getFilteredActions().map((action, index) => {
                                    const CategoryIcon = getCategoryIcon(action.category);
                                    const priorityColor = getPriorityColor(action.priority);

                                    return (
                                        <div key={action.id} className={`action-item-wrapper ${action.isCompleted ? 'completed' : ''}`}>
                                            <div className="action-item-timeline">
                                                <div className="timeline-dot" style={{ background: priorityColor }}>
                                                    {action.isCompleted ? <CheckCircle size={16} /> : <span className="step-number">{index + 1}</span>}
                                                </div>
                                                {index < actionPlan.length - 1 && <div className="timeline-line" />}
                                            </div>

                                            <div className="action-item-card">
                                                <div className="action-card-header">
                                                    <div className="action-category">
                                                        <div className="category-icon" style={{ background: `${priorityColor}15`, color: priorityColor }}>
                                                            <CategoryIcon size={20} />
                                                        </div>
                                                        <span className="category-label">{action.category.replace('-', ' ')}</span>
                                                    </div>
                                                    <div className="action-header-right">
                                                        <div className="priority-badge" style={{ background: `${priorityColor}20`, color: priorityColor, borderColor: `${priorityColor}40` }}>
                                                            {action.priority === 'critical' && <Zap size={14} />}
                                                            {action.priority === 'high' && <AlertCircle size={14} />}
                                                            {action.priority === 'medium' && <Clock size={14} />}
                                                            {action.priority === 'standard' && <CheckCircle size={14} />}
                                                            <span>{action.priority.toUpperCase()}</span>
                                                        </div>
                                                        {action.isCustom && (
                                                            <button
                                                                className="delete-action-btn"
                                                                onClick={() => deleteActionItem(action.id)}
                                                                title="Remove custom action"
                                                            >
                                                                <X size={16} />
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>

                                                <div className="action-card-body">
                                                    <h4 className="action-title">{action.title}</h4>
                                                    <p className="action-description">{action.description}</p>
                                                </div>

                                                <div className="action-card-footer">
                                                    <button
                                                        className={`action-btn-complete ${action.isCompleted ? 'completed' : ''}`}
                                                        onClick={() => toggleActionComplete(action.id)}
                                                    >
                                                        {action.isCompleted ? (
                                                            <>
                                                                <CheckCircle size={16} />
                                                                <span>Completed</span>
                                                            </>
                                                        ) : (
                                                            <>
                                                                <Circle size={16} />
                                                                <span>Mark Complete</span>
                                                            </>
                                                        )}
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
                                    <Zap size={20} />
                                    <span><strong>{actionPlan.filter(a => a.priority === 'critical').length}</strong> Critical Actions</span>
                                </div>
                                <div className="summary-card">
                                    <AlertCircle size={20} />
                                    <span><strong>{actionPlan.filter(a => a.priority === 'high').length}</strong> High Priority</span>
                                </div>
                                <div className="summary-card">
                                    <Target size={20} />
                                    <span><strong>{actionPlan.filter(a => a.priority === 'medium' || a.priority === 'standard').length}</strong> Standard Tasks</span>
                                </div>
                            </div>
                        </div>

                        {showCustomizeModal && (
                            <div className="modal-overlay" onClick={() => setShowCustomizeModal(false)}>
                                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                                    <div className="modal-header">
                                        <h3>Add Custom Action</h3>
                                        <button onClick={() => setShowCustomizeModal(false)}>
                                            <X size={24} />
                                        </button>
                                    </div>
                                    <div className="modal-body">
                                        <div className="form-group">
                                            <label>Action Title</label>
                                            <input
                                                type="text"
                                                value={newActionItem.title}
                                                onChange={(e) => setNewActionItem(prev => ({ ...prev, title: e.target.value }))}
                                                placeholder="e.g., Review Chapter 5 notes"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Description</label>
                                            <textarea
                                                value={newActionItem.description}
                                                onChange={(e) => setNewActionItem(prev => ({ ...prev, description: e.target.value }))}
                                                placeholder="Describe the action in detail..."
                                                rows={3}
                                            />
                                        </div>
                                        <div className="form-row">
                                            <div className="form-group">
                                                <label>Priority</label>
                                                <select
                                                    value={newActionItem.priority}
                                                    onChange={(e) => setNewActionItem(prev => ({ ...prev, priority: e.target.value as any }))}
                                                >
                                                    <option value="critical">Critical</option>
                                                    <option value="high">High</option>
                                                    <option value="medium">Medium</option>
                                                    <option value="standard">Standard</option>
                                                </select>
                                            </div>
                                            <div className="form-group">
                                                <label>Category</label>
                                                <select
                                                    value={newActionItem.category}
                                                    onChange={(e) => setNewActionItem(prev => ({ ...prev, category: e.target.value as any }))}
                                                >
                                                    <option value="academic">Academic</option>
                                                    <option value="engagement">Engagement</option>
                                                    <option value="time-management">Time Management</option>
                                                    <option value="support">Support</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="modal-footer">
                                        <button className="btn-secondary" onClick={() => setShowCustomizeModal(false)}>
                                            Cancel
                                        </button>
                                        <button className="btn-primary" onClick={addCustomAction}>
                                            Add Action
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

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
                                                            color: theme === 'light' ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.1)',
                                                            lineWidth: 1,
                                                        },
                                                        ticks: {
                                                            color: theme === 'light' ? '#4a5568' : '#a0aec0',
                                                            font: { size: 12 },
                                                            callback: (value) => value + '%',
                                                        },
                                                    },
                                                    x: {
                                                        grid: { display: false },
                                                        ticks: {
                                                            color: theme === 'light' ? '#1a202c' : '#fff',
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
                                                            color: theme === 'light' ? '#1a202c' : '#fff',
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
                                                            color: theme === 'light' ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.1)',
                                                        },
                                                        ticks: {
                                                            color: theme === 'light' ? '#4a5568' : '#a0aec0',
                                                            font: { size: 12 },
                                                        },
                                                    },
                                                    x: {
                                                        grid: { display: false },
                                                        ticks: {
                                                            color: theme === 'light' ? '#1a202c' : '#fff',
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
                                                        borderColor: theme === 'light' ? '#ffffff' : '#1a1a2e',
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
                                                            color: theme === 'light' ? '#1a202c' : '#fff',
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
                                                            color: theme === 'light' ? '#1a202c' : '#fff',
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
                                                            color: theme === 'light' ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.15)',
                                                            lineWidth: 1,
                                                        },
                                                        angleLines: {
                                                            color: theme === 'light' ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.15)',
                                                            lineWidth: 1,
                                                        },
                                                        ticks: {
                                                            color: theme === 'light' ? '#4a5568' : '#a0aec0',
                                                            backdropColor: 'transparent',
                                                            font: { size: 11 },
                                                            stepSize: 20,
                                                        },
                                                        pointLabels: {
                                                            color: theme === 'light' ? '#1a202c' : '#fff',
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

            {/* Share Modal */}
            {showShareModal && (
                <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
                    <div className="modal-content share-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Share Prediction Report</h3>
                            <button onClick={() => setShowShareModal(false)}>
                                <X size={24} />
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="share-content">
                                <div className="share-info">
                                    <div className="share-icon">
                                        <Share2 size={32} />
                                    </div>
                                    <p>Share this risk assessment report with advisors, tutors, or parents</p>
                                </div>

                                <div className="share-link-container">
                                    <label>Shareable Link</label>
                                    <div className="link-input-group">
                                        <input
                                            type="text"
                                            value={shareLink}
                                            readOnly
                                            onClick={(e) => (e.target as HTMLInputElement).select()}
                                        />
                                        <button className="copy-btn" onClick={copyToClipboard}>
                                            <Copy size={18} />
                                            Copy
                                        </button>
                                    </div>
                                </div>

                                <div className="qr-code-section">
                                    <label>QR Code</label>
                                    <div className="qr-placeholder">
                                        <QrCode size={120} strokeWidth={1.5} />
                                        <p>Scan to view report</p>
                                    </div>
                                    <button className="btn-secondary" onClick={downloadQRCode}>
                                        <Download size={16} />
                                        Download QR Code
                                    </button>
                                </div>

                                <div className="share-options">
                                    <p className="share-label">Quick Share</p>
                                    <div className="share-buttons">
                                        <button className="share-btn email" onClick={() => showToastMessage('Opening email client...')}>
                                            <Mail size={16} /> Email
                                        </button>
                                        <button className="share-btn whatsapp" onClick={() => showToastMessage('Opening WhatsApp...')}>
                                            <MessageCircle size={16} /> WhatsApp
                                        </button>
                                        <button className="share-btn link" onClick={copyToClipboard}>
                                            <ExternalLink size={16} /> Copy Link
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn-secondary" onClick={() => setShowShareModal(false)}>
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* What-If Simulator Modal */}
            {showWhatIfModal && whatIfData && (
                <div className="modal-overlay" onClick={() => setShowWhatIfModal(false)}>
                    <div className="modal-content what-if-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>What-If Scenario Simulator</h3>
                            <button onClick={() => setShowWhatIfModal(false)}>
                                <X size={24} />
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="what-if-content">
                                <div className="scenario-intro">
                                    <Sliders size={32} className="scenario-icon" />
                                    <p>Adjust the sliders below to see how changes would affect the risk prediction</p>
                                </div>

                                <div className="scenario-controls">
                                    <div className="scenario-item">
                                        <div className="slider-header">
                                            <Award size={18} />
                                            <label>Average Grade</label>
                                            <span className="slider-value">{whatIfData.avg_grade}%</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            value={whatIfData.avg_grade}
                                            onChange={(e) => setWhatIfData({ ...whatIfData, avg_grade: parseFloat(e.target.value) })}
                                        />
                                    </div>

                                    <div className="scenario-item">
                                        <div className="slider-header">
                                            <TargetIcon size={18} />
                                            <label>Grade Consistency</label>
                                            <span className="slider-value">{whatIfData.grade_consistency}%</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            value={whatIfData.grade_consistency}
                                            onChange={(e) => setWhatIfData({ ...whatIfData, grade_consistency: parseFloat(e.target.value) })}
                                        />
                                    </div>

                                    <div className="scenario-item">
                                        <div className="slider-header">
                                            <BookOpen size={18} />
                                            <label>Number of Assessments</label>
                                            <span className="slider-value">{whatIfData.num_assessments}</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="20"
                                            value={whatIfData.num_assessments}
                                            onChange={(e) => setWhatIfData({ ...whatIfData, num_assessments: parseInt(e.target.value) })}
                                        />
                                    </div>

                                    <div className="scenario-item">
                                        <div className="slider-header">
                                            <CheckCircle size={18} />
                                            <label>Assessment Completion Rate</label>
                                            <span className="slider-value">{(whatIfData.assessment_completion_rate * 100).toFixed(0)}%</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.01"
                                            value={whatIfData.assessment_completion_rate}
                                            onChange={(e) => setWhatIfData({ ...whatIfData, assessment_completion_rate: parseFloat(e.target.value) })}
                                        />
                                    </div>

                                    <div className="scenario-item">
                                        <div className="slider-header">
                                            <GraduationCap size={18} />
                                            <label>Studied Credits</label>
                                            <span className="slider-value">{whatIfData.studied_credits}</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="240"
                                            step="10"
                                            value={whatIfData.studied_credits}
                                            onChange={(e) => setWhatIfData({ ...whatIfData, studied_credits: parseInt(e.target.value) })}
                                        />
                                    </div>
                                </div>

                                {whatIfPrediction && (
                                    <div className="scenario-result">
                                        <h4>Predicted Outcome</h4>
                                        <div className={`risk-preview ${whatIfPrediction.risk_level.toLowerCase().replace(' ', '-')}`}>
                                            <span className="risk-level">{whatIfPrediction.risk_level}</span>
                                            <span className="risk-score">{whatIfPrediction.risk_score.toFixed(1)}% Risk</span>
                                            <span className="confidence">{whatIfPrediction.confidence.toFixed(1)}% Confident</span>
                                        </div>
                                        <div className="comparison">
                                            <div className="comparison-item">
                                                <span>Current:</span>
                                                <strong>{prediction?.risk_level}</strong>
                                            </div>
                                            <div className="comparison-arrow">→</div>
                                            <div className="comparison-item">
                                                <span>If changed:</span>
                                                <strong>{whatIfPrediction.risk_level}</strong>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn-secondary" onClick={() => setShowWhatIfModal(false)}>
                                Cancel
                            </button>
                            <button className="btn-secondary" onClick={runWhatIfScenario}>
                                <Brain size={16} />
                                Calculate
                            </button>
                            <button className="btn-primary" onClick={applyWhatIfScenario}>
                                Apply Scenario
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default XAIPrediction;

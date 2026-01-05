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
    BarChart3,
    Bell,
    Calendar,
    CheckCircle,
    FileText,
    Mail,
    PieChart,
    Settings,
    Target,
    TrendingUp,
    Users
} from 'lucide-react';
import { useState } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import './Dashboard.css';

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

interface DashboardStats {
    totalStudents: number;
    safeStudents: number;
    mediumRiskStudents: number;
    atRiskStudents: number;
    averageGrade: number;
    completionRate: number;
}

const Dashboard = () => {
    const [stats, setStats] = useState<DashboardStats>({
        totalStudents: 1250,
        safeStudents: 687,
        mediumRiskStudents: 312,
        atRiskStudents: 251,
        averageGrade: 68.5,
        completionRate: 72.3,
    });

    // Risk Distribution Chart
    const riskDistributionData = {
        labels: ['Safe', 'Medium Risk', 'At-Risk'],
        datasets: [
            {
                label: 'Number of Students',
                data: [stats.safeStudents, stats.mediumRiskStudents, stats.atRiskStudents],
                backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
                borderColor: ['#16a34a', '#d97706', '#dc2626'],
                borderWidth: 2,
            },
        ],
    };

    // Grade Distribution Chart
    const gradeDistributionData = {
        labels: ['0-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100'],
        datasets: [
            {
                label: 'Number of Students',
                data: [45, 78, 156, 342, 389, 198, 42],
                backgroundColor: 'rgba(99, 102, 241, 0.8)',
                borderColor: 'rgb(99, 102, 241)',
                borderWidth: 2,
            },
        ],
    };

    // Trend Over Time Chart
    const trendData = {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
        datasets: [
            {
                label: 'Safe',
                data: [520, 545, 580, 610, 635, 658, 675, 687],
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Medium Risk',
                data: [380, 365, 345, 330, 325, 318, 315, 312],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
            },
            {
                label: 'At-Risk',
                data: [350, 340, 325, 310, 290, 274, 260, 251],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
            },
        ],
    };

    // Doughnut chart for risk distribution
    const riskDoughnutData = {
        labels: ['Safe', 'Medium Risk', 'At-Risk'],
        datasets: [
            {
                data: [stats.safeStudents, stats.mediumRiskStudents, stats.atRiskStudents],
                backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
                borderColor: ['#fff', '#fff', '#fff'],
                borderWidth: 3,
            },
        ],
    };

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1><BarChart3 className="header-icon" /> Student Risk Analytics Dashboard</h1>
                <p className="dashboard-subtitle">Real-time monitoring and insights</p>
            </div>

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card total">
                    <div className="stat-icon"><Users size={48} /></div>
                    <div className="stat-content">
                        <h3>Total Students</h3>
                        <p className="stat-value">{stats.totalStudents.toLocaleString()}</p>
                        <span className="stat-change positive">+5.2% from last month</span>
                    </div>
                </div>

                <div className="stat-card safe">
                    <div className="stat-icon"><CheckCircle size={48} /></div>
                    <div className="stat-content">
                        <h3>Safe Students</h3>
                        <p className="stat-value">{stats.safeStudents}</p>
                        <span className="stat-percentage">{((stats.safeStudents / stats.totalStudents) * 100).toFixed(1)}%</span>
                    </div>
                </div>

                <div className="stat-card medium">
                    <div className="stat-icon"><AlertTriangle size={48} /></div>
                    <div className="stat-content">
                        <h3>Medium Risk</h3>
                        <p className="stat-value">{stats.mediumRiskStudents}</p>
                        <span className="stat-percentage">{((stats.mediumRiskStudents / stats.totalStudents) * 100).toFixed(1)}%</span>
                    </div>
                </div>

                <div className="stat-card at-risk">
                    <div className="stat-icon"><AlertCircle size={48} /></div>
                    <div className="stat-content">
                        <h3>At-Risk Students</h3>
                        <p className="stat-value">{stats.atRiskStudents}</p>
                        <span className="stat-percentage">{((stats.atRiskStudents / stats.totalStudents) * 100).toFixed(1)}%</span>
                    </div>
                </div>

                <div className="stat-card grade">
                    <div className="stat-icon"><TrendingUp size={48} /></div>
                    <div className="stat-content">
                        <h3>Average Grade</h3>
                        <p className="stat-value">{stats.averageGrade}%</p>
                        <span className="stat-change positive">+2.3% from last week</span>
                    </div>
                </div>

                <div className="stat-card completion">
                    <div className="stat-icon"><Target size={48} /></div>
                    <div className="stat-content">
                        <h3>Completion Rate</h3>
                        <p className="stat-value">{stats.completionRate}%</p>
                        <span className="stat-change negative">-1.5% from last week</span>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="charts-grid">
                <div className="chart-card">
                    <h3><BarChart3 size={20} className="chart-icon" /> Risk Level Distribution</h3>
                    <div className="chart-container">
                        <Bar
                            data={riskDistributionData}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        display: false,
                                    },
                                    title: {
                                        display: false,
                                    },
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        grid: {
                                            color: 'rgba(255, 255, 255, 0.1)',
                                        },
                                        ticks: {
                                            color: '#fff',
                                        },
                                    },
                                    x: {
                                        grid: {
                                            display: false,
                                        },
                                        ticks: {
                                            color: '#fff',
                                        },
                                    },
                                },
                            }}
                        />
                    </div>
                </div>

                <div className="chart-card">
                    <h3><PieChart size={20} className="chart-icon" /> Risk Distribution</h3>
                    <div className="chart-container">
                        <Doughnut
                            data={riskDoughnutData}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            color: '#fff',
                                            padding: 20,
                                            font: {
                                                size: 14,
                                            },
                                        },
                                    },
                                },
                            }}
                        />
                    </div>
                </div>

                <div className="chart-card wide">
                    <h3><TrendingUp size={20} className="chart-icon" /> Grade Distribution</h3>
                    <div className="chart-container">
                        <Bar
                            data={gradeDistributionData}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        display: false,
                                    },
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        grid: {
                                            color: 'rgba(255, 255, 255, 0.1)',
                                        },
                                        ticks: {
                                            color: '#fff',
                                        },
                                    },
                                    x: {
                                        grid: {
                                            display: false,
                                        },
                                        ticks: {
                                            color: '#fff',
                                        },
                                    },
                                },
                            }}
                        />
                    </div>
                </div>

                <div className="chart-card wide">
                    <h3><Activity size={20} className="chart-icon" /> Risk Trend Over Time</h3>
                    <div className="chart-container">
                        <Line
                            data={trendData}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        position: 'top',
                                        labels: {
                                            color: '#fff',
                                            padding: 15,
                                        },
                                    },
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        grid: {
                                            color: 'rgba(255, 255, 255, 0.1)',
                                        },
                                        ticks: {
                                            color: '#fff',
                                        },
                                    },
                                    x: {
                                        grid: {
                                            display: false,
                                        },
                                        ticks: {
                                            color: '#fff',
                                        },
                                    },
                                },
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Recent Alerts */}
            <div className="alerts-section">
                <h3><Bell size={24} className="section-icon" /> Recent Alerts</h3>
                <div className="alerts-list">
                    <div className="alert-item critical">
                        <span className="alert-badge">CRITICAL</span>
                        <div className="alert-content">
                            <p className="alert-title">15 students moved to At-Risk status</p>
                            <p className="alert-time">2 hours ago</p>
                        </div>
                    </div>
                    <div className="alert-item warning">
                        <span className="alert-badge">WARNING</span>
                        <div className="alert-content">
                            <p className="alert-title">Assessment completion rate dropped below 75%</p>
                            <p className="alert-time">5 hours ago</p>
                        </div>
                    </div>
                    <div className="alert-item info">
                        <span className="alert-badge">INFO</span>
                        <div className="alert-content">
                            <p className="alert-title">42 students improved to Safe status</p>
                            <p className="alert-time">1 day ago</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
                <h3><Settings size={24} className="section-icon" /> Quick Actions</h3>
                <div className="actions-grid">
                    <button className="action-btn">
                        <Mail size={20} />
                        Send Bulk Emails
                    </button>
                    <button className="action-btn">
                        <FileText size={20} />
                        Export Report
                    </button>
                    <button className="action-btn">
                        <Calendar size={20} />
                        Schedule Meetings
                    </button>
                    <button className="action-btn">
                        <Bell size={20} />
                        Set Alerts
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

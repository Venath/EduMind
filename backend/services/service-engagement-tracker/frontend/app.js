// ============================================
// EDUMIND ANALYTICS - MODERN JAVASCRIPT
// ============================================

// API Configuration
const API_BASE_URL = 'http://localhost:8002';

// State Management
let currentStudent = null;
let engagementChart = null;
let activityChart = null;

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    await checkSystemHealth();
    await loadSystemStats();
    setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
    // Enter key on input
    document.getElementById('studentInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            loadStudentDashboard();
        }
    });
    
    // Toast close
    document.getElementById('toastClose').addEventListener('click', hideToast);
}

// ============================================
// SYSTEM HEALTH & STATS
// ============================================

async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const badge = document.getElementById('systemBadge');
        if (data.status === 'healthy') {
            badge.innerHTML = '<div class="badge-pulse"></div><span>System Online</span>';
        } else {
            badge.innerHTML = '<div class="badge-pulse" style="background: #ef4444;"></div><span>System Offline</span>';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        const badge = document.getElementById('systemBadge');
        badge.innerHTML = '<div class="badge-pulse" style="background: #ef4444;"></div><span>System Offline</span>';
        // Don't show toast on initial load - less intrusive
        console.warn('API server not available. Please start the server on port 8002.');
    }
}

async function loadSystemStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/stats`);
        const data = await response.json();
        
        console.log('Stats data:', data); // Debug log
        
        document.getElementById('totalStudents').textContent = data.total_students || 0;
        document.getElementById('highRiskCount').textContent = data.high_risk_students || 0;
        document.getElementById('lowEngagementCount').textContent = data.low_engagement_students || 0;
        document.getElementById('avgEngagement').textContent = (data.avg_engagement_score || 0).toFixed(2);
    } catch (error) {
        console.error('Failed to load system stats:', error);
        // Set default values when server is not available
        document.getElementById('totalStudents').textContent = '--';
        document.getElementById('highRiskCount').textContent = '--';
        document.getElementById('lowEngagementCount').textContent = '--';
        document.getElementById('avgEngagement').textContent = '--';
    }
}

// ============================================
// STUDENT LOADING
// ============================================

function loadStudent(studentId) {
    document.getElementById('studentInput').value = studentId;
    loadStudentDashboard();
}

async function loadStudentDashboard() {
    const studentId = document.getElementById('studentInput').value.trim().toUpperCase();
    
    if (!studentId) {
        showToast('Please enter a student ID', 'error');
        return;
    }
    
    // Show loading
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    try {
        // Load student data
        const [engagementResponse, predictionResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/api/v1/students/${studentId}/dashboard`),
            fetch(`${API_BASE_URL}/api/v1/predictions/students/${studentId}/latest`)
        ]);
        
        // Check if both responses are successful
        if (!engagementResponse.ok) {
            throw new Error(`Engagement API returned ${engagementResponse.status}: ${engagementResponse.statusText}`);
        }
        if (!predictionResponse.ok) {
            throw new Error(`Prediction API returned ${predictionResponse.status}: ${predictionResponse.statusText}`);
        }
        
        const engagementData = await engagementResponse.json();
        const predictionData = await predictionResponse.json();
        
        currentStudent = {
            id: studentId,
            engagement: engagementData,
            prediction: predictionData
        };
        
        // Display dashboard
        displayStudentDashboard();
        
        // Load existing schedule
        await loadExistingSchedule();
        
        showToast('Student data loaded successfully', 'success');
        
    } catch (error) {
        console.error('Failed to load student:', error);
        showToast('Failed to load student data. Please check the student ID.', 'error');
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// ============================================
// DASHBOARD DISPLAY
// ============================================

function displayStudentDashboard() {
    const { id, engagement, prediction } = currentStudent;
    
    // Set student ID and initials
    const initials = id.substring(0, 2);
    document.getElementById('studentInitials').textContent = initials;
    document.getElementById('studentIdDisplay').textContent = id;
    document.getElementById('studentMetadata').textContent = `Last updated: ${engagement.last_updated || new Date().toLocaleDateString()}`;
    
    // Update chart title with actual days
    const daysAnalyzed = engagement.recent_trend?.days_analyzed || 7;
    const chartTitle = document.querySelector('.chart-card-modern h3');
    if (chartTitle) {
        chartTitle.textContent = `📊 Engagement Trend (Last ${daysAnalyzed} Days)`;
    }
    
    // Display engagement metrics
    displayEngagementMetrics(engagement);
    
    // Display prediction
    displayPrediction(prediction);
    
    // Create charts with dashboard data
    createEngagementChart(engagement);
    createActivityChart(engagement);
    
    // Show dashboard
    document.getElementById('studentDashboard').style.display = 'block';
    
    // Smooth scroll
    setTimeout(() => {
        document.getElementById('studentDashboard').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function displayEngagementMetrics(engagement) {
    const status = engagement.current_status || {};
    const components = engagement.component_scores || {};
    
    // Engagement score and level
    const score = status.engagement_score || 0;
    const level = status.engagement_level || 'Unknown';
    
    document.getElementById('engagementScore').textContent = score.toFixed(2);
    document.getElementById('engagementLevel').textContent = level;
    
    // Set badge color based on level
    const badge = document.getElementById('engagementBadge');
    badge.className = 'profile-badge';
    if (level === 'High') {
        badge.style.borderColor = '#43e97b';
    } else if (level === 'Medium') {
        badge.style.borderColor = '#fa709a';
    } else {
        badge.style.borderColor = '#f5576c';
    }
    
    // Days tracked
    const daysTracked = engagement.recent_trend?.days_analyzed || 0;
    document.getElementById('daysTracked').textContent = daysTracked;
    
    // Activity level (score is on 0-100 scale)
    const activityLevel = score >= 70 ? 'High' : score >= 40 ? 'Medium' : 'Low';
    document.getElementById('activityLevel').textContent = activityLevel;
    
    // Detailed metrics - use component scores (0-100 scale)
    // These represent engagement scores in different areas, not raw counts
    document.getElementById('contentViews').textContent = Math.round(components.session || 0) + '%';
    document.getElementById('assignments').textContent = Math.round(components.assignment || 0) + '%';
    document.getElementById('quizScore').textContent = Math.round(components.interaction || 0) + '%';
    document.getElementById('forumPosts').textContent = Math.round(components.forum || 0) + '%';
    document.getElementById('timeSpent').textContent = Math.round(components.session || 0) + '%';
    document.getElementById('loginFreq').textContent = Math.round(components.login || 0) + '%';
}

function displayPrediction(prediction) {
    const riskLevel = prediction.risk_level || 'Unknown';
    const probability = prediction.risk_probability || 0;
    
    // Set risk level
    const riskElement = document.getElementById('riskLevel');
    riskElement.textContent = riskLevel;
    riskElement.className = 'status-value ' + riskLevel.toLowerCase();
    
    // Set probability bar
    const probabilityPercent = (probability * 100).toFixed(1);
    document.getElementById('probabilityBar').style.width = probabilityPercent + '%';
    document.getElementById('probabilityValue').textContent = probabilityPercent + '%';
    
    // Set icon color based on risk
    const icon = document.getElementById('predictionIcon');
    if (riskLevel === 'Low') {
        icon.style.background = 'rgba(67, 233, 123, 0.1)';
        icon.style.color = '#43e97b';
    } else if (riskLevel === 'Medium') {
        icon.style.background = 'rgba(250, 112, 154, 0.1)';
        icon.style.color = '#fa709a';
    } else {
        icon.style.background = 'rgba(245, 87, 108, 0.1)';
        icon.style.color = '#f5576c';
    }
    
    // Display key factors
    displayKeyFactors(prediction.contributing_factors || {});
}

function displayKeyFactors(factors) {
    const container = document.getElementById('factorsList');
    const factorsSection = document.getElementById('predictionFactors');
    container.innerHTML = '';
    
    // Convert object to array if needed
    let factorArray = [];
    if (typeof factors === 'object' && !Array.isArray(factors)) {
        // factors is an object like {low_login: true, declining_engagement: true}
        factorArray = Object.entries(factors)
            .filter(([key, value]) => value)
            .map(([key, value]) => ({
                name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                severity: 'medium'
            }));
    } else if (Array.isArray(factors)) {
        factorArray = factors;
    }
    
    if (factorArray.length === 0) {
        // Hide the entire factors section if no factors
        factorsSection.style.display = 'none';
        return;
    }
    
    // Show the factors section
    factorsSection.style.display = 'block';
    
    factorArray.forEach(factor => {
        const factorDiv = document.createElement('div');
        factorDiv.className = 'factor-item';
        
        // Determine icon based on factor type
        let icon = '📊';
        const factorName = typeof factor === 'string' ? factor : (factor.name || factor);
        const factorText = String(factorName).toLowerCase();
        
        if (factorText.includes('login')) icon = '🔑';
        else if (factorText.includes('assignment')) icon = '📝';
        else if (factorText.includes('quiz')) icon = '✅';
        else if (factorText.includes('forum')) icon = '💬';
        else if (factorText.includes('time') || factorText.includes('session')) icon = '⏱️';
        else if (factorText.includes('engagement')) icon = '📉';
        
        factorDiv.innerHTML = `
            <div class="factor-icon">${icon}</div>
            <div class="factor-text">${factorName}</div>
        `;
        
        container.appendChild(factorDiv);
    });
}

// ============================================
// CHARTS
// ============================================

function createEngagementChart(engagement) {
    const ctx = document.getElementById('engagementChart').getContext('2d');
    
    if (engagementChart) {
        engagementChart.destroy();
    }
    
    // For dashboard endpoint, create a simple 7-day trend
    // In production, you'd fetch analytics endpoint for full history
    const currentScore = engagement.current_status?.engagement_score || 0;
    const trendChange = engagement.recent_trend?.change || 0;
    const daysAnalyzed = engagement.recent_trend?.days_analyzed || 7;
    
    // Generate simple trend data
    const labels = [];
    const scores = [];
    const today = new Date();
    
    for (let i = daysAnalyzed - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // Simple linear interpolation
        const progress = i / (daysAnalyzed - 1);
        const score = currentScore - (trendChange * (1 - progress));
        scores.push(Math.max(0, Math.min(1, score)));
    }
    
    engagementChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Engagement Score',
                data: scores,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(22, 33, 62, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#a0aec0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        color: '#a0aec0',
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: '#a0aec0',
                        font: {
                            size: 11
                        },
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createActivityChart(engagement) {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    if (activityChart) {
        activityChart.destroy();
    }
    
    const components = engagement.component_scores || {};
    
    const data = {
        labels: ['Login', 'Session', 'Interaction', 'Forum', 'Assignment'],
        datasets: [{
            data: [
                components.login || 0,
                components.session || 0,
                components.interaction || 0,
                components.forum || 0,
                components.assignment || 0
            ],
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(118, 75, 162, 0.8)',
                'rgba(67, 233, 123, 0.8)',
                'rgba(250, 112, 154, 0.8)',
                'rgba(79, 172, 254, 0.8)'
            ],
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 2
        }]
    };
    
    activityChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0aec0',
                        padding: 15,
                        font: {
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(22, 33, 62, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#a0aec0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const title = document.getElementById('toastTitle');
    const messageEl = document.getElementById('toastMessage');
    
    title.textContent = type === 'success' ? 'Success' : 'Error';
    messageEl.textContent = message;
    
    toast.className = `toast-notification ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        hideToast();
    }, 5000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('show');
}

// ============================================
// STUDY SCHEDULING
// ============================================

let scheduleDetailsExpanded = false;

async function generateSchedule() {
    const studentId = document.getElementById('studentInput').value.trim().toUpperCase();
    
    if (!studentId) {
        showToast('Please enter a student ID first', 'error');
        return;
    }
    
    // Show loading
    document.getElementById('scheduleLoading').style.display = 'block';
    document.getElementById('noSchedule').style.display = 'none';
    document.getElementById('scheduleSummary').style.display = 'none';
    document.getElementById('weeklySchedule').style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/schedules/students/${studentId}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.message || error.detail || 'Failed to generate schedule');
        }
        
        const schedule = await response.json();
        displaySchedule(schedule);
        showToast('Schedule generated successfully!', 'success');
    } catch (error) {
        console.error('Failed to generate schedule:', error);
        showToast(error.message || 'Failed to generate schedule', 'error');
        document.getElementById('scheduleLoading').style.display = 'none';
        document.getElementById('noSchedule').style.display = 'block';
    }
}

async function loadExistingSchedule() {
    const studentId = document.getElementById('studentInput').value.trim().toUpperCase();
    
    if (!studentId) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/schedules/students/${studentId}`);
        
        if (response.ok) {
            const data = await response.json();
            
            // Check if schedule exists (new format returns {schedule: null} when not found)
            if (data.schedule === null || data.message) {
                // No schedule exists - show empty state
                document.getElementById('noSchedule').style.display = 'block';
                document.getElementById('scheduleSummary').style.display = 'none';
                document.getElementById('weeklySchedule').style.display = 'none';
                document.getElementById('scheduleLoading').style.display = 'none';
            } else {
                // Schedule exists - display it
                displaySchedule(data);
            }
        } else {
            // Handle other errors
            document.getElementById('noSchedule').style.display = 'block';
            document.getElementById('scheduleSummary').style.display = 'none';
            document.getElementById('weeklySchedule').style.display = 'none';
            document.getElementById('scheduleLoading').style.display = 'none';
        }
    } catch (error) {
        // Network error - show empty state
        document.getElementById('noSchedule').style.display = 'block';
        document.getElementById('scheduleSummary').style.display = 'none';
        document.getElementById('weeklySchedule').style.display = 'none';
        document.getElementById('scheduleLoading').style.display = 'none';
    }
}

function displaySchedule(schedule) {
    // Hide loading and empty state
    document.getElementById('scheduleLoading').style.display = 'none';
    document.getElementById('noSchedule').style.display = 'none';
    
    // Calculate average session duration from daily schedules (accounts for load reduction)
    let totalSessionMinutes = 0;
    let totalSessions = 0;
    let totalDailyMinutes = 0;
    let totalDays = 0;
    
    if (schedule.daily_schedules && schedule.daily_schedules.length > 0) {
        schedule.daily_schedules.forEach(day => {
            if (day.sessions && day.sessions.length > 0) {
                day.sessions.forEach(session => {
                    totalSessionMinutes += session.duration_minutes || 0;
                    totalSessions += 1;
                });
            }
            // Calculate actual daily total from daily_schedules
            if (day.total_minutes !== undefined) {
                totalDailyMinutes += day.total_minutes;
                totalDays += 1;
            }
        });
    }
    
    const avgSessionDuration = totalSessions > 0 ? Math.round(totalSessionMinutes / totalSessions) : schedule.session_length_minutes;
    const avgDailyMinutes = totalDays > 0 ? Math.round(totalDailyMinutes / totalDays) : schedule.total_study_minutes_per_day;
    
    // Display summary
    document.getElementById('scheduleSessionLength').textContent = `${avgSessionDuration} minutes`;
    document.getElementById('scheduleSessionsPerDay').textContent = schedule.sessions_per_day;
    document.getElementById('scheduleDailyMinutes').textContent = `${avgDailyMinutes} minutes/day`;
    
    if (schedule.load_reduction_factor < 1.0) {
        const reduction = Math.round((1 - schedule.load_reduction_factor) * 100);
        document.getElementById('scheduleLoadReduction').textContent = `${reduction}% reduction applied`;
    } else {
        document.getElementById('scheduleLoadReduction').textContent = 'No reduction';
    }
    
    document.getElementById('scheduleSummary').style.display = 'block';
    
    // Load reasoning
    loadScheduleReasoning(schedule.student_id);
    
    // Display weekly schedule
    displayWeeklySchedule(schedule.daily_schedules);
    document.getElementById('weeklySchedule').style.display = 'block';
}

async function loadScheduleReasoning(studentId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/schedules/students/${studentId}/summary`);
        const toggleBtn = document.getElementById('toggleDetailsBtn');
        
        if (response.ok) {
            const summary = await response.json();
            const reasoningContent = document.getElementById('reasoningContent');
            
            if (summary.reasoning && Object.keys(summary.reasoning).length > 0) {
                reasoningContent.innerHTML = '';
                
                for (const [key, value] of Object.entries(summary.reasoning)) {
                    const reasoningItem = document.createElement('div');
                    reasoningItem.className = 'reasoning-item';
                    reasoningItem.innerHTML = `
                        <strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                        <p>${value}</p>
                    `;
                    reasoningContent.appendChild(reasoningItem);
                }
                
                // Show indicator that reasoning is available
                toggleBtn.style.opacity = '1';
                toggleBtn.style.cursor = 'pointer';
                toggleBtn.setAttribute('title', 'Show AI Reasoning (Click to expand)');
                toggleBtn.removeAttribute('disabled');
            } else {
                // No reasoning available - disable toggle button
                toggleBtn.style.opacity = '0.3';
                toggleBtn.style.cursor = 'not-allowed';
                toggleBtn.setAttribute('title', 'No reasoning available');
                toggleBtn.setAttribute('disabled', 'true');
            }
        } else if (response.status === 404) {
            // Schedule exists but summary not available
            toggleBtn.style.opacity = '0.3';
            toggleBtn.style.cursor = 'not-allowed';
            toggleBtn.setAttribute('title', 'Reasoning not available');
            toggleBtn.setAttribute('disabled', 'true');
        }
    } catch (error) {
        console.error('Failed to load schedule reasoning:', error);
        const toggleBtn = document.getElementById('toggleDetailsBtn');
        toggleBtn.style.opacity = '0.3';
        toggleBtn.style.cursor = 'not-allowed';
        toggleBtn.setAttribute('disabled', 'true');
    }
}

function displayWeeklySchedule(dailySchedules) {
    const scheduleDays = document.getElementById('scheduleDays');
    scheduleDays.innerHTML = '';
    
    dailySchedules.forEach(day => {
        const dayCard = document.createElement('div');
        dayCard.className = `schedule-day-card ${day.is_light_day ? 'light-day' : ''}`;
        
        const sessionsHtml = day.sessions.map(session => `
            <div class="session-item">
                <div class="session-header">
                    <span class="session-number">Session ${session.session_number}</span>
                    <span class="session-duration">${session.duration_minutes} min</span>
                </div>
                <div class="session-details">
                    <div class="session-task">${formatTaskType(session.task_type)}</div>
                    <div class="session-time">${session.suggested_time}</div>
                </div>
            </div>
        `).join('');
        
        dayCard.innerHTML = `
            <div class="day-header">
                <h5>${day.day_name}</h5>
                <span class="day-date">${formatDate(day.date)}</span>
                ${day.is_light_day ? '<span class="light-day-badge">Light Day</span>' : ''}
            </div>
            <div class="day-total">
                <span>Total: ${day.total_minutes} minutes</span>
            </div>
            <div class="sessions-list">
                ${sessionsHtml}
            </div>
            <div class="task-breakdown">
                ${day.task_breakdown.assignment_prep_minutes > 0 ? 
                    `<div class="task-item">📝 Assignments: ${day.task_breakdown.assignment_prep_minutes} min</div>` : ''}
                ${day.task_breakdown.quiz_interaction_minutes > 0 ? 
                    `<div class="task-item">🎯 Quizzes: ${day.task_breakdown.quiz_interaction_minutes} min</div>` : ''}
                ${day.task_breakdown.forum_engagement_minutes > 0 ? 
                    `<div class="task-item">💬 Forum: ${day.task_breakdown.forum_engagement_minutes} min</div>` : ''}
                ${day.task_breakdown.general_study_minutes > 0 ? 
                    `<div class="task-item">📚 General Study: ${day.task_breakdown.general_study_minutes} min</div>` : ''}
            </div>
        `;
        
        scheduleDays.appendChild(dayCard);
    });
}

function formatTaskType(taskType) {
    const types = {
        'assignment_prep': '📝 Assignment Prep',
        'quiz_interaction': '🎯 Quiz/Interaction',
        'forum_engagement': '💬 Forum Engagement',
        'general_study': '📚 General Study'
    };
    return types[taskType] || taskType;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function toggleScheduleDetails() {
    const toggleBtn = document.getElementById('toggleDetailsBtn');
    
    // Don't toggle if button is disabled
    if (toggleBtn.hasAttribute('disabled')) {
        return;
    }
    
    scheduleDetailsExpanded = !scheduleDetailsExpanded;
    const reasoning = document.getElementById('scheduleReasoning');
    
    if (scheduleDetailsExpanded) {
        reasoning.style.display = 'block';
        toggleBtn.style.transform = 'rotate(180deg)';
        toggleBtn.setAttribute('title', 'Hide AI Reasoning');
    } else {
        reasoning.style.display = 'none';
        toggleBtn.style.transform = 'rotate(0deg)';
        toggleBtn.setAttribute('title', 'Show AI Reasoning (Click to expand)');
    }
}



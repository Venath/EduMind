// ============================================
// EDUMIND AI - MODERN WORKFLOW JAVASCRIPT
// ============================================

// API Configuration
const API_BASE_URL = 'http://localhost:8003/api/v1';

// State Management
let students = [];
let currentStudentId = null;
let currentStudentProfile = null;
let currentMLPrediction = null;
let learningStyleChart = null;
let struggleTopicsChart = null;

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    await checkSystemHealth();
    await loadSystemStats();
    await loadStudents();
    await loadCharts();
    setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
    // Step 1: Load Student
    document.getElementById('loadStudentBtn').addEventListener('click', loadStudentProfile);
    document.getElementById('studentInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadStudentProfile();
    });
    
    // Step 2: Classify
    document.getElementById('classifyBtn').addEventListener('click', classifyLearningStyle);
    document.getElementById('proceedToClassifyBtn').addEventListener('click', () => {
        document.getElementById('step2Card').style.display = 'block';
        document.getElementById('step2Card').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    
    // Step 3: Recommendations
    document.getElementById('proceedToRecommendBtn').addEventListener('click', () => {
        document.getElementById('step3Card').style.display = 'block';
        document.getElementById('step3Card').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    document.getElementById('generateBtn').addEventListener('click', generateRecommendations);
    
    // Slider
    const slider = document.getElementById('maxRecsInput');
    const sliderValue = document.getElementById('sliderValue');
    slider.addEventListener('input', () => {
        sliderValue.textContent = slider.value;
    });
    
    // Toast close
    document.getElementById('toastClose').addEventListener('click', hideToast);
}

// ============================================
// SYSTEM HEALTH & STATS
// ============================================

async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/system/health`);
        const data = await response.json();
        
        const badge = document.getElementById('systemBadge');
        if (data.status === 'healthy') {
            badge.innerHTML = '<div class="badge-pulse"></div><span>System Online</span>';
        } else {
            badge.innerHTML = '<div class="badge-pulse" style="background: #ef4444;"></div><span>System Offline</span>';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        showToast('Failed to connect to API', 'error');
    }
}

async function loadSystemStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/system/stats`);
        const data = await response.json();
        
        document.getElementById('totalStudents').textContent = data.total_students;
        document.getElementById('totalResources').textContent = data.total_resources;
        document.getElementById('totalRecommendations').textContent = data.total_recommendations;
        document.getElementById('completionRate').textContent = data.recommendation_completion_rate.toFixed(1) + '%';
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ============================================
// STEP 1: STUDENT SELECTION
// ============================================

async function loadStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/students?limit=100`);
        students = await response.json();
        
        // Populate datalist
        const datalist = document.getElementById('studentsList');
        datalist.innerHTML = '';
        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.student_id;
            datalist.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load students:', error);
    }
}

async function loadStudentProfile() {
    const studentId = document.getElementById('studentInput').value.trim().toUpperCase();
    
    if (!studentId) {
        showToast('Please enter a student ID', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/students/${studentId}`);
        
        if (!response.ok) {
            throw new Error('Student not found');
        }
        
        currentStudentProfile = await response.json();
        currentStudentId = studentId;
        
        // Display profile
        displayStudentProfile();
        
        // Reset subsequent steps
        document.getElementById('step2Card').style.display = 'none';
        document.getElementById('step3Card').style.display = 'none';
        document.getElementById('mlResultsCard').style.display = 'none';
        document.getElementById('recommendationsDisplay').style.display = 'none';
        
        showToast('Student profile loaded successfully', 'success');
        
    } catch (error) {
        console.error('Failed to load student:', error);
        showToast('Student not found. Please check the ID.', 'error');
    }
}

function displayStudentProfile() {
    const profile = currentStudentProfile;
    
    // Set initials
    const initials = currentStudentId.substring(0, 2);
    document.getElementById('studentInitials').textContent = initials;
    
    // Set profile info
    document.getElementById('profileStudentId').textContent = currentStudentId;
    document.getElementById('profileMetadata').textContent = `Profile loaded • ${new Date().toLocaleDateString()}`;
    
    // Set details
    document.getElementById('profileDifficulty').textContent = profile.preferred_difficulty || 'Medium';
    document.getElementById('profileCompletionRate').textContent = (profile.avg_completion_rate || 0).toFixed(1) + '%';
    
    // Get days tracked from profile or calculate from behavior tracking
    const daysTracked = profile.days_tracked || 0;
    document.getElementById('profileDaysTracked').textContent = daysTracked > 0 ? `${daysTracked} ${daysTracked === 1 ? 'day' : 'days'}` : 'No data';
    
    // Show profile card
    document.getElementById('studentProfileCard').style.display = 'block';
    
    // Smooth scroll
    setTimeout(() => {
        document.getElementById('studentProfileCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// ============================================
// STEP 2: ML CLASSIFICATION
// ============================================

async function classifyLearningStyle() {
    if (!currentStudentId) {
        showToast('Please load a student first', 'error');
        return;
    }
    
    // Show loading
    document.getElementById('mlLoading').style.display = 'flex';
    document.getElementById('mlResultsCard').style.display = 'none';
    document.getElementById('mlError').style.display = 'none';
    document.getElementById('classifyBtn').disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/ml/classify/${currentStudentId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail?.message || 'Classification failed');
        }
        
        currentMLPrediction = await response.json();
        
        // Display results
        displayMLResults();
        
        showToast('Learning style classified successfully!', 'success');
        
    } catch (error) {
        console.error('Classification failed:', error);
        document.getElementById('mlError').style.display = 'flex';
        document.getElementById('mlErrorMessage').textContent = error.message;
        showToast('Classification failed', 'error');
    } finally {
        document.getElementById('mlLoading').style.display = 'none';
        document.getElementById('classifyBtn').disabled = false;
    }
}

function displayMLResults() {
    const data = currentMLPrediction;
    
    // Set predicted style
    document.getElementById('mlPredictedStyle').textContent = data.predicted_style;
    
    // Set confidence
    const confidence = (data.confidence * 100).toFixed(1);
    document.getElementById('mlConfidence').textContent = confidence + '%';
    
    // Set confidence badge
    const badge = document.getElementById('mlConfidenceBadge');
    if (data.confidence >= 0.7) {
        badge.textContent = 'High';
        badge.style.background = 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
    } else if (data.confidence >= 0.5) {
        badge.textContent = 'Medium';
        badge.style.background = 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
    } else {
        badge.textContent = 'Low';
        badge.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
    
    // Display probabilities
    displayProbabilities(data.probabilities);
    
    // Set timestamp
    const timestamp = new Date(data.predicted_at).toLocaleString();
    document.getElementById('mlPredictedAt').textContent = timestamp;
    
    // Show results
    document.getElementById('mlResultsCard').style.display = 'block';
    
    // Smooth scroll
    setTimeout(() => {
        document.getElementById('mlResultsCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function displayProbabilities(probabilities) {
    const container = document.getElementById('probabilityBars');
    container.innerHTML = '';
    
    // Sort by probability
    const sorted = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);
    
    sorted.forEach(([style, probability]) => {
        const percentage = (probability * 100).toFixed(1);
        
        const barDiv = document.createElement('div');
        barDiv.className = 'probability-bar';
        barDiv.innerHTML = `
            <div class="probability-label">${style}</div>
            <div class="probability-track">
                <div class="probability-fill" style="width: 0%">
                    <span class="probability-value">${percentage}%</span>
                </div>
            </div>
        `;
        container.appendChild(barDiv);
        
        // Animate width
        setTimeout(() => {
            const fill = barDiv.querySelector('.probability-fill');
            fill.style.width = percentage + '%';
        }, 100);
    });
}

// ============================================
// STEP 3: RECOMMENDATIONS
// ============================================

async function generateRecommendations() {
    if (!currentStudentId) {
        showToast('Please load a student first', 'error');
        return;
    }
    
    if (!currentMLPrediction) {
        showToast('Please classify learning style first', 'error');
        return;
    }
    
    const topic = document.getElementById('topicInput').value.trim();
    const maxRecs = parseInt(document.getElementById('maxRecsInput').value);
    
    // Show loading
    document.getElementById('recommendationsLoading').style.display = 'flex';
    document.getElementById('recommendationsDisplay').style.display = 'none';
    document.getElementById('generateBtn').disabled = true;
    
    try {
        const requestBody = {
            student_id: currentStudentId,
            max_recommendations: maxRecs
        };
        
        if (topic) {
            requestBody.topic = topic;
        }
        
        console.log('Requesting recommendations with:', requestBody);
        
        const response = await fetch(`${API_BASE_URL}/recommendations/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            throw new Error(`Failed to generate recommendations: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Full API Response:', data);
        console.log('Response keys:', Object.keys(data));
        
        // Try different possible response formats
        let recommendations = [];
        
        if (data.recommendations) {
            recommendations = data.recommendations;
            console.log('Found recommendations in data.recommendations');
        } else if (Array.isArray(data)) {
            recommendations = data;
            console.log('Response is an array');
        } else if (data.results) {
            recommendations = data.results;
            console.log('Found recommendations in data.results');
        } else if (data.data) {
            recommendations = data.data;
            console.log('Found recommendations in data.data');
        }
        
        console.log('Extracted recommendations:', recommendations);
        console.log('Recommendations count:', recommendations.length);
        
        // Display recommendations
        displayRecommendations(recommendations);
        
        if (recommendations.length === 0) {
            showToast('No recommendations found. The student may not have struggles that match available resources.', 'error');
        } else {
            showToast(`Generated ${recommendations.length} recommendations`, 'success');
        }
        
    } catch (error) {
        console.error('Failed to generate recommendations:', error);
        showToast('Failed to generate recommendations: ' + error.message, 'error');
    } finally {
        document.getElementById('recommendationsLoading').style.display = 'none';
        document.getElementById('generateBtn').disabled = false;
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');
    container.innerHTML = '';
    
    console.log('Displaying recommendations:', recommendations);
    
    // Handle undefined or empty recommendations
    if (!recommendations || !Array.isArray(recommendations) || recommendations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No recommendations found. The system may need more data or the student may not have matching resources.</p>';
        document.getElementById('recommendationsCount').textContent = '0 resources found';
        document.getElementById('recommendationsDisplay').style.display = 'block';
        return;
    }
    
    // Update count
    document.getElementById('recommendationsCount').textContent = `${recommendations.length} resources found`;
    
    recommendations.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.style.opacity = '0';
        card.style.animation = 'fadeInUp 0.5s ease-out forwards';
        card.style.animationDelay = `${index * 0.1}s`;
        
        console.log('Processing recommendation:', rec);
        
        // Handle different API response formats
        let resource, relevanceScore, reason;
        
        // Check if rec has resource property (nested format)
        if (rec.resource) {
            resource = rec.resource;
            relevanceScore = rec.relevance_score || rec.score || 0;
            reason = rec.reason || 'Recommended based on your learning style';
        } 
        // Check if rec IS the resource (flat format)
        else if (rec.title || rec.resource_id) {
            resource = rec;
            relevanceScore = rec.relevance_score || rec.score || 0.85;
            reason = rec.reason || 'Recommended based on your learning style';
        }
        // Fallback
        else {
            console.warn('Unknown recommendation format:', rec);
            resource = {};
            relevanceScore = 0;
            reason = 'Recommended resource';
        }
        
        // Safely extract resource properties
        const title = resource.title || 'Untitled Resource';
        const resourceType = resource.resource_type || 'Resource';
        const estimatedTime = resource.estimated_duration || resource.estimated_time_minutes || 15;
        const difficultyLevel = resource.difficulty_level || 'Medium';
        const avgRating = resource.avg_helpfulness_rating || resource.avg_rating || 4.0;
        
        card.innerHTML = `
            <div class="recommendation-header">
                <div>
                    <div class="recommendation-title">${title}</div>
                    <span class="recommendation-type">${resourceType}</span>
                </div>
                <div class="relevance-score">${relevanceScore.toFixed(2)}</div>
            </div>
            
            <div class="recommendation-details">
                <div class="detail-badge">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    ${estimatedTime} min
                </div>
                <div class="detail-badge">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                    </svg>
                    ${difficultyLevel}
                </div>
                <div class="detail-badge">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                    ${avgRating.toFixed(1)}
                </div>
            </div>
            
            <p class="recommendation-reason">${reason}</p>
        `;
        
        container.appendChild(card);
    });
    
    console.log('Added', recommendations.length, 'cards to container');
    console.log('Container HTML length:', container.innerHTML.length);
    console.log('Container children count:', container.children.length);
    
    // Make sure Step 3 card is visible
    const step3Card = document.getElementById('step3Card');
    if (step3Card) {
        step3Card.style.display = 'block';
        console.log('Step 3 card made visible');
    }
    
    // Make sure display is visible
    const displaySection = document.getElementById('recommendationsDisplay');
    displaySection.style.display = 'block';
    
    console.log('Display section visibility:', displaySection.style.display);
    console.log('Display section exists:', !!displaySection);
    console.log('Display section offsetHeight:', displaySection.offsetHeight);
    
    // Smooth scroll
    setTimeout(() => {
        displaySection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// ============================================
// ANALYTICS CHARTS
// ============================================

async function loadCharts() {
    try {
        const response = await fetch(`${API_BASE_URL}/system/stats`);
        const data = await response.json();
        
        // Learning Style Distribution Chart
        if (data.learning_style_distribution) {
            createLearningStyleChart(data.learning_style_distribution);
        }
        
        // Struggle Topics Chart
        if (data.top_struggle_topics && Array.isArray(data.top_struggle_topics)) {
            createStruggleTopicsChart(data.top_struggle_topics);
        }
        
    } catch (error) {
        console.error('Failed to load charts:', error);
    }
}

function createLearningStyleChart(distribution) {
    try {
        const ctx = document.getElementById('learningStyleChart').getContext('2d');
        
        if (learningStyleChart) {
            learningStyleChart.destroy();
        }
        
        // Handle empty or invalid data
        if (!distribution || Object.keys(distribution).length === 0) {
            distribution = { 'No Data': 1 };
        }
        
        const styles = Object.keys(distribution);
        const counts = Object.values(distribution);
        
        learningStyleChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: styles,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(79, 172, 254, 0.8)',
                    'rgba(67, 233, 123, 0.8)',
                    'rgba(250, 112, 154, 0.8)'
                ],
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 2
            }]
        },
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
                }
            }
        }
    });
    } catch (error) {
        console.error('Failed to create learning style chart:', error);
    }
}

function createStruggleTopicsChart(topics) {
    try {
        const ctx = document.getElementById('struggleTopicsChart').getContext('2d');
        
        if (struggleTopicsChart) {
            struggleTopicsChart.destroy();
        }
        
        // Handle empty or invalid data
        if (!topics || !Array.isArray(topics) || topics.length === 0) {
            topics = [
                { topic: 'No data', count: 0 }
            ];
        }
        
        const labels = topics.map(t => t.topic || 'Unknown');
        const counts = topics.map(t => t.count || 0);
        
        struggleTopicsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Struggles',
                data: counts,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
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
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error('Failed to create struggle topics chart:', error);
    }
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

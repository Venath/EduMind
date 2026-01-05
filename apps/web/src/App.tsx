import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css'

function App() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    students: 0,
    courses: 0,
    resources: 0,
    completionRate: 0
  });
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const dropdownTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleDropdownEnter = () => {
    if (dropdownTimeoutRef.current) {
      clearTimeout(dropdownTimeoutRef.current);
    }
    setProfileDropdownOpen(true);
  };

  const handleDropdownLeave = () => {
    dropdownTimeoutRef.current = setTimeout(() => {
      setProfileDropdownOpen(false);
    }, 150);
  };

  const handleAdminLogin = () => {
    navigate('/admin-signin');
    setProfileDropdownOpen(false);
  };

  const handleUserLogin = () => {
    navigate('/user-signin');
    setProfileDropdownOpen(false);
  };

  useEffect(() => {
    // Simulate loading stats
    const loadStats = async () => {
      setStats({
        students: 1250,
        courses: 48,
        resources: 8500,
        completionRate: 87
      });
    };

    setTimeout(loadStats, 1000);
  }, []);

  const scrollToSection = (sectionId: string) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="App">
      {/* Navigation */}
      {/* <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <div className="logo-icon">
              <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="url(#navGradient)" strokeWidth="3"/>
                <path d="M24 14 L24 34 M14 24 L34 24" stroke="url(#navGradient)" strokeWidth="3" strokeLinecap="round"/>
                <defs>
                  <linearGradient id="navGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor:"#667eea"}}/>
                    <stop offset="100%" style={{stopColor:"#764ba2"}}/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <span>EduMind LMS</span>
          </div>
          <div className="nav-links">
            <button className="nav-link" onClick={() => scrollToSection('dashboard')}>Dashboard</button>
            <button className="nav-link" onClick={() => scrollToSection('courses')}>Courses</button>
            <button className="nav-link" onClick={() => scrollToSection('resources')}>Resources</button>
            <button className="nav-link" onClick={() => scrollToSection('analytics')}>Analytics</button>
            <button className="nav-button">Get Started</button>
            <div className="nav-profile-wrapper"
              onMouseEnter={handleDropdownEnter}
              onMouseLeave={handleDropdownLeave}
            >
              <button 
                className="nav-profile-icon" 
                title="User Profile"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </button>
              {profileDropdownOpen && (
                <div className="profile-dropdown">
                  <button className="dropdown-item" onClick={handleAdminLogin}>Login as Admin</button>
                  <button className="dropdown-item" onClick={handleUserLogin}>Login as User</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav> */}

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content-wrapper">
          <div className="hero-content">
            <div className="system-badge">
              <div className="badge-pulse"></div>
              <span>System Online</span>
            </div>
            <h1 className="hero-title">
              Welcome to <span className="gradient-text">EduMind LMS</span>
            </h1>
            <p className="hero-subtitle">
              Your intelligent learning management system powered by AI. 
              Discover personalized courses, track progress, and achieve your learning goals.
            </p>
            <div className="hero-actions">
              <button className="btn-primary-modern" onClick={() => scrollToSection('courses')}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14"/>
                  <path d="m12 5 7 7-7 7"/>
                </svg>
                <span>Explore Courses</span>
              </button>
              <button className="btn-secondary-modern" onClick={() => scrollToSection('dashboard')}>
                <span>View Dashboard</span>
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="ai-visualization">
              <div className="brain-icon">
                <svg width="200" height="200" viewBox="0 0 200 200" fill="none">
                  <circle cx="100" cy="100" r="80" stroke="url(#brainGradient)" strokeWidth="2" opacity="0.3"/>
                  <circle cx="100" cy="100" r="60" stroke="url(#brainGradient)" strokeWidth="2" opacity="0.5"/>
                  <circle cx="100" cy="100" r="40" stroke="url(#brainGradient)" strokeWidth="2" opacity="0.7"/>
                  <circle cx="100" cy="100" r="25" fill="url(#brainGradient)"/>
                  <defs>
                    <linearGradient id="brainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style={{stopColor:"#667eea"}}/>
                      <stop offset="100%" style={{stopColor:"#764ba2"}}/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <p className="ai-description">AI-Powered Learning Platform</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Dashboard */}
      <section id="dashboard" className="stats-section">
        <div className="main-container">
          <div className="stats-dashboard">
            <div className="stat-card-modern" data-color="purple">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div className="stat-info">
                <div className="stat-value">{stats.students.toLocaleString()}</div>
                <div className="stat-label">Total Students</div>
              </div>
            </div>

            <div className="stat-card-modern" data-color="blue">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <div className="stat-info">
                <div className="stat-value">{stats.courses}</div>
                <div className="stat-label">Active Courses</div>
              </div>
            </div>

            <div className="stat-card-modern" data-color="green">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
              </div>
              <div className="stat-info">
                <div className="stat-value">{stats.resources.toLocaleString()}</div>
                <div className="stat-label">Learning Resources</div>
              </div>
            </div>

            <div className="stat-card-modern" data-color="orange">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <div className="stat-info">
                <div className="stat-value">{stats.completionRate}%</div>
                <div className="stat-label">Completion Rate</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Courses Section */}
      <section id="courses" className="courses-section">
        <div className="main-container">
          <div className="workflow-header">
            <div className="step-badge">Featured</div>
            <h2>Explore Our Courses</h2>
            <p>Hand-picked courses designed to accelerate your learning journey</p>
          </div>

          <div className="courses-grid">
            <div className="course-card">
              <div className="course-header">
                <div className="course-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <span className="course-badge">Beginner</span>
              </div>
              <h3 className="course-title">Introduction to Machine Learning</h3>
              <p className="course-description">
                Learn the fundamentals of ML algorithms, data preprocessing, and model evaluation.
              </p>
              <div className="course-meta">
                <div className="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <span>8 hours</span>
                </div>
                <div className="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  <span>1,234 students</span>
                </div>
              </div>
              <button className="btn-course">Enroll Now</button>
            </div>

            <div className="course-card">
              <div className="course-header">
                <div className="course-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                    <line x1="12" y1="22.08" x2="12" y2="12"/>
                  </svg>
                </div>
                <span className="course-badge">Intermediate</span>
              </div>
              <h3 className="course-title">Full-Stack Web Development</h3>
              <p className="course-description">
                Master modern web technologies including React, Node.js, and database management.
              </p>
              <div className="course-meta">
                <div className="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <span>12 hours</span>
                </div>
                <div className="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  <span>2,456 students</span>
                </div>
              </div>
              <button className="btn-course">Enroll Now</button>
            </div>

            <div className="course-card">
              <div className="course-header">
                <div className="course-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <span className="course-badge">Advanced</span>
              </div>
              <h3 className="course-title">Deep Learning & Neural Networks</h3>
              <p className="course-description">
                Advanced course covering deep neural networks, CNNs, RNNs, and transfer learning.
              </p>
              <div className="course-meta">
                <div className="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <span>16 hours</span>
                </div>
                <div className="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  <span>856 students</span>
                </div>
              </div>
              <button className="btn-course">Enroll Now</button>
            </div>
          </div>
        </div>
      </section>

      {/* Resources Section */}
      <section id="resources" className="resources-section">
        <div className="main-container">
          <div className="workflow-header">
            <div className="step-badge">Library</div>
            <h2>Learning Resources</h2>
            <p>Access thousands of curated resources to support your learning</p>
          </div>

          <div className="resources-grid">
            <div className="resource-card">
              <div className="resource-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
              </div>
              <h3>Documentation</h3>
              <p>Comprehensive guides and technical documentation</p>
              <span className="resource-count">2,450+ docs</span>
            </div>

            <div className="resource-card">
              <div className="resource-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="23 7 16 12 23 17 23 7"/>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                </svg>
              </div>
              <h3>Video Tutorials</h3>
              <p>Step-by-step video lessons from experts</p>
              <span className="resource-count">1,200+ videos</span>
            </div>

            <div className="resource-card">
              <div className="resource-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h3>Interactive Exercises</h3>
              <p>Practice with hands-on coding challenges</p>
              <span className="resource-count">3,800+ exercises</span>
            </div>

            <div className="resource-card">
              <div className="resource-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <h3>E-Books</h3>
              <p>Downloadable books and study materials</p>
              <span className="resource-count">850+ books</span>
            </div>
          </div>
        </div>
      </section>

      {/* Analytics Section */}
      <section id="analytics" className="analytics-section">
        <div className="main-container">
          <div className="workflow-header">
            <div className="step-badge">Insights</div>
            <h2>Learning Analytics</h2>
            <p>Track your progress and optimize your learning path</p>
          </div>

          <div className="analytics-buttons">
            <button className="analytics-btn">Learning Style Analytics</button>
            <button className="analytics-btn">Engagement Analytics</button>
            <button className="analytics-btn">Performance Analytics</button>
          </div>

          <div className="analytics-grid">
            <div className="analytics-card">
              <h3>Progress Overview</h3>
              <div className="progress-visual">
                <div className="progress-ring">
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none"/>
                    <circle cx="60" cy="60" r="50" stroke="url(#progressGradient)" strokeWidth="8" 
                            fill="none" strokeDasharray="314" strokeDashoffset="94" 
                            transform="rotate(-90 60 60)" strokeLinecap="round"/>
                    <defs>
                      <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style={{stopColor:"#667eea"}}/>
                        <stop offset="100%" style={{stopColor:"#764ba2"}}/>
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="progress-text">
                    <span className="progress-value">70%</span>
                    <span className="progress-label">Complete</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="analytics-card">
              <h3>Recent Activity</h3>
              <div className="activity-list">
                <div className="activity-item">
                  <div className="activity-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  </div>
                  <div className="activity-content">
                    <p>Completed "Introduction to Python"</p>
                    <span>2 hours ago</span>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                      <path d="M2 17l10 5 10-5"/>
                      <path d="M2 12l10 5 10-5"/>
                    </svg>
                  </div>
                  <div className="activity-content">
                    <p>Started "Machine Learning Basics"</p>
                    <span>5 hours ago</span>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                      <circle cx="9" cy="7" r="4"/>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                  </div>
                  <div className="activity-content">
                    <p>Joined study group</p>
                    <span>1 day ago</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
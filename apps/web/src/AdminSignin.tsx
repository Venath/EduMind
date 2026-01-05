import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminSignin.css';

function AdminSignin() {
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Simulate login delay
    setTimeout(() => {
      setIsLoading(false);

      // Manual validation
      if (username === 'admin' && password === 'admin') {
        navigate('/admin');
      } else {
        setError('Invalid username or password');
      }
    }, 800);
  };

  return (
    <div className="signin-container admin-signin">
      <div className="signin-wrapper">
        {/* Background Elements */}
        <div className="background-gradient"></div>
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>

        {/* Signin Card */}
        <div className="signin-card">
          {/* Header */}
          <div className="signin-header">
            <div className="logo-circle admin-logo">
              <svg width="40" height="40" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="url(#adminGradient)" strokeWidth="3"/>
                <path d="M24 14 L24 34 M14 24 L34 24" stroke="url(#adminGradient)" strokeWidth="3" strokeLinecap="round"/>
                <defs>
                  <linearGradient id="adminGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor:"#667eea"}}/>
                    <stop offset="100%" style={{stopColor:"#764ba2"}}/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h1 className="signin-title">Admin Portal</h1>
            <p className="signin-subtitle">Sign in to your admin account</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="signin-form">
            {/* Username Field */}
            <div className="form-group">
              <label htmlFor="username" className="form-label">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="4" width="20" height="16" rx="2"/>
                  <path d="m22 6-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 6"/>
                </svg>
                Username
              </label>
              <input
                type="text"
                id="username"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder=""
                required
              />
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password" className="form-label">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                Password
              </label>
              <input
                type="password"
                id="password"
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="form-actions">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="checkbox-input"
                />
                <span>Remember me</span>
              </label>
              <button type="button" className="forgot-link">Forgot password?</button>
            </div>

            {/* Error message */}
            {error && <p className="signin-error">{error}</p>}

            {/* Submit Button */}
            <button type="submit" className="signin-button" disabled={isLoading}>
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Signing in...
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12l5 5 10-10"/>
                  </svg>
                  Sign in as Admin
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="form-divider">
            <span>or continue as</span>
          </div>

          {/* User Signin Link */}
          <button
            type="button"
            className="user-signin-link"
            onClick={() => navigate('/user-signin')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            Sign in as User
          </button>

          {/* Footer */}
          <div className="signin-footer">
            <button type="button" className="back-button" onClick={() => navigate('/')}>
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminSignin;

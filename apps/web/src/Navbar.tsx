import { useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import "./Navbar.css"

function Navbar() {
  const navigate = useNavigate()

  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false)
  const dropdownTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleDropdownEnter = () => {
    if (dropdownTimeoutRef.current) {
      clearTimeout(dropdownTimeoutRef.current)
    }
    setProfileDropdownOpen(true)
  }

  const handleDropdownLeave = () => {
    dropdownTimeoutRef.current = setTimeout(() => {
      setProfileDropdownOpen(false)
    }, 150)
  }

  const handleAdminLogin = () => {
    navigate("/admin-signin")
    setProfileDropdownOpen(false)
  }

  const handleUserLogin = () => {
    navigate("/user-signin")
    setProfileDropdownOpen(false)
  }

  const scrollToSection = (sectionId: string) => {
    document
      .getElementById(sectionId)
      ?.scrollIntoView({ behavior: "smooth" })
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Logo */}
        <div className="nav-logo" onClick={() => navigate("/")}>
          <div className="logo-icon">
            <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
              <circle
                cx="24"
                cy="24"
                r="20"
                stroke="url(#navGradient)"
                strokeWidth="3"
              />
              <path
                d="M24 14 L24 34 M14 24 L34 24"
                stroke="url(#navGradient)"
                strokeWidth="3"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient
                  id="navGradient"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="100%"
                >
                  <stop offset="0%" stopColor="#667eea" />
                  <stop offset="100%" stopColor="#764ba2" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span>EduMind LMS</span>
        </div>

        {/* Navigation Links */}
        <div className="nav-links">
          <button
            className="nav-link"
            onClick={() => scrollToSection("dashboard")}
          >
            Dashboard
          </button>
          <button
            className="nav-link"
            onClick={() => scrollToSection("courses")}
          >
            Courses
          </button>
          <button
            className="nav-link"
            onClick={() => scrollToSection("resources")}
          >
            Resources
          </button>
          <button
            className="nav-link"
            onClick={() => scrollToSection("analytics")}
          >
            Analytics
          </button>

          <button
            className="nav-button"
            onClick={() => navigate("/engagement")}
          >
            Get Started
          </button>

          {/* Profile Dropdown */}
          <div
            className="nav-profile-wrapper"
            onMouseEnter={handleDropdownEnter}
            onMouseLeave={handleDropdownLeave}
          >
            <button className="nav-profile-icon" title="User Profile">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </button>

            {profileDropdownOpen && (
              <div className="profile-dropdown">
                <button
                  className="dropdown-item"
                  onClick={handleAdminLogin}
                >
                  Login as Admin
                </button>
                <button
                  className="dropdown-item"
                  onClick={handleUserLogin}
                >
                  Login as User
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

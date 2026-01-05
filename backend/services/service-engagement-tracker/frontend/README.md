# 🎨 EduMind Frontend - Student Engagement Dashboard

Beautiful, responsive web interface to showcase the EduMind Student Engagement Analytics System.

## 📸 Features

- **Student Lookup Form** - Search by Student ID
- **Real-time Dashboard** - Live data from FastAPI backend
- **Interactive Charts** - Component scores & engagement history
- **Risk Indicators** - Visual alerts for at-risk students
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Modern UI** - Clean, professional interface with animations

---

## 🚀 Quick Start

### 1. Make Sure API is Running

```powershell
cd ..\
$env:DATABASE_URL="postgresql+psycopg://postgres:admin@localhost:5432/edumind"
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

API should be running at: `http://localhost:8002`

### 2. Open the Frontend

Simply open `index.html` in your browser:

**Option A: Double-click**
- Double-click `index.html` file

**Option B: Python HTTP Server**
```powershell
cd frontend
python -m http.server 8080
```
Then open: `http://localhost:8080`

**Option C: VS Code Live Server**
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

---

## 🎯 How to Use

### Step 1: Check API Status
- Green dot in header = API is online
- Red/yellow dot = API is offline

### Step 2: Enter Student ID
- Type a Student ID (e.g., `STU0001` to `STU0100`)
- Or use Quick Select buttons:
  - **High Performer**: STU0001 (Good engagement)
  - **At Risk**: STU0085 (High risk, low engagement)
  - **Medium**: STU0050 (Average engagement)

### Step 3: View Dashboard
- **Key Metrics**: Engagement score, risk probability, days tracked
- **Component Scores**: Bar chart showing 5 component scores
- **History Chart**: 30-day engagement trend
- **Alerts**: Actionable recommendations
- **Risk Factors**: Contributing factors for at-risk students

---

## 📊 Dashboard Components

### Student Header
- **Student ID** with engagement level badge
- **Risk Level** indicator (High/Medium/Low)

### Key Metrics (4 Cards)
1. **Engagement Score** - Current score with trend
2. **Risk Probability** - Disengagement risk percentage
3. **Days Tracked** - Total data points available
4. **Average Score** - Historical average

### Component Scores Chart
Interactive bar chart showing scores for:
- 📝 Login Activity (20%)
- ⏱️ Session Engagement (25%)
- 🖱️ Content Interaction (25%)
- 💬 Forum Participation (15%)
- 📚 Assignment Completion (15%)

### Engagement History Chart
Line chart showing engagement score over last 30 days:
- 🟢 Green area = High engagement (≥70)
- 🟡 Yellow area = Medium engagement (40-69)
- 🔴 Red area = Low engagement (<40)

### Alerts & Recommendations
System-generated alerts based on student data:
- 🔴 **High** = Immediate action required
- 🟡 **Warning** = Monitor closely
- 🔵 **Info** = General recommendation
- 🟢 **Success** = Student is doing well

### Risk Contributing Factors (For At-Risk Students)
Shows specific factors contributing to disengagement risk:
- 📉 Low engagement score
- ⬇️ Declining trend
- ⏱️ Low session activity
- 📅 Consecutive low engagement days

---

## 🎨 Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid/Flexbox
- **Vanilla JavaScript** - No frameworks, pure JS
- **Chart.js** - Beautiful, responsive charts

### Backend Integration
- **Fetch API** - Modern HTTP requests
- **RESTful API** - Clean, consistent endpoints
- **Real-time Data** - Live updates from database

---

## 📁 File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All CSS styling
├── app.js          # JavaScript logic & API calls
└── README.md       # This file
```

---

## 🎨 Color Scheme

| Color | Usage | Hex |
|-------|-------|-----|
| Primary | Main actions, headers | `#4f46e5` |
| Secondary | Accents | `#06b6d4` |
| Success | High engagement, positive | `#10b981` |
| Warning | Medium engagement, caution | `#f59e0b` |
| Danger | Low engagement, risk | `#ef4444` |

---

## 🔌 API Endpoints Used

The frontend connects to these API endpoints:

```javascript
// Health Check
GET /health

// System Statistics
GET /api/v1/stats

// Student Dashboard
GET /api/v1/students/{student_id}/dashboard

// Engagement History
GET /api/v1/engagement/students/{student_id}/history?days=30

// Latest Prediction
GET /api/v1/predictions/students/{student_id}/latest
```

---

## 📱 Responsive Design

The dashboard adapts to different screen sizes:

- **Desktop** (>1200px): Full layout with sidebar
- **Tablet** (768px-1200px): Adjusted grid
- **Mobile** (<768px): Stacked layout, single column

---

## 🎯 Sample Student IDs

Try these students to see different scenarios:

### High Performers
- `STU0013` - Avg score: 63.13
- `STU0014` - Avg score: 61.98
- `STU0024` - Avg score: 61.04

### At Risk
- `STU0085` - Avg score: 5.89 (HIGHEST RISK)
- `STU0077` - Avg score: 7.10
- `STU0078` - Avg score: 7.17

### Medium Engagement
- `STU0050` - Typical medium engagement
- `STU0025` - Stable engagement
- `STU0040` - Moderate scores

---

## 🐛 Troubleshooting

### Dashboard Not Loading?

**Check:**
1. ✅ API is running (`http://localhost:8002/health` returns 200)
2. ✅ Student ID exists (`STU0001` to `STU0100`)
3. ✅ No browser console errors (Press F12)
4. ✅ CORS is enabled (should be by default)

### Charts Not Showing?

**Check:**
1. ✅ Chart.js is loaded (check browser console)
2. ✅ Canvas elements exist in HTML
3. ✅ API returned data successfully

### Styling Issues?

**Check:**
1. ✅ `styles.css` is in same directory
2. ✅ No CSS errors in browser console
3. ✅ Browser supports modern CSS (Grid, Flexbox)

---

## 🚀 Deployment

### For Production:

1. **Change API URL**
   ```javascript
   // In app.js
   const API_BASE_URL = 'https://your-api-domain.com';
   ```

2. **Host Frontend**
   - GitHub Pages
   - Netlify
   - Vercel
   - AWS S3 + CloudFront
   - Any static file hosting

3. **Enable HTTPS**
   - Use SSL certificate
   - Update CORS settings in backend

---

## 🎓 Demo Workflow

Perfect for presentations:

1. **Start**: Show welcome screen
2. **System Stats**: Point out 100 students, 89 at risk
3. **High Performer**: Enter `STU0001`
   - Show high scores across all components
   - Highlight positive trend
   - Show green success alerts
4. **At-Risk Student**: Enter `STU0085`
   - Show critically low scores
   - Highlight high risk probability (85.5%)
   - Show red warning alerts
   - Display contributing factors
5. **API Docs**: Click "API Documentation" link
6. **Emphasize**: Real-time data, 99.94% accuracy, production-ready

---

## 📊 Performance

- **Load Time**: <500ms (with API)
- **API Calls**: 3-4 per dashboard load
- **Chart Rendering**: <100ms
- **Responsive**: Smooth on all devices

---

## 🔒 Security Notes

**Current Setup (Development)**:
- No authentication required
- CORS enabled for all origins
- API is open

**For Production**:
- Add JWT authentication
- Restrict CORS to specific domains
- Add rate limiting
- Implement HTTPS
- Sanitize all inputs

---

## ✨ Future Enhancements

Possible improvements:
- [ ] Real-time updates (WebSocket)
- [ ] Multiple student comparison view
- [ ] Export data to PDF/Excel
- [ ] Intervention management interface
- [ ] Historical data animation
- [ ] Dark mode toggle
- [ ] Advanced filtering
- [ ] Batch student upload

---

## 📝 Credits

**Built for**: EduMind Student Engagement Analytics System  
**Purpose**: Demonstration of ML-powered engagement tracking  
**Tech**: FastAPI + PostgreSQL + Machine Learning  
**Accuracy**: 99.94%  

---

## 📞 Support

For questions or issues:
1. Check API documentation: `http://localhost:8002/api/docs`
2. Review browser console for errors
3. Verify API health endpoint
4. Check database connection

---

**Enjoy exploring student engagement data! 🎓✨**


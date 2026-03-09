# EduMind – Run on Another Computer (Full Guide)

This guide lets you copy the project to a **new computer** and run it exactly like on your current laptop: **LMS (Institute A)** with 5 students, **LMS2 (Institute B)** with 20 students, and the EduMind dashboard.

- **Windows users:** For a full step-by-step guide with small steps (including after unzipping without venv/node_modules), see **[RUN_ON_WINDOWS.md](RUN_ON_WINDOWS.md)**.

---

## What You Need Before Starting

| Software | Version | Why |
|----------|---------|-----|
| **Python** | 3.10 or 3.11 (recommended) | Backend services (engagement, learning-style, XAI, LMS, LMS2) |
| **Node.js** | 18 or 20 (LTS) | EduMind web UI (`npm` / `npx`) |
| **PostgreSQL** | 14 or 15 | Databases for engagement, learning-style, and XAI services |
| **Git** (optional) | Any | Only if you copy the project via git clone |

---

## Step 1: Copy the Project to the New Computer

- **Option A:** Copy the whole `edumind` folder (e.g. via USB, cloud, or zip) to the new PC.  
  Example path: `C:\Projects\edumind`
- **Option B:** If you use Git: clone the repo on the new PC into `C:\Projects\edumind` (or your chosen path).

Use the **same folder name** (e.g. `edumind`) so the commands below work as-is. If you use a different path, replace `C:\Projects\edumind` in all steps with your path.

---

## Step 2: Install PostgreSQL and Create Databases

1. Install PostgreSQL if not already installed.
2. Open **pgAdmin** or **psql** and create **two databases** manually (same user, e.g. `postgres`):

```sql
CREATE DATABASE edumind;
CREATE DATABASE edumind_learning_style;
```

3. Note your PostgreSQL:
   - **Username** (often `postgres`)
   - **Password**
   - **Port** (usually `5432`)
   - **Host** (usually `localhost`)

If your password or user is different, you will set them in **Step 4** and **Step 5** using `.env` or environment variables.

The XAI service can create its own databases automatically during `init_db.py`:

- `xai-prediction`
- `temporary_students_db`

---

## Step 3: Create Python Virtual Environments and Install Dependencies

Open **PowerShell** or **Command Prompt**. Run these **one by one** (wait for each to finish).

### 3.1 Engagement Tracker (EduMind)

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-engagement-tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2 Learning Style (EduMind)

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-learning-style
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3.3 XAI Prediction (EduMind)

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-xai-prediction
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3.4 LMS (Institute A)

```powershell
cd C:\Projects\edumind\LMS
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3.5 LMS2 (Institute B)

```powershell
cd C:\Projects\edumind\LMS2
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 4: Configure Databases (Only If Not Using Defaults)

Default PostgreSQL connection used by the code:

- **User:** `postgres`  
- **Password:** `admin`  
- **Host:** `localhost`  
- **Port:** `5432`

If your setup is different:

**Engagement Tracker**  
Create or edit:

`EduMind\backend\services\service-engagement-tracker\.env`

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/edumind
```

**Learning Style**  
Create or edit:

`EduMind\backend\services\service-learning-style\.env`

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/edumind_learning_style
```

**XAI Prediction**  
Create or edit:

`EduMind\backend\services\service-xai-prediction\.env`

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/xai-prediction
TEMP_STUDENTS_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/temporary_students_db
```

Replace `YOUR_PASSWORD` and `postgres` if your user is different.  
LMS and LMS2 use **SQLite** by default (`lms.db` and `lms2.db` in their folders); no PostgreSQL config needed for them.

---

## Step 5: Initialize Databases (First Time Only)

Do this **once** on the new computer (or after resetting the DBs).

### 5.1 Engagement Tracker – create tables

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-engagement-tracker
venv\Scripts\activate
python scripts/init_db.py
```

### 5.2 Learning Style – create tables

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-learning-style
venv\Scripts\activate
python scripts/init_db.py create
```

### 5.3 XAI Prediction – create databases and tables

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-xai-prediction
.venv\Scripts\activate
python scripts/init_db.py
```

This creates and initializes:

- `xai-prediction`
- `temporary_students_db`

LMS and LMS2 create their SQLite DB and tables automatically when you run the seed script or start the server.

---

## Step 6: Install Node Dependencies for EduMind Web UI

The EduMind frontend is in a pnpm monorepo. Install from the **EduMind** root (recommended):

```powershell
cd C:\Projects\edumind\EduMind
pnpm install
```

If you don't have pnpm: `npm install -g pnpm`. Then run the web app from `EduMind\apps\web` with `pnpm run dev`.

Optional: create `EduMind\apps\web\.env.local` if you want to point to different backend URLs (usually not needed on same machine):

```env
VITE_ENGAGEMENT_TRACKER_API_URL=http://localhost:8005
VITE_LEARNING_STYLE_API_URL=http://localhost:8006
VITE_XAI_API_URL=http://localhost:8004
```

---

## Step 7: Start All Services (Correct Order)

Start in this order. Use **6 separate terminals** (or 6 tabs). Leave each running.

### Terminal 1 – Engagement Tracker (port 8005)

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-engagement-tracker
venv\Scripts\activate
uvicorn app.main:app --reload --port 8005
```

Wait until you see it is running (e.g. "Uvicorn running on http://...").

### Terminal 2 – Learning Style (port 8006)

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-learning-style
venv\Scripts\activate
uvicorn app.main:app --reload --port 8006
```

### Terminal 3 – XAI Prediction (port 8004)

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-xai-prediction
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8004
```

### Terminal 4 – EduMind Web UI (port 5174)

```powershell
cd C:\Projects\edumind\EduMind\apps\web
pnpm i
pnpm run dev
```

### Terminal 5 – LMS Institute A (port 8010)

```powershell
cd C:\Projects\edumind\LMS
venv\Scripts\activate
uvicorn app.main:app --reload --port 8010
```

### Terminal 6 – LMS2 Institute B (port 8011)

```powershell
cd C:\Projects\edumind\LMS2
venv\Scripts\activate
uvicorn app.main:app --reload --port 8011
```

---

## Step 8: Seed Demo Data (First Time Only)

Run seeds **only after** Engagement Tracker (8005) and Learning Style (8006) are running.

### 8.1 Seed LMS (Institute A) – 5 students

```powershell
cd C:\Projects\edumind\LMS
venv\Scripts\activate
python scripts/seed_demo_data.py
```

This creates 5 users (e.g. student1…student5), courses, events, and learning-style profiles (STU0001–STU0005).

### 8.2 Seed LMS2 (Institute B) – 20 students

```powershell
cd C:\Projects\edumind\LMS2
venv\Scripts\activate
python scripts/seed_demo_data.py
```

This creates 20 users (e.g. student_b01…student_b20), courses, events, and learning-style profiles (STU0006–STU0025).

### 8.3 Seed Learning Style demo resources (optional)

For non-zero RESOURCES and RECOMMENDATIONS on the learning-style dashboard:

```powershell
cd C:\Projects\edumind\EduMind\backend\services\service-learning-style
venv\Scripts\activate
python scripts/seed_demo_data.py
```

---

## Step 9: Open the Apps in the Browser

| What | URL |
|------|-----|
| **EduMind dashboard (admin)** | http://localhost:5174/admin-signin |
| **EduMind (after login)** | http://localhost:5174 |
| **XAI API** | http://localhost:8004/health |
| **LMS (Institute A)** | http://localhost:8010/frontend/index.html |
| **LMS2 (Institute B)** | http://localhost:8011/frontend/index.html |

---

## Step 10: Logins

### EduMind admin (dashboard)

| Account | Username | Password | Sees |
|---------|----------|----------|------|
| Institute A | `admin` | `admin` | 5 students (STU0001–STU0005) |
| Institute B | `admin_b` | `admin_b` | 20 students (STU0006–STU0025) |

### LMS (Institute A) – student

- Any of: `student1` … `student5`  
- Password: `password123`

### LMS2 (Institute B) – student

- Any of: `student_b01` … `student_b20`  
- Password: `password123`

---

## Quick Checklist (New Computer)

- [ ] Python 3.10+ and Node 18+ installed  
- [ ] PostgreSQL installed; databases `edumind` and `edumind_learning_style` created  
- [ ] Project folder copied (e.g. `C:\Projects\edumind`)  
- [ ] Five Python venvs created and dependencies installed (engagement, learning-style, XAI, LMS, LMS2)  
- [ ] Engagement + Learning Style + XAI DBs initialized (`init_db.py`)  
- [ ] EduMind web: `pnpm install` in `EduMind` (or `EduMind\apps\web` after installing pnpm)  
- [ ] All 6 services started in order (8005 → 8006 → 8004 → vite → 8010 → 8011)  
- [ ] LMS seed run (5 students)  
- [ ] LMS2 seed run (20 students)  
- [ ] Login: admin / admin (Institute A) or admin_b / admin_b (Institute B) at http://localhost:5174/admin-signin  

---

## If Something Fails

- **“Database does not exist”**  
  Create `edumind` and `edumind_learning_style` in PostgreSQL (Step 2), then run XAI `python scripts/init_db.py` to create its databases.

- **“Connection refused” or “could not connect”**  
  Start Engagement Tracker (8005) and Learning Style (8006) first; then run the seed scripts. Start XAI (8004) before using the XAI page or XAI-backed dashboard stats.

- **“Port already in use”**  
  Another program is using that port. Close it or change the port in the `uvicorn` or `vite` command and in any config that references it.

- **LMS/LMS2 seed or XAI search fails when calling backend services**  
  Make sure Engagement Tracker, Learning Style, and XAI are running and that no firewall is blocking localhost ports 8005, 8006, and 8004.

---

## Summary: Run Order Every Time

1. Start **Engagement Tracker** (8005)  
2. Start **Learning Style** (8006)  
3. Start **XAI Prediction** (8004)  
4. Start **EduMind Web** (vite, 5174)  
5. Start **LMS** (8010)  
6. Start **LMS2** (8011)  
7. Open http://localhost:5174/admin-signin or http://localhost:8010/frontend/index.html (LMS) or http://localhost:8011/frontend/index.html (LMS2)

You only need to run the seed scripts once per machine (or when you want to reset demo data).

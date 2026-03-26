# Live Demo Plan — Smart Financial Monitoring System

**Duration:** 10–15 minutes
**Audience:** Instructor / Evaluators
**Format:** Live screen share

---

## Demo Checklist (Prepare Before)

- [ ] Application runs successfully (`python main.py`)
- [ ] GitHub repository is public and accessible
- [ ] Latest commit is pushed and CI/CD pipeline has completed
- [ ] GitHub Project board is set up with all sprints
- [ ] A test invoice image is ready (PNG with a visible price like `$45.99`)
- [ ] Browser open to GitHub Actions tab
- [ ] All dependencies installed

---

## Demo Script

### Section 1: GitHub Repository (2 min)

**Say:** "Let me start by showing the GitHub repository structure."

1. Open browser → Navigate to `https://github.com/YOUR_USERNAME/smart-finance-system`
2. Show the **file structure** in the root:
   - `main.py` — the full application source code
   - `requirements.txt` — all dependencies
   - `README.md` — complete project documentation
   - `.github/workflows/ci-cd.yml` — CI/CD pipeline config
   - `tests/` — automated unit tests
   - `docs/` — sprint report, risk register, demo plan

3. Click on `README.md` → show the feature table and architecture diagram

**Key point:** *"Everything needed to understand, run, and maintain this project is in one repository."*

---

### Section 2: CI/CD Pipeline (3 min)

**Say:** "Now let me show the automated CI/CD pipeline."

1. Click the **Actions** tab on GitHub
2. Show the **CI/CD Pipeline** workflow
3. Click on the most recent run → show all 5 jobs:
   - ✅ Code Quality Check (lint)
   - ✅ Unit Tests (14 tests)
   - ✅ Build & Package
   - ✅ Security Scan
   - ✅ Pipeline Summary
4. Click into **Unit Tests** job → show test output with 14 passing tests
5. Click into **Build** job → show artifact uploaded (zip package)

**Key point:** *"Every push to the repository automatically runs quality checks, tests, and builds a release package."*

---

### Section 3: Project Board (1 min)

**Say:** "Here's our sprint planning board."

1. Click the **Projects** tab on GitHub
2. Show the Kanban board with 4 columns: Backlog / In Progress / Review / Done
3. Show Sprint 6 items all in Done column
4. Reference `docs/sprint_report.md` for velocity data

**Key point:** *"We completed 6 sprints totaling 64 story points using Agile methodology."*

---

### Section 4: Live Application Demo (7 min)

**Say:** "Now let me run the application live."

#### Step 1 — Launch (30s)
```bash
python main.py
```
- Show the dark-themed login screen

#### Step 2 — Registration & Login (30s)
- Click **Register** → enter username: `demo` / password: `demo123`
- Show success message
- Click **Login** → show dashboard loads

#### Step 3 — Add Business (60s)
- Click **➕ Add Business**
- Enter name: `Sunrise Cafe`
- Select currency: `$ US Dollar`
- Select period: `Monthly`
- Enter budget: `5000`
- Show business appears in sidebar

#### Step 4 — Add Income (30s)
- Click **💰 Add Income**
- Enter: `3500`
- Show dashboard updates → Total Income: $3,500.00

#### Step 5 — Add Expenses (60s)
- Click **💸 Add Expense** → `800` → Category: `Rent`
- Click **💸 Add Expense** → `1200` → Category: `Salaries`
- Click **💸 Add Expense** → `300` → Category: `Supplies`
- Show pie chart updates in real time

#### Step 6 — OCR Bill Upload (60s)
- Click **📄 Upload Bill**
- Select prepared invoice image
- Show OCR detects amount automatically
- Select category → click OK
- Show expense added to dashboard

#### Step 7 — Alerts Demo (30s)
- Click **💸 Add Expense** → `3000` → `Marketing`
- Show red alert: *"⚠ Budget exceeded!"*
- Explain: *"The system automatically warns when spending exceeds the set budget."*

#### Step 8 — Export (60s)
- Click **📁 Export CSV** → save file → open it → show all transactions
- Click **📊 Export Excel** → show file auto-opens in Excel

#### Step 9 — Archive (30s)
- Click **🗂️ Open Archive**
- Show exported files listed
- Add a note: `"Monthly report reviewed"` → click Save Notes

---

## Talking Points

| Feature | What to say |
|---------|-------------|
| bcrypt passwords | "Passwords are hashed with bcrypt — never stored as plain text" |
| Auto-save | "Data is saved after every action — no manual save button needed" |
| OCR | "The system uses Tesseract OCR to read invoice images automatically" |
| Alerts | "Budget and loss alerts help owners make decisions before it's too late" |
| CI/CD | "14 unit tests run automatically on every commit via GitHub Actions" |
| Multi-business | "Users can manage multiple businesses from a single account" |

---

## Backup Plan (if live demo fails)

If the application cannot run:
1. Show recorded demo video (screen recording prepared beforehand)
2. Walk through source code in the repository
3. Show GitHub Actions results from last successful run

---

## Q&A Preparation

**Q: Why Python/tkinter instead of a web app?**
A: Desktop app is more appropriate for small business owners who don't have internet connectivity and prefer a local, offline tool with no subscription.

**Q: How is data secured?**
A: Passwords are hashed with bcrypt. Data is stored locally in JSON files — no cloud server means no data breach risk.

**Q: What happens if Tesseract isn't installed?**
A: The app shows an error message. Manual entry is always available as a fallback.

**Q: How would you scale this?**
A: Replace JSON storage with SQLite or PostgreSQL, add a web frontend, and host on cloud.

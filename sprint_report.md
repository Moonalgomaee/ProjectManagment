# Sprint Report — Smart Financial Monitoring System

## Project Info
- **Project:** Smart Financial Monitoring & Expense Management System
- **Start Date:** Sprint 1 — Week 1
- **Methodology:** Agile / Scrum (2-week sprints)

---

## Sprint Board Setup (GitHub Projects)

To create your sprint board on GitHub:
1. Go to your repository on GitHub
2. Click the **Projects** tab
3. Click **New project** → Select **Board** view
4. Create columns: `Backlog` | `In Progress` | `Review` | `Done`
5. Add issues for each user story below

---

## Product Backlog (User Stories)

| ID | User Story | Priority | Points | Sprint |
|----|------------|----------|--------|--------|
| US-01 | As a user, I can register an account with username and password | High | 3 | 1 |
| US-02 | As a user, I can log in securely | High | 3 | 1 |
| US-03 | As a user, I can add a new business with name, currency, period, and budget | High | 5 | 1 |
| US-04 | As a user, I can add income entries | High | 3 | 2 |
| US-05 | As a user, I can add expense entries with category | High | 3 | 2 |
| US-06 | As a user, I can view total income, expense, and net profit on a dashboard | High | 5 | 2 |
| US-07 | As a user, I receive automatic alerts when budget is exceeded | Medium | 3 | 3 |
| US-08 | As a user, I can see a pie chart of expenses by category | Medium | 5 | 3 |
| US-09 | As a user, I can see a line chart of financial overview | Medium | 3 | 3 |
| US-10 | As a user, I can upload a bill image and have the amount auto-detected via OCR | High | 8 | 4 |
| US-11 | As a user, I can export financial data as a CSV report | Medium | 5 | 5 |
| US-12 | As a user, I can export an Excel report that auto-opens | Medium | 5 | 5 |
| US-13 | As a user, I can view and search archived reports | Low | 3 | 5 |
| US-14 | As a user, I can add notes to archived reports | Low | 2 | 5 |
| US-15 | As a developer, automated tests run on every push via CI/CD | High | 5 | 6 |
| US-16 | As a developer, the pipeline reports lint, test, and build status | High | 3 | 6 |

---

## Sprint 1 — Foundation
**Goal:** Set up project, business data model, user authentication

| Task | Assignee | Status | Notes |
|------|----------|--------|-------|
| Set up Python project structure | Dev | ✅ Done | |
| Implement Business class with income/expense logic | Dev | ✅ Done | |
| Implement user registration with bcrypt | Dev | ✅ Done | |
| Implement user login with session | Dev | ✅ Done | |
| Implement JSON data persistence | Dev | ✅ Done | |

**Velocity:** 11 points | **Duration:** 2 weeks

---

## Sprint 2 — Core Features
**Goal:** Dashboard UI, financial calculations, multi-business support

| Task | Assignee | Status | Notes |
|------|----------|--------|-------|
| Build login/register UI with customtkinter | Dev | ✅ Done | |
| Build main dashboard frame | Dev | ✅ Done | |
| Implement income/expense manual entry | Dev | ✅ Done | |
| Build sidebar for business selection | Dev | ✅ Done | |
| Implement refresh_dashboard function | Dev | ✅ Done | |

**Velocity:** 11 points | **Duration:** 2 weeks

---

## Sprint 3 — Analytics & Alerts
**Goal:** Charts, alerts, and financial period tracking

| Task | Assignee | Status | Notes |
|------|----------|--------|-------|
| Integrate Matplotlib pie chart | Dev | ✅ Done | |
| Integrate Matplotlib line chart | Dev | ✅ Done | |
| Implement budget exceeded alert | Dev | ✅ Done | |
| Implement net loss alert | Dev | ✅ Done | |
| Add period selector (Daily/Weekly/Monthly) | Dev | ✅ Done | |

**Velocity:** 11 points | **Duration:** 2 weeks

---

## Sprint 4 — OCR Integration
**Goal:** Scan and process invoice images

| Task | Assignee | Status | Notes |
|------|----------|--------|-------|
| Integrate Tesseract OCR | Dev | ✅ Done | Requires installation |
| Build image upload dialog | Dev | ✅ Done | |
| Implement regex amount extraction | Dev | ✅ Done | Detects XX.XX patterns |
| Auto-assign bill number (OCR-HHMMSS) | Dev | ✅ Done | |
| Category selection after OCR | Dev | ✅ Done | |

**Velocity:** 8 points | **Duration:** 2 weeks

---

## Sprint 5 — Export & Archive
**Goal:** CSV/Excel export, report archiving

| Task | Assignee | Status | Notes |
|------|----------|--------|-------|
| Implement CSV export with all transactions | Dev | ✅ Done | |
| Implement Excel export with openpyxl | Dev | ✅ Done | |
| Auto-open Excel on export | Dev | ✅ Done | Cross-platform |
| Build archive browser window | Dev | ✅ Done | |
| Add notes field to archive | Dev | ✅ Done | |

**Velocity:** 15 points | **Duration:** 2 weeks

---

## Sprint 6 — CI/CD & Testing
**Goal:** Automated tests, GitHub Actions pipeline

| Task | Assignee | Status | Notes |
|------|----------|--------|-------|
| Write 14 unit tests for Business class | Dev | ✅ Done | |
| Set up GitHub Actions workflow | Dev | ✅ Done | |
| Configure headless test runner (xvfb) | Dev | ✅ Done | |
| Add lint job (flake8) | Dev | ✅ Done | |
| Add security scan (bandit) | Dev | ✅ Done | |
| Add build/package artifact job | Dev | ✅ Done | |
| Write README documentation | Dev | ✅ Done | |
| Write risk register | Dev | ✅ Done | |
| Write demo plan | Dev | ✅ Done | |

**Velocity:** 8 points | **Duration:** 2 weeks

---

## Sprint Velocity Chart

| Sprint | Planned | Actual |
|--------|---------|--------|
| Sprint 1 | 11 | 11 |
| Sprint 2 | 11 | 11 |
| Sprint 3 | 11 | 11 |
| Sprint 4 | 8 | 8 |
| Sprint 5 | 15 | 15 |
| Sprint 6 | 8 | 8 |
| **Total** | **64** | **64** |

---

## Definition of Done (DoD)

A user story is considered **Done** when:
- [ ] Feature is implemented and manually tested
- [ ] Unit tests written (where applicable)
- [ ] Code committed to repository
- [ ] CI/CD pipeline passes all jobs
- [ ] Feature is demonstrated and working

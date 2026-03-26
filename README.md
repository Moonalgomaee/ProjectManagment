# 💼 Smart Financial Monitoring & Expense Management System

![CI/CD Pipeline](https://github.com/YOUR_USERNAME/smart-finance-system/actions/workflows/ci-cd.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A desktop application for intelligent accounting and financial management designed for small businesses, cafés, and retail stores.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Board](#project-board)
- [Testing](#testing)
- [Demo Plan](#demo-plan)
- [Risk Register](#risk-register)
- [Team](#team)

---

## 🎯 Project Overview

### Problem Statement
Small businesses struggle with:
- Manual income/expense tracking
- No periodic financial analysis
- Limited financial visibility
- No budget alerts
- Difficulty managing paper invoices

### Solution
This system provides real-time financial monitoring with OCR bill scanning, visual analytics, and automated alerts — all in a user-friendly desktop interface.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 User Authentication | Secure login/register with bcrypt password hashing |
| 🏢 Multi-Business Support | Manage multiple businesses from one account |
| 💰 Income Tracking | Record income by day, week, or month |
| 💸 Expense Categorization | 8 categories: Rent, Salaries, Supplies, Marketing, Utilities, Transport, Maintenance, Other |
| 📄 OCR Bill Scanning | Upload invoice images — amount auto-detected via Tesseract OCR |
| 📊 Visual Analytics | Pie chart (expenses by category) + Line chart (financial overview) |
| ⚠️ Smart Alerts | Automatic warnings for budget exceeded or net loss |
| 📁 Export CSV | Detailed CSV reports with all transactions |
| 📈 Export Excel | Formatted Excel reports organized by business/period |
| 🗂️ Archive | Browse historical reports with notes |
| 🌍 Multi-Currency | Support for USD ($) and Turkish Lira (₺) |

---

## 🏗️ System Architecture

```
smart-finance-system/
├── main.py                     # Main application (GUI + logic)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── business_data.json          # Auto-generated: saved business data
├── users.json                  # Auto-generated: user accounts
├── business_summary.csv        # Auto-generated: summary export
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD pipeline
├── tests/
│   └── test_business.py        # Unit tests for Business class
├── docs/
│   ├── sprint_report.md        # Sprint planning & progress
│   ├── risk_register.md        # Risk identification & mitigation
│   └── demo_plan.md            # Live demo script
└── Reports/                    # Auto-generated: Excel exports
    └── <BusinessName>/
        └── <Period>/
```

---

## 🚀 Installation

### Prerequisites
- Python 3.9+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/smart-finance-system.git
cd smart-finance-system

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## 📖 Usage

### First Launch
1. Run `python main.py`
2. Click **Register** to create an account
3. Log in with your credentials
4. Click **➕ Add Business** to create your first business
5. Set currency, period (Daily/Weekly/Monthly), and budget

### Daily Use
- **Add Income**: Click 💰 Add Income → enter amount
- **Add Expense**: Click 💸 Add Expense → enter amount and category
- **Scan Bill**: Click 📄 Upload Bill → select invoice image
- **Export Reports**: Click 📁 Export CSV or 📊 Export Excel
- **View Archive**: Click 🗂️ Open Archive

---

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** for automated CI/CD.

### Pipeline Jobs

```
Push/PR → [Lint] → [Test] → [Build] → [Security Scan]
                                            ↓
                                     [Summary Report]
```

| Job | Description | Trigger |
|---|---|---|
| **Lint** | PEP8 style check + syntax validation | Every push/PR |
| **Unit Tests** | 14 automated tests on Business logic | After lint passes |
| **Build** | Package validation + zip artifact | After tests pass |
| **Security Scan** | Bandit security analysis | Parallel with tests |
| **Summary** | Pipeline result report | Always (final step) |

### View Pipeline
👉 Go to your repo → **Actions** tab → **CI/CD Pipeline**

---

## 📋 Project Board

### Sprint Board
👉 [View on GitHub Projects](https://github.com/YOUR_USERNAME/smart-finance-system/projects)

### Sprint Overview

| Sprint | Goal | Status |
|---|---|---|
| Sprint 1 | Core business logic + data model | ✅ Done |
| Sprint 2 | Login/Register + authentication | ✅ Done |
| Sprint 3 | Dashboard UI + charts | ✅ Done |
| Sprint 4 | OCR bill scanning | ✅ Done |
| Sprint 5 | CSV/Excel export + archive | ✅ Done |
| Sprint 6 | CI/CD pipeline + tests | ✅ Done |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m unittest tests/test_business.py -v
```

### Test Coverage

| Test Case | Description |
|---|---|
| `test_business_creation` | Validates business object initialization |
| `test_add_income` | Income addition and total calculation |
| `test_add_multiple_incomes` | Multiple income aggregation |
| `test_add_expense` | Expense addition with category |
| `test_net_profit_positive` | Profit calculation (income > expense) |
| `test_net_profit_negative` | Loss calculation (expense > income) |
| `test_alert_budget_exceeded` | Budget alert trigger |
| `test_alert_running_at_loss` | Loss alert trigger |
| `test_no_alerts_when_healthy` | No false alerts |
| `test_expense_by_category` | Category-based expense grouping |
| `test_to_dict_and_from_dict` | Data serialization/deserialization |
| `test_empty_business_totals` | Zero state validation |
| `test_income_with_custom_date` | Date assignment |
| `test_categories_list` | Default categories check |

---

## 🎬 Demo Plan

See [`docs/demo_plan.md`](docs/demo_plan.md) for the complete live demo script.

### Quick Demo Flow (5 minutes)
1. Show GitHub repository structure (30s)
2. Show CI/CD pipeline running in Actions tab (60s)
3. Show GitHub Project sprint board (30s)
4. Launch application live (30s)
5. Register new user → Login (30s)
6. Add business (name, currency, budget) (30s)
7. Add income + expense entries (30s)
8. Upload bill image → OCR detection (30s)
9. Show dashboard charts + alerts (30s)
10. Export CSV/Excel report (30s)

---

## ⚠️ Risk Register

See [`docs/risk_register.md`](docs/risk_register.md) for the full risk register.

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| OCR fails on blurry images | High | Medium | Manual fallback entry |
| Data loss (no backup) | Medium | High | JSON auto-save on every action |
| Tesseract not installed | High | High | Clear error message + install guide |
| Budget miscalculation | Low | High | Unit tests cover all calculations |

---

## 👥 Team

| Role | Responsibility |
|---|---|
| Developer | Full-stack development, UI, business logic |
| Tester | Unit tests, CI/CD configuration |
| Analyst | Requirements, documentation, demo |

---

## 📄 License

MIT License — free to use, modify, and distribute.

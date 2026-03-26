# Risk Register — Smart Financial Monitoring System

**Project:** Smart Financial Monitoring & Expense Management System
**Last Updated:** Sprint 6
**Status:** Active

---

## Risk Matrix

```
         │  LOW    MEDIUM   HIGH
─────────┼────────────────────────
HIGH     │  R5      R1       R2
MEDIUM   │  R6      R3       R4
LOW      │         R7
─────────┴────────────────────────
          (Probability ↑)
```

---

## Risk Register Table

| ID | Risk | Category | Probability | Impact | Score | Status | Mitigation | Owner |
|----|------|----------|-------------|--------|-------|--------|------------|-------|
| R1 | Tesseract OCR not installed on user machine | Technical | High | High | 9 | Active | Display clear install error message with download link in README | Dev |
| R2 | OCR fails to detect amount in blurry or low-res images | Technical | High | Medium | 6 | Active | Fallback to manual entry dialog; user can type amount manually | Dev |
| R3 | Data loss from app crash before save | Data | Medium | High | 6 | Mitigated | Auto-save to JSON after every income/expense action | Dev |
| R4 | Budget miscalculation due to floating-point errors | Data | Medium | High | 6 | Mitigated | Unit tests cover all calculation paths; Python float precision acceptable | Dev/Test |
| R5 | User forgets password (no reset mechanism) | Security | High | Low | 3 | Accepted | Future sprint: add email-based password reset | Dev |
| R6 | JSON data file corrupted or deleted manually | Data | Medium | Medium | 4 | Active | Future: add automatic backup file (.bak) creation | Dev |
| R7 | Application slow with very large transaction history | Performance | Low | Medium | 2 | Accepted | Acceptable for MVP scope (< 1000 transactions per business) | Dev |

---

## Risk Detail Cards

### R1 — Tesseract Not Installed
- **Description:** OCR upload feature requires Tesseract to be installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`. If missing, the bill upload feature crashes silently.
- **Probability:** High — many users won't have it pre-installed
- **Impact:** High — OCR is a key feature
- **Current Status:** Active
- **Mitigation Actions:**
  1. README includes Tesseract installation instructions
  2. Future: wrap pytesseract call in try/except with user-friendly error popup
  3. Future: add startup check for Tesseract executable

---

### R2 — OCR Amount Detection Failure
- **Description:** The regex `\d+\.\d{2}` may fail on handwritten bills, non-standard formatting, or low image quality.
- **Probability:** High — real-world invoices vary significantly
- **Impact:** Medium — feature degrades but manual entry still works
- **Current Status:** Active
- **Mitigation Actions:**
  1. Error dialog shown when no amount detected
  2. User redirected to manual expense entry
  3. Future: improve regex, add multi-language OCR support

---

### R3 — Data Loss from App Crash
- **Description:** If the application crashes mid-operation, unsaved data could be lost.
- **Probability:** Medium
- **Impact:** High — financial data loss is unacceptable
- **Current Status:** Mitigated
- **Mitigation Actions:**
  1. `save_data()` called after every income/expense addition
  2. JSON file written atomically
  3. Future: implement WAL (write-ahead log) pattern

---

### R4 — Budget Miscalculation
- **Description:** Floating-point arithmetic in Python can produce small rounding errors in financial calculations.
- **Probability:** Medium
- **Impact:** High — incorrect budget alerts damage user trust
- **Current Status:** Mitigated
- **Mitigation Actions:**
  1. 14 unit tests cover all calculation scenarios
  2. All display values formatted to 2 decimal places
  3. Future: use Python `decimal` module for precision-critical paths

---

### R5 — No Password Reset
- **Description:** Users who forget their password have no recovery mechanism.
- **Probability:** High (users forget passwords)
- **Impact:** Low (workaround: admin can edit users.json manually)
- **Current Status:** Accepted for MVP
- **Planned Fix:** Sprint 7 — email-based password reset

---

### R6 — JSON File Corruption
- **Description:** If users manually edit or delete `business_data.json`, all business data is lost.
- **Probability:** Medium
- **Impact:** Medium — data recovery is difficult
- **Current Status:** Active
- **Mitigation Actions:**
  1. `load_data()` handles missing file gracefully (starts fresh)
  2. Future: create `.bak` backup on every save

---

### R7 — Performance with Large Data
- **Description:** All transactions are loaded into memory. With 1000+ transactions, UI may lag.
- **Probability:** Low (MVP scope is small businesses)
- **Impact:** Medium — user experience degradation
- **Current Status:** Accepted for MVP
- **Planned Fix:** Future sprint — pagination or SQLite backend

---

## Risk Updates Log

| Date | Risk | Update |
|------|------|--------|
| Sprint 1 | R3 | Added auto-save after every action — risk reduced from High to Medium |
| Sprint 4 | R1, R2 | OCR integrated; clear error messages added |
| Sprint 6 | R4 | Unit tests added covering all calculation paths — risk mitigated |

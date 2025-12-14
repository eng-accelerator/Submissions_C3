# Personal Finance AI Coach  

Standalone Streamlit app with clean architecture and database persistence

---

## 🚀 Quick Start (Fast Setup with `uv`)

This project runs on **Python 3.11.4**. We recommend using `uv` for blazing fast package management.

### 1. Install `uv` (if not installed)
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create venv with specific python version
uv venv --python 3.11.4

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies (fast!)
uv pip install -r requirements.txt
```


### 3. Run Application
```bash
streamlit run app.py
```
Visit: **http://localhost:8501**

---

## 🏗️ Architecture & Design

### Clean Architecture (Standalone Monolith)
**Layers (from outer to inner):**
1. **UI Layer** (`app.py`, `pages/`) - Streamlit components
2. **Service Layer** (`services/`) - Business logic
3. **Data Layer** (`models/`) - SQLAlchemy ORM
4. **Utils** (`utils/`, `config.py`) - Cross-cutting concerns

**Dependencies flow inward:** UI → Services → Models → Database. Nothing depends on UI.

### Design Patterns Used
1. **Repository Pattern** - Database access through models
2. **Service Pattern** - Business logic in services layer
3. **Dependency Injection** - Pass db sessions, not globals
4. **Configuration Object** - Centralized settings

### 🔄 Migration Path to API
If you later need a separate backend (e.g., for mobile app):
1. Services → FastAPI routes
2. Keep models unchanged
3. Frontend calls API instead of services
4. **Zero business logic changes** required

---

## 📁 Project Structure

```
project-x/
├── app.py                     # Landing page (no sidebar)
├── pages/                     # Multi-page app
│   ├── 1_onboarding.py        # Data collection
│   ├── 2_dashboard.py         # Analysis + charts
│   └── 3_goals.py             # Goal tracking + projections
├── models/                    # SQLAlchemy ORM (data layer)
│   ├── database.py            # DB setup (SQLite/PostgreSQL)
│   ├── user.py                # User models
│   ├── financial.py           # Financial data models
│   └── plans.py               # Plans & tracking
├── services/                  # Business logic
│   ├── auth_service.py        # Authentication
│   ├── calculator.py          # Financial calculations
│   └── data_service.py        # CRUD operations
├── utils/                     # Utilities
│   ├── security.py            # Password hashing, JWT
├── config.py                  # Environment config
├── init_db.py                 # Database initialization
├── requirements.txt           # Dependencies (Python 3.11.4)
└── .env                       # Environment variables
```

---

## ✨ Features

### Guest Mode (Default)
- ✅ No login required
- ✅ Full functionality (stored in session)
- ✅ Data lost on session end (Privacy focused)

### Registered User Mode
- ✅ Create account & Login
- ✅ Data persists to SQLite (Dev) / PostgreSQL (Prod)
- ✅ Auto-switch based on `DATABASE_URL`

### Analytics & Tools
- **Dashboard**: Plotly charts (Income/Expense, Assets/Liabilities), Health Gauges
- **Goals**: Smart projections, feasibility checks, timeline calculation
- **Calculator**: Net Worth, Savings Rate, Emergency Fund analysis

---

## 🗄️ Database

**Local Development:** SQLite (`finance_coach.db`)
**Production:** Automatically switches to PostgreSQL via `DATABASE_URL` env var

**Tables:** `users`, `financial_snapshots`, `assets`, `liabilities`, `goals`, `plans`

---

## 📊 Technology Stack

- **Frontend**: Streamlit
- **Database**: SQLAlchemy ORM (SQLite → PostgreSQL)
- **Charts**: Plotly
- **Auth**: Bcrypt + JWT (ready)
- **AI**: LangChain/LangGraph (Phase 2 RAG)

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set Environment Variables:
   ```ini
   ENV=production
   DATABASE_URL=postgresql://user:pass@host:5432/finance_coach
   JWT_SECRET_KEY=your-secret-key
   ```

---

## 📝 Usage Flow

1. **Landing Page** → "Get Started Free"
2. **Onboarding** → Enter Snapshot (Income/Expenses) & Assets/Debts
3. **Dashboard** → View Financial Health & Recommendations
4. **Goals** → Set Goals & View Projections
5. **(Optional)** Login to save data

---

## ✅ Best Practices Implemented

- ✅ Separation of concerns
- ✅ Type hints throughout
- ✅ Docstrings for all functions
- ✅ Error handling
- ✅ Versioned calculations (audit trail)
- ✅ Environment-based config
- ✅ Clean imports (relative within package)

---

**Status**: ✅ Production Ready  
**Built with ❤️ using clean architecture principles**

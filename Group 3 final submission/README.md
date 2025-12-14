# 💰 AI Financial Coach

> **Your Personal AI-Powered Financial Advisor**
> 
> A comprehensive multi-agent financial advisory system that leverages advanced AI to provide personalized financial guidance through debt analysis, savings strategies, investment planning, budget optimization, and retirement planning.

---

## 🎯 Project Overview

AI Financial Coach is a sophisticated financial advisory application that combines the power of multiple specialized AI agents with document processing capabilities to deliver personalized financial advice. The system intelligently analyzes your financial documents (salary slips, bank statements, credit card statements, loan documents, and asset holdings) to provide actionable insights and strategic recommendations.

### Key Features

- 🤖 **Multi-Agent AI System** - Five specialized AI agents for different financial domains
- 📄 **Document Processing** - Automated extraction of financial data from uploaded documents
- 🔐 **Secure Authentication** - User registration, login, and profile management
- 💾 **Dual Storage Architecture** - PostgreSQL for structured data + ChromaDB for vector embeddings
- 📊 **Interactive Dashboard** - Real-time financial overview and insights
- 🧠 **RAG (Retrieval Augmented Generation)** - Context-aware responses using your financial documents
- 📈 **Financial Analytics** - Track income, expenses, debts, and investments
- 💬 **Conversational Interface** - Natural language interaction with AI agents

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  (Auth, Dashboard, Profile, Chat, Upload, Analytics)        │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────────────┐
│                  Financial Advisor Orchestrator                │
│              (LangGraph Multi-Agent Workflow)                  │
└───┬────────────┬──────────────┬────────────┬────────────┬──────┘
    │            │              │            │            │
    ▼            ▼              ▼            ▼            ▼
┌────────┐  ┌───────────┐  ┌─────────┐  ┌──────────┐   ┌──────────┐
│ Debt   │  │Retirement │  │Savings  │  │Budget    │   │Investment│
│Analyzer│  │Planner    │  │Strategy │  │Planner   │   │Advisor   │
└────────┘  └───────────┘  └─────────┘  └──────────┘   └──────────┘
    │            │             │            │              │
    └────────────┴─────────────┴────────────┴──────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌──────────────┐        ┌──────────────┐
            │  PostgreSQL  │        │  ChromaDB    │
            │  (Tabular)   │        │  (Vector)    │
            └──────────────┘        └──────────────┘
                    │                       │
                    └───────────────────────┘
```

### Component Architecture

```
fincoach/
│
├── app.py                          # Main Streamlit application & authentication
│
├── pages/                          # Streamlit multi-page structure
│   ├── 1___Dashboard.py           # Financial overview & metrics
│   ├── 2___Profile.py             # User profile & document upload
│   └── 4___Manual_Data_Entry.py   # Manual financial data input
│
├── auth/
│   └── auth_manager.py            # User authentication & authorization
│
├── database/
│   ├── models.py                  # SQLAlchemy ORM models
│   └── db_manager.py              # Database operations & queries
│
├── processors/
│   ├── document_processor.py      # PDF/Excel/CSV document parsing
│   ├── text_chunker.py            # Text chunking for embeddings
│   ├── vector_store_manager.py    # ChromaDB vector operations
│   └── credit_card_processor.py   # Specialized credit card parsing
│
├── agents/
│   └── ai_agents.py               # 5 specialized financial AI agents
│
├── utils/
│   ├── session_state.py           # Streamlit session management
│   └── rag_system.py              # RAG orchestration
│
├── chroma_db/                     # ChromaDB vector storage (auto-created)
├── uploads/                       # User uploaded documents (auto-created)
│
├── .env                           # Environment variables (create this)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🤖 AI Agents

The system employs five specialized AI agents, each powered by Claude 3.5 Sonnet through OpenRouter:

### 1. 💳 Debt Analyzer Agent
**Purpose**: Comprehensive debt analysis and payoff strategies

**Capabilities**:
- Analyzes total debt burden and interest rates
- Prioritizes high-interest debts
- Suggests debt payoff methods (Snowball vs Avalanche)
- Creates realistic timelines for debt freedom
- Recommends budget adjustments to accelerate payoff
- Provides motivational support

**Example Queries**:
- "Analyze my debt and suggest a repayment plan"
- "Should I consolidate my credit card debts?"
- "How can I become debt-free in 2 years?"

---

### 2. 💰 Savings Strategy Agent
**Purpose**: Personalized savings plans and wealth building

**Capabilities**:
- Analyzes current savings rate and potential
- Suggests realistic savings goals (Emergency fund, specific goals)
- Recommends expense optimization strategies
- Proposes automated savings mechanisms
- Suggests appropriate savings instruments (FD, RD, PPF, Mutual Funds)
- Creates phased savings plans (3-month, 6-month, 1-year targets)

**Example Queries**:
- "How much should I save each month?"
- "Help me build a 6-month emergency fund"
- "What are the best savings instruments for me?"

---

### 3. 📈 Investment Advisor Agent
**Purpose**: Portfolio building and investment recommendations

**Capabilities**:
- Assesses risk tolerance based on age and goals
- Recommends asset allocation (Equity, Debt, Gold, Real Estate)
- Suggests specific investment products (Mutual Funds, Stocks, ETFs)
- Creates diversified portfolio recommendations
- Explains investment strategies and expected returns
- Suggests SIP amounts and frequency
- Addresses tax optimization (80C, ELSS, etc.)

**Example Queries**:
- "Build me an investment portfolio"
- "Where should I invest ₹50,000?"
- "Suggest mutual funds for long-term growth"

---

### 4. 📊 Budget Planner Agent
**Purpose**: Budget creation and spending optimization

**Capabilities**:
- Analyzes current spending patterns
- Identifies areas of overspending
- Creates 50-30-20 budget framework (Needs-Wants-Savings)
- Suggests specific cost-cutting measures
- Provides category-wise budget recommendations
- Creates actionable monthly budget templates
- Sets up spending alerts and checkpoints

**Example Queries**:
- "Create a monthly budget for me"
- "How can I reduce my expenses?"
- "Help me stick to my budget"

---

### 5. 🏖️ Retirement Planner Agent
**Purpose**: Long-term retirement planning

**Capabilities**:
- Calculates retirement corpus needed (considering inflation)
- Assesses current retirement readiness
- Recommends retirement savings instruments (PPF, NPS, EPF)
- Creates monthly investment plans for retirement goals
- Suggests early retirement options if applicable
- Plans for healthcare costs in retirement
- Provides milestone-based targets

**Example Queries**:
- "Prepare an early retirement plan"
- "How much do I need to retire at 50?"
- "Am I on track for retirement?"

---

## 📊 Database Schema

### PostgreSQL Tables

#### Users Table
```sql
- id (PK)
- username (unique)
- email (unique)
- password_hash
- full_name
- phone
- created_at
- last_login
- is_active
- monthly_income
- occupation
- age
- dependents
- city
- has_salary_slip (boolean)
- has_bank_statement (boolean)
- has_loan_data (boolean)
- has_credit_card_statement (boolean)
- has_collateral_details (boolean)
```

#### Documents Table
```sql
- id (PK)
- user_id (FK)
- document_type (salary_slip, bank_statement, etc.)
- file_name
- file_path
- uploaded_at
- processed (boolean)
- doc_metadata (JSON)
```

#### Financial Data Table
```sql
- id (PK)
- user_id (FK)
- data_type (income, expense, debt, investment)
- category
- amount
- description
- transaction_date
- created_at
- source_document_id (FK)
```

#### Chat History Table
```sql
- id (PK)
- user_id (FK)
- message
- response
- agent_type
- created_at
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- OpenRouter API account
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/fincoach.git
cd fincoach
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://username:password@host:port/database_name

# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# OpenAI API Key (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
APP_NAME=AI Financial Coach
SECRET_KEY=your_secret_key_here
DEBUG=False
```

**Important Notes**:
- Replace `username`, `password`, `host`, `port`, and `database_name` with your PostgreSQL credentials
- Get your OpenRouter API key from https://openrouter.ai/
- Get your OpenAI API key from https://platform.openai.com/
- Generate a secure random string for `SECRET_KEY`

### Step 5: Initialize Database

```bash
python -m database.models
```

This will create all necessary database tables.

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

---

## 📱 User Guide

### Getting Started

#### 1. Registration
- Navigate to the Register tab
- Fill in your details (username, email, password)
- Agree to terms and conditions
- Click Register

#### 2. Login
- Enter your username/email and password
- Click Login

#### 3. Complete Your Profile
- Go to Profile page (sidebar)
- Fill in personal information:
  - Full name
  - Age
  - Monthly income
  - Occupation
  - Number of dependents
  - City

#### 4. Upload Financial Documents
The system accepts the following document types:

**Salary Slip/Income Data**
- PDF format
- Contains salary breakdown
- Recent 1-3 months

**Bank Statements**
- PDF, CSV, or Excel format
- Last 3 months recommended
- Includes all transactions

**Loan Documents**
- PDF format
- Loan agreement or statement
- Shows principal, interest rate, EMI

**Credit Card Statements**
- PDF format
- Last 1-3 months
- Shows all transactions and dues

**Collateral/Asset Details**
- Stock/Mutual Fund holdings (Excel/CSV)
- Property documents (PDF)
- Any movable/immovable assets

#### 5. Chat with AI Agents

Navigate to the Dashboard or Chat page and ask questions like:
- "Analyze my debt and suggest a repayment plan"
- "Create a budget based on my spending"
- "Build an investment portfolio for me"
- "Help me plan for early retirement"
- "How can I save more each month?"

The system will automatically route your query to the most appropriate agent.

---

## 🔧 Technical Stack

### Frontend
- **Streamlit** - Interactive web application framework
- **Plotly** - Data visualization and charts
- **Pandas** - Data manipulation and analysis

### Backend
- **LangChain** - LLM orchestration framework
- **OpenRouter API** - Access to Claude 3.5 Sonnet
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database for structured data
- **ChromaDB** - Vector database for embeddings

### Document Processing
- **PyPDF2** - PDF parsing
- **openpyxl** - Excel file processing
- **pandas** - CSV processing
- **Unstructured** - Advanced document parsing

### AI & Embeddings
- **OpenAI Embeddings** - Text vectorization
- **Claude 3.5 Sonnet** - Reasoning and response generation
- **LangChain** - Agent orchestration

### Security
- **bcrypt** - Password hashing
- **python-dotenv** - Environment variable management

---

## 🎨 User Interface Pages

### 1. Login/Registration Page (app.py)
- Secure authentication
- Password validation
- New user registration
- Profile creation

### 2. Dashboard (1___Dashboard.py)
- Financial overview metrics
- Profile completion status
- Quick action buttons
- Document checklist
- Financial health score

### 3. Profile & Document Upload (2___Profile.py)
- Personal information management
- Document upload interface
- Document processing status
- Data extraction preview

### 4. Manual Data Entry (4___Manual_Data_Entry.py)
- Manual transaction entry
- Income/expense logging
- Debt/investment tracking
- Category management

---

## 🔐 Security Features

- ✅ Password hashing using bcrypt
- ✅ Session-based authentication
- ✅ User data isolation (each user only sees their own data)
- ✅ Secure file upload handling
- ✅ Environment variable protection
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation and sanitization

---

## 📈 RAG (Retrieval Augmented Generation) System

The RAG system enhances AI responses by:

1. **Document Processing**
   - Extracts text from uploaded documents
   - Identifies financial data (amounts, dates, categories)

2. **Chunking**
   - Splits documents into meaningful chunks
   - Maintains context with overlap
   - Preserves metadata (document type, user, upload date)

3. **Embedding**
   - Converts text chunks to vector embeddings
   - Uses OpenAI's embedding models
   - Stores in ChromaDB with metadata

4. **Retrieval**
   - Semantic search across user's documents
   - Finds relevant context for queries
   - Filters by document type and user

5. **Generation**
   - Provides context to AI agents
   - Generates personalized responses
   - Cites specific documents when relevant

---

## 🤝 Agent Orchestrator

The `AgentOrchestrator` intelligently routes queries to the appropriate agent:

```python
orchestrator = AgentOrchestrator(openrouter_api_key)

# Automatic routing
response = orchestrator.process_query(
    user_id=user_id,
    query="Help me reduce my debt"
)
# Routes to: DebtAnalyzerAgent

# Manual routing to specific agent
response = orchestrator.process_query(
    user_id=user_id,
    query="What should I invest in?",
    specific_agent='investment_advisor'
)
# Routes to: InvestmentAdvisorAgent
```

---

## 🧪 Sample Questions by Agent

### Debt Analyzer
- "What's the best way to pay off my credit card debt?"
- "Should I consolidate my loans?"
- "How long will it take to become debt-free?"
- "Which debt should I prioritize?"

### Savings Strategy
- "How do I build an emergency fund?"
- "What percentage of my income should I save?"
- "Suggest ways to reduce my monthly expenses"
- "Help me save for a car down payment"

### Investment Advisor
- "Create a balanced portfolio for me"
- "Should I invest in stocks or mutual funds?"
- "What are tax-saving investment options?"
- "How much should I invest in SIP monthly?"

### Budget Planner
- "Create a monthly budget based on my income"
- "Help me track my spending better"
- "I'm overspending on food, what should I do?"
- "Set up a budget for my family of 4"

### Retirement Planner
- "Can I retire at 50?"
- "How much do I need for retirement?"
- "Suggest retirement savings plans"
- "Calculate my retirement corpus"

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Test database connection
python -c "from database.models import engine; print(engine.connect())"

# Reinitialize database
python -m database.models
```

### ChromaDB Issues
```bash
# Reset vector store
python reset_vector_store.py
```

### Document Processing Errors
```bash
# Check document processor
python diagnose_processing.py
```

### Import Errors
```bash
# Verify all imports
python diagnose_imports.py
```

---

## 📝 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| DATABASE_URL | PostgreSQL connection string | Yes | - |
| OPENROUTER_API_KEY | OpenRouter API key | Yes | - |
| OPENAI_API_KEY | OpenAI API key for embeddings | Yes | - |
| APP_NAME | Application name | No | AI Financial Coach |
| SECRET_KEY | Flask secret key | Yes | - |
| DEBUG | Debug mode | No | False |

---

## 🚧 Development Roadmap

### Phase 1: Core Features ✅
- [x] User authentication
- [x] Document upload and processing
- [x] Basic financial data extraction
- [x] 5 specialized AI agents
- [x] RAG system implementation
- [x] Dashboard with metrics

### Phase 2: Enhanced Features (In Progress)
- [ ] Real-time chat interface
- [ ] Advanced analytics dashboard
- [ ] Goal tracking system
- [ ] Bill reminders and alerts
- [ ] Multi-language support
- [ ] Mobile app

### Phase 3: Advanced Features (Planned)
- [ ] Financial health score
- [ ] Automated categorization
- [ ] Bank account integration
- [ ] Investment tracking
- [ ] Tax planning module
- [ ] Family/shared accounts

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Dr. Nitin**
- IT Head at MIT School of Distance Education, Pune
- Location: Pune, Maharashtra, India

---

## 🙏 Acknowledgments

- OpenRouter for providing access to Claude 3.5 Sonnet
- Anthropic for Claude AI models
- Streamlit for the amazing web framework
- LangChain for agent orchestration capabilities
- The open-source community

---

## 📧 Support

For questions, issues, or suggestions:
- Create an issue on GitHub
- Contact: [Your Email]
- Documentation: [Your Docs URL]

---

## ⚠️ Disclaimer

This application provides financial guidance based on AI analysis and should not be considered as professional financial advice. Always consult with certified financial advisors before making significant financial decisions.

---

**Made with ❤️ in Pune, India**

*AI Financial Coach - Empowering Your Financial Future*

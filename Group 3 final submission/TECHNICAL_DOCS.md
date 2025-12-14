# 🔧 AI Financial Coach - Technical Architecture & API Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Database Schema](#database-schema)
4. [AI Agents API](#ai-agents-api)
5. [RAG System](#rag-system)
6. [Document Processing Pipeline](#document-processing-pipeline)
7. [Authentication Flow](#authentication-flow)
8. [Code Examples](#code-examples)
9. [Extension Guide](#extension-guide)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                      (Streamlit)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Login   │  │Dashboard │  │ Profile  │  │  Chat    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Application Layer                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Session State Management                   │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Authentication Manager                     │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ RAG System   │  │Agent Orch.   │  │ DB Manager   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Doc Processor│  │Text Chunker  │  │Vector Store  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      AI/ML Layer                            │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Agent Orchestrator                   │      │
│  └───┬──────┬──────┬──────┬──────┬────────────────┘      │
│      │      │      │      │      │                          │
│  ┌───▼──┐ ┌▼───┐ ┌▼───┐ ┌▼───┐ ┌▼───────┐                │
│  │Debt  │ │Sav. │ │Inv. │ │Bud.│ │Retire. │                │
│  │Agent │ │Agent│ │Agent│ │Agnt│ │Agent   │                │
│  └──────┘ └─────┘ └─────┘ └────┘ └────────┘                │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │    OpenRouter → Claude 3.5 Sonnet                │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │    OpenAI → text-embedding-3-small                │      │
│  └──────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Data Storage Layer                       │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │   PostgreSQL         │  │   ChromaDB           │        │
│  │   (Structured Data)  │  │   (Vector Embeddings)│        │
│  │                      │  │                       │        │
│  │  - Users             │  │  - Document Chunks   │        │
│  │  - Documents         │  │  - Embeddings        │        │
│  │  - Financial Data    │  │  - Metadata          │        │
│  │  - Chat History      │  │                       │        │
│  └──────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Action → Streamlit UI → Session State → Business Logic → AI Agents → LLM
                    ↓                             ↓
              Authentication                  RAG System
                    ↓                             ↓
              DB Manager ← ─────────────── Vector Store
                    ↓                             ↓
              PostgreSQL                     ChromaDB
```

---

## Core Components

### 1. Authentication Manager (`auth/auth_manager.py`)

**Purpose**: Handle user registration, login, and session management

**Key Methods**:

```python
class AuthManager:
    def register_user(username, email, password, full_name, phone) -> (bool, str)
        """Register new user with hashed password"""
    
    def login_user(username_or_email, password) -> (bool, str, int)
        """Authenticate user and return user_id"""
    
    def get_user_info(user_id) -> User
        """Retrieve user information"""
    
    def update_password(user_id, old_password, new_password) -> (bool, str)
        """Change user password"""
```

**Usage Example**:
```python
from auth.auth_manager import AuthManager

auth = AuthManager()
success, message = auth.register_user(
    username="john_doe",
    email="john@example.com",
    password="SecurePass123",
    full_name="John Doe",
    phone="+91 98765 43210"
)

if success:
    success, msg, user_id = auth.login_user("john_doe", "SecurePass123")
```

---

### 2. Database Manager (`database/db_manager.py`)

**Purpose**: CRUD operations for all database tables

**Key Methods**:

```python
class DBManager:
    # User operations
    def get_user_by_id(user_id) -> User
    def update_user_profile(user_id, **kwargs) -> bool
    
    # Document operations
    def add_document(user_id, document_type, file_name, file_path, metadata) -> Document
    def get_user_documents(user_id) -> List[Document]
    def mark_document_processed(document_id) -> bool
    
    # Financial data operations
    def add_financial_data(user_id, data_type, category, amount, description, source_document_id) -> FinancialData
    def get_financial_data(user_id, data_type=None) -> List[FinancialData]
    def get_financial_summary(user_id) -> Dict
    
    # Chat operations
    def save_chat_message(user_id, message, response, agent_type) -> ChatHistory
    def get_chat_history(user_id, limit=50) -> List[ChatHistory]
```

**Usage Example**:
```python
from database.db_manager import DBManager

db = DBManager()

# Add financial data
db.add_financial_data(
    user_id=1,
    data_type='expense',
    category='Food',
    amount=5000.0,
    description='Monthly groceries',
    source_document_id=None
)

# Get summary
summary = db.get_financial_summary(user_id=1)
print(f"Total Income: {summary['total_income']}")
print(f"Total Expenses: {summary['total_expenses']}")
```

---

### 3. RAG System (`utils/rag_system.py`)

**Purpose**: Orchestrate document processing, embedding, and retrieval

**Key Methods**:

```python
class RAGSystem:
    def process_uploaded_document(user_id, file_path, document_type, file_name) -> Dict
        """Complete pipeline: process → chunk → embed → store"""
    
    def query_documents(user_id, query, document_type=None, k=5) -> List[Dict]
        """Search documents using semantic similarity"""
    
    def get_context_for_query(user_id, query, document_type=None, max_tokens=3000) -> str
        """Get relevant context as formatted string"""
    
    def get_user_stats(user_id) -> Dict
        """Statistics about user's documents"""
```

**Usage Example**:
```python
from utils.rag_system import RAGSystem

rag = RAGSystem()

# Process document
result = rag.process_uploaded_document(
    user_id=1,
    file_path='uploads/salary_slip.pdf',
    document_type='salary_slip',
    file_name='salary_slip.pdf'
)

if result['success']:
    print(f"Created {result['chunks_created']} chunks")
    print(f"Extracted {result['vectors_created']} vectors")

# Query documents
context = rag.get_context_for_query(
    user_id=1,
    query="What is my monthly salary?"
)
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (PK)         │──┐
│ username        │  │
│ email           │  │
│ password_hash   │  │
│ full_name       │  │
│ phone           │  │
│ monthly_income  │  │
│ age             │  │
│ city            │  │
│ ...             │  │
└─────────────────┘  │
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Documents   │ │ Financial    │ │ Chat         │ │ ChromaDB     │
│              │ │ Data         │ │ History      │ │ (Vectors)    │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ id (PK)      │ │ id (PK)      │ │ id (PK)      │ │ chunk_id     │
│ user_id (FK) │ │ user_id (FK) │ │ user_id (FK) │ │ user_id      │
│ doc_type     │ │ data_type    │ │ message      │ │ embedding    │
│ file_name    │ │ category     │ │ response     │ │ metadata     │
│ file_path    │ │ amount       │ │ agent_type   │ │ document     │
│ processed    │ │ description  │ │ created_at   │ │ ...          │
│ ...          │ │ ...          │ └──────────────┘ └──────────────┘
└──────────────┘ └──────────────┘
```

### Table Definitions

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    monthly_income FLOAT DEFAULT 0.0,
    occupation VARCHAR(100),
    age INTEGER,
    dependents INTEGER DEFAULT 0,
    city VARCHAR(100),
    has_salary_slip BOOLEAN DEFAULT FALSE,
    has_bank_statement BOOLEAN DEFAULT FALSE,
    has_loan_data BOOLEAN DEFAULT FALSE,
    has_credit_card_statement BOOLEAN DEFAULT FALSE,
    has_collateral_details BOOLEAN DEFAULT FALSE
);
```

#### Documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255),
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    doc_metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### Financial Data Table
```sql
CREATE TABLE financial_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    data_type VARCHAR(50),
    category VARCHAR(100),
    amount FLOAT,
    description TEXT,
    transaction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_document_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (source_document_id) REFERENCES documents(id) ON DELETE SET NULL
);
```

#### Chat History Table
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    agent_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## AI Agents API

### Agent Orchestrator

**Initialize Orchestrator**:
```python
from agents.ai_agents import AgentOrchestrator
import os

orchestrator = AgentOrchestrator(
    openrouter_api_key=os.getenv('OPENROUTER_API_KEY')
)
```

### Using Individual Agents

#### 1. Debt Analyzer Agent

```python
from agents.ai_agents import DebtAnalyzerAgent

agent = DebtAnalyzerAgent(openrouter_api_key=api_key)

response = agent.process_query(
    user_id=1,
    query="Analyze my debt and create a payoff plan",
    context=""  # Optional RAG context
)

print(response)
```

**Response Format**:
```
Based on your financial profile, here's a comprehensive debt analysis:

CURRENT DEBT SITUATION:
- Total Debt: ₹5,00,000
- High-interest credit card: ₹2,00,000 at 36% APR
- Personal loan: ₹3,00,000 at 14% APR

RECOMMENDED STRATEGY: Avalanche Method
1. Pay minimum on all debts
2. Focus extra ₹10,000/month on credit card
3. Timeline: 18 months to clear credit card
...
```

#### 2. Savings Strategy Agent

```python
from agents.ai_agents import SavingsStrategyAgent

agent = SavingsStrategyAgent(openrouter_api_key=api_key)

response = agent.process_query(
    user_id=1,
    query="Help me build a 6-month emergency fund",
    context=""
)
```

#### 3. Investment Advisor Agent

```python
from agents.ai_agents import InvestmentAdvisorAgent

agent = InvestmentAdvisorAgent(openrouter_api_key=api_key)

response = agent.process_query(
    user_id=1,
    query="Create an investment portfolio with ₹50,000",
    context=""
)
```

#### 4. Budget Planner Agent

```python
from agents.ai_agents import BudgetPlannerAgent

agent = BudgetPlannerAgent(openrouter_api_key=api_key)

response = agent.process_query(
    user_id=1,
    query="Create a monthly budget based on my spending",
    context=""
)
```

#### 5. Retirement Planner Agent

```python
from agents.ai_agents import RetirementPlannerAgent

agent = RetirementPlannerAgent(openrouter_api_key=api_key)

response = agent.process_query(
    user_id=1,
    query="Plan for retirement at age 50",
    context=""
)
```

### Automatic Agent Routing

```python
# Orchestrator automatically selects best agent
result = orchestrator.process_query(
    user_id=1,
    query="How can I reduce my monthly expenses?"
)

print(f"Routed to: {result['agent']}")
print(f"Response: {result['response']}")
print(f"Timestamp: {result['timestamp']}")
```

---

## RAG System

### Document Processing Pipeline

```python
from processors.document_processor import DocumentProcessor
from processors.text_chunker import TextChunker
from processors.vector_store_manager import VectorStoreManager

# 1. Process Document
doc_processor = DocumentProcessor()
processed = doc_processor.process_document('path/to/document.pdf')

# 2. Chunk Text
chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_document(processed, metadata={
    'user_id': 1,
    'document_type': 'salary_slip'
})

# 3. Create Embeddings and Store
vector_store = VectorStoreManager(
    persist_directory='chroma_db',
    openai_api_key=api_key
)
vector_store.add_chunks(user_id=1, chunks=chunks)

# 4. Search
results = vector_store.search_with_score(
    user_id=1,
    query="What is my monthly salary?",
    k=5
)
```

### Vector Store Operations

```python
# Initialize
vector_store = VectorStoreManager(
    persist_directory='chroma_db',
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Add chunks
vector_store.add_chunks(
    user_id=1,
    chunks=[
        {
            'text': 'Salary: ₹75,000 per month',
            'metadata': {
                'user_id': 1,
                'document_type': 'salary_slip',
                'page': 1
            }
        }
    ]
)

# Search
results = vector_store.search_with_score(
    user_id=1,
    query="monthly salary",
    k=5,
    filter_metadata={'document_type': 'salary_slip'}
)

# Get context
context = vector_store.get_relevant_context(
    user_id=1,
    query="What are my deductions?",
    max_tokens=2000
)

# Delete document vectors
vector_store.delete_document(user_id=1, document_id=5)

# Get statistics
stats = vector_store.get_collection_stats(user_id=1)
```

---

## Document Processing Pipeline

### Supported Document Types

1. **PDF** - Salary slips, bank statements, loan documents
2. **Excel/CSV** - Bank transactions, investment holdings
3. **Word Documents** - Loan agreements, contracts

### Processing Flow

```python
from processors.document_processor import DocumentProcessor

processor = DocumentProcessor()

# Process PDF
result = processor.process_document('salary_slip.pdf')
print(result['text'])  # Extracted text
print(result['metadata']['num_pages'])  # Number of pages
print(result['tables'])  # Extracted tables

# Extract financial data
financial_data = processor.extract_financial_data(result, 'salary_slip')
# Returns list of financial transactions
```

### Text Chunking Strategy

```python
from processors.text_chunker import TextChunker

chunker = TextChunker(
    chunk_size=1000,  # Characters per chunk
    chunk_overlap=200  # Overlap for context continuity
)

chunks = chunker.chunk_document(
    processed_doc=result,
    metadata={'user_id': 1, 'doc_type': 'salary_slip'}
)

for chunk in chunks:
    print(f"Chunk: {chunk['text'][:100]}...")
    print(f"Metadata: {chunk['metadata']}")
```

---

## Authentication Flow

### Registration Flow

```
User Input → Validate → Hash Password → Create DB Record → Success
    │            │            │              │
    ▼            ▼            ▼              ▼
Username    Format      bcrypt        INSERT users
Email       Check       (salt+hash)   RETURNING id
Password    Length
```

### Login Flow

```
User Input → Find User → Verify Password → Create Session → Return User
    │            │            │                │
    ▼            ▼            ▼                ▼
Credentials  Query DB    bcrypt.verify    st.session_state
             WHERE        (input, hash)    user_id = X
             username                      authenticated = True
             OR email
```

### Session Management

```python
import streamlit as st

# Initialize session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None

# Check authentication
def check_authentication():
    return st.session_state.get('authenticated', False)

# Logout
def logout():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_data = None
```

---

## Code Examples

### Complete Example: Upload and Query Document

```python
import os
from utils.rag_system import RAGSystem
from agents.ai_agents import AgentOrchestrator

# Initialize systems
rag = RAGSystem(openai_api_key=os.getenv('OPENAI_API_KEY'))
orchestrator = AgentOrchestrator(
    openrouter_api_key=os.getenv('OPENROUTER_API_KEY')
)

# 1. Process uploaded document
result = rag.process_uploaded_document(
    user_id=1,
    file_path='uploads/salary_slip.pdf',
    document_type='salary_slip',
    file_name='October_2024_Salary.pdf'
)

if result['success']:
    print(f"✅ Document processed: {result['chunks_created']} chunks created")
    
    # 2. Get relevant context from documents
    context = rag.get_context_for_query(
        user_id=1,
        query="What is my take-home salary after all deductions?"
    )
    
    # 3. Query AI agent with context
    agent_response = orchestrator.process_query(
        user_id=1,
        query="Based on my salary slip, suggest a budget plan",
        context=context  # RAG context
    )
    
    print(f"🤖 Agent: {agent_response['agent']}")
    print(f"📝 Response: {agent_response['response']}")
```

### Example: Financial Summary Dashboard

```python
from database.db_manager import DBManager
import streamlit as st

db = DBManager()
user_id = st.session_state.user_id

# Get financial summary
summary = db.get_financial_summary(user_id)

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Monthly Income",
        f"₹{summary['total_income']:,.0f}",
        delta=f"+₹{summary['income_change']:,.0f}"
    )

with col2:
    st.metric(
        "Monthly Expenses",
        f"₹{summary['total_expenses']:,.0f}",
        delta=f"-₹{summary['expense_change']:,.0f}"
    )

with col3:
    savings = summary['total_income'] - summary['total_expenses']
    savings_rate = (savings / summary['total_income']) * 100
    st.metric(
        "Savings",
        f"₹{savings:,.0f}",
        delta=f"{savings_rate:.1f}%"
    )

with col4:
    st.metric(
        "Total Debt",
        f"₹{summary['total_debt']:,.0f}"
    )
```

---

## Extension Guide

### Adding a New AI Agent

1. **Create Agent Class**:

```python
# agents/ai_agents.py

class TaxPlannerAgent(BaseFinancialAgent):
    """Agent specialized in tax planning"""
    
    def __init__(self, openrouter_api_key: str = None):
        super().__init__("TaxPlanner", "anthropic/claude-3.5-sonnet", openrouter_api_key)
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        user_context = self.get_user_context(user_id)
        
        system_prompt = f"""You are an expert Tax Planning Agent...
        
        USER PROFILE:
        - Income: ₹{user_context['user']['monthly_income']:,.2f}
        ...
        
        Your task is to:
        1. Analyze tax liability
        2. Suggest tax-saving investments
        3. Optimize deductions under 80C, 80D, etc.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
```

2. **Register in Orchestrator**:

```python
# agents/ai_agents.py - AgentOrchestrator.__init__

self.agents = {
    'debt_analyzer': DebtAnalyzerAgent(openrouter_api_key),
    'savings_strategy': SavingsStrategyAgent(openrouter_api_key),
    'investment_advisor': InvestmentAdvisorAgent(openrouter_api_key),
    'budget_planner': BudgetPlannerAgent(openrouter_api_key),
    'retirement_planner': RetirementPlannerAgent(openrouter_api_key),
    'tax_planner': TaxPlannerAgent(openrouter_api_key)  # New agent
}
```

3. **Update Router**:

```python
# agents/ai_agents.py - AgentOrchestrator.route_query

routing_prompt = f"""...
Available Agents:
...
- tax_planner: For tax optimization, deductions, tax-saving investments
...
"""
```

### Adding a New Document Type

1. **Update Models**:

```python
# database/models.py

class User(Base):
    # Add new document flag
    has_tax_documents = Column(Boolean, default=False)
```

2. **Create Processor**:

```python
# processors/tax_document_processor.py

class TaxDocumentProcessor:
    def extract_tax_data(self, processed_doc):
        """Extract tax-specific information"""
        # Implementation
        pass
```

3. **Update Document Processor**:

```python
# processors/document_processor.py

def extract_financial_data(self, processed_doc, document_type):
    if document_type == 'tax_document':
        return self.tax_processor.extract_tax_data(processed_doc)
    # ... existing code
```

---

**For more details, refer to the code comments in each module.**

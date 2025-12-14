# 🏗️ System Architecture & Application Flows

Complete architecture diagrams, user flows, and technical implementation details for Personal Finance Coach.

---

## Tech Stack Overview

### Frontend
- **Web App**: Streamlit (Python)
- **State Management**: `st.session_state`
- **UI Components**: Native Streamlit widgets

### Backend & API
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy or Drizzle ORM (if using Node.js layer)

### AI & ML Stack
- **Frameworks**: LangChain, LlamaIndex, LangGraph (Agentic workflows)
- **Embeddings**: Hugging Face Transformers (sentence-transformers)
- **Vector Store**: ChromaDB / Weaviate
- **LLMs**: OpenRouter API (Mistral, Llama models)
- **RAG**: LangChain + LlamaIndex for document indexing & retrieval

### Infrastructure
- **Hosting**: Streamlit Cloud (Frontend) or Railway (Full Stack)
- **Storage**: S3 compatible (optional for uploads)
- **Caching**: Redis (for embeddings/API caching)

---

## 1. System Architecture Overview

```mermaid
graph LR
    subgraph "Client Layer"
        WEB[Web App<br/>Streamlit]
    end
    
    subgraph "API Layer"
        GATEWAY[API Gateway<br/>FastAPI + Auth]
    end
    
    subgraph "Business Logic Layer"
        PROFILE[Profile Service]
        ANALYZER[Financial Analyzer]
        BUCKET[Bucket Engine]
        RULE[Rule Engine]
        PLANNER[Plan Generator]
        TRACKER[Tracking Engine]
        NUDGE[Notification Service]
    end
    
    subgraph "AI/ML Layer"
        AGENT[LangGraph Agent<br/>Agentic RAG]
        RAG[RAG Pipeline<br/>LangChain]
        EMBED[Embeddings<br/>HuggingFace]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>User Data)]
        VECTOR[(ChromaDB<br/>Knowledge Base)]
        CACHE[(Redis<br/>Sessions)]
    end
    
    subgraph "External Services"
        EMAIL[Email Service]
        LLM[OpenRouter<br/>Mistral/Llama]
    end
    
    WEB --> GATEWAY
    
    GATEWAY --> PROFILE
    GATEWAY --> ANALYZER
    GATEWAY --> PLANNER
    GATEWAY --> TRACKER
    GATEWAY --> AGENT
    
    PROFILE --> PG
    ANALYZER --> PG
    BUCKET --> PG
    RULE --> PG
    PLANNER --> PG
    TRACKER --> PG
    
    AGENT --> RAG
    RAG --> EMBED
    RAG --> VECTOR
    RAG --> LLM
    
    NUDGE --> EMAIL
    
    style RULE fill:#90EE90,color:#ffff00
    style ANALYZER fill:#90EE90,color:#ffff00
    style BUCKET fill:#90EE90,color:#ffff00
    style AGENT fill:#FFD700,color:#ffff00
    style RAG fill:#FFD700,color:#ffff00
    style EMBED fill:#FFD700,color:#ffff00
    style LLM fill:#FFD700,color:#ffff00

```

---

## 2. Complete User Journey Flow

```mermaid
flowchart TD
    START([User Opens App]) --> AUTH{Authenticated?}
    
    AUTH -->|No| SIGNUP[Sign Up / Login]
    AUTH -->|Yes| CHECK_PROFILE{Profile<br/>Complete?}
    
    SIGNUP --> CREATE_ACCOUNT[Create Account]
    CREATE_ACCOUNT --> CHECK_PROFILE
    
    CHECK_PROFILE -->|No| ONBOARDING[Start Onboarding]
    CHECK_PROFILE -->|Yes| DASHBOARD[Dashboard]
    
    ONBOARDING --> STEP1[Step 1: Basic Profile<br/>Age, Country, Risk, Dependents]
    STEP1 --> STEP2[Step 2: Financial Snapshot<br/>Income, Expenses, Savings]
    STEP2 --> STEP3[Step 3: Assets<br/>Cash, FD, MF, Stocks, etc.]
    STEP3 --> STEP4[Step 4: Liabilities<br/>Loans, Credit Cards]
    STEP4 --> STEP5[Step 5: Goals<br/>Emergency, House, Retirement]
    
    STEP5 --> SYSTEM_ANALYSIS[System Analyzes Data]
    
    SYSTEM_ANALYSIS --> CALC[Calculate Metrics<br/>Net Worth, Savings Rate,<br/>Debt Ratios, Emergency Months]
    
    CALC --> BUCKETIZE[Auto-Bucketize Money<br/>Emergency, Debt,<br/>Short-term, Long-term]
    
    BUCKETIZE --> GENERATE_PLAN[Generate Plan<br/>Top 3 Actions +<br/>Monthly Targets]
    
    GENERATE_PLAN --> SHOW_PLAN[Show Plan to User]
    
    SHOW_PLAN --> USER_REVIEW{User Reviews}
    
    USER_REVIEW -->|Has Questions| WHY_THIS[Click "Why This?"<br/>RAG Explanation]
    WHY_THIS --> USER_REVIEW
    
    USER_REVIEW -->|Accepts Plan| DASHBOARD
    
    DASHBOARD --> USER_ACTION{What Next?}
    
    USER_ACTION -->|View Progress| PROGRESS_CHART[Progress Charts<br/>Net Worth, Debt Trend]
    USER_ACTION -->|Monthly Update| MONTHLY_CHECKIN[Monthly Check-in Form]
    USER_ACTION -->|Edit Data| EDIT_PROFILE[Edit Profile/Assets/Goals]
    USER_ACTION -->|Ask Question| ASK_AI[Ask AI Assistant]
    USER_ACTION -->|View Goals| GOAL_DETAIL[Goal Details & Progress]
    
    MONTHLY_CHECKIN --> INPUT_PROGRESS[Enter:<br/>Saved Amount<br/>Invested Amount<br/>Debt Paid<br/>Notes]
    
    INPUT_PROGRESS --> TRACK_PROGRESS[System Compares<br/>Actual vs Target]
    
    TRACK_PROGRESS --> STATUS{Status?}
    
    STATUS -->|On Track| ENCOURAGE[Show Encouragement<br/>"Great job! Keep going"]
    STATUS -->|Ahead| CELEBRATE[Celebrate Success<br/>"You're ahead! 🎉"]
    STATUS -->|Behind| CORRECT[Correction Nudge<br/>"Here's how to catch up"]
    
    ENCOURAGE --> DASHBOARD
    CELEBRATE --> DASHBOARD
    CORRECT --> DASHBOARD
    
    PROGRESS_CHART --> DASHBOARD
    EDIT_PROFILE --> SYSTEM_ANALYSIS
    ASK_AI --> WHY_THIS
    GOAL_DETAIL --> DASHBOARD
    
    DASHBOARD --> MILESTONE{Goal<br/>Achieved?}
    MILESTONE -->|No| USER_ACTION
    MILESTONE -->|Yes| SUCCESS([Success!<br/>Financial Freedom 🎯])
    
    style START fill:#87CEEB
    style SUCCESS fill:#90EE90
    style SYSTEM_ANALYSIS fill:#FFD700
    style BUCKETIZE fill:#FFD700
    style GENERATE_PLAN fill:#FFD700
    style WHY_THIS fill:#FFA500
```

---

## 3. Data Processing Flow

```mermaid
flowchart LR
    INPUT[User Input<br/>Profile + Snapshot] --> VALIDATE[Validation<br/>Check Ranges]
    
    VALIDATE --> CALCULATE[Calculate Metrics]
    
    subgraph "Calculations"
        C1[Net Worth<br/>Assets - Liabilities]
        C2[Savings Rate<br/>Surplus / Income]
        C3[Emergency Months<br/>Savings / Expenses]
        C4[Debt-to-Income<br/>Debt / Income]
    end
    
    CALCULATE --> C1 & C2 & C3 & C4
    
    C1 & C2 & C3 & C4 --> RULES[Rule Engine]
    
    subgraph "Rules"
        R1{Emergency<br/>< 3 months?}
        R2{High-Interest<br/>Debt > 12%?}
        R3{Savings Rate<br/>< 20%?}
        R4{Goals<br/>Timeline?}
    end
    
    RULES --> R1 & R2 & R3 & R4
    
    R1 & R2 & R3 & R4 --> BUCKETS[Bucketization]
    
    subgraph "Buckets"
        B1[Emergency Fund]
        B2[Debt Payoff]
        B3[Short-term Goals]
        B4[Long-term Wealth]
    end
    
    BUCKETS --> B1 & B2 & B3 & B4
    
    B1 & B2 & B3 & B4 --> PLAN[Generate Plan<br/>Top 3 Actions]
    
    PLAN --> OUTPUT[Personalized Plan<br/>+ Monthly Targets]
    
    OUTPUT --> SAVE[(Save to Database)]
    SAVE --> DISPLAY[Display to User]
```

---

## 4. Agentic RAG System ("Why This?")

```mermaid
flowchart TB
    USER[User asks:<br/>"Why pay debt first?"] --> LANGRAPH_AGENT[LangGraph Agent Node]
    
    LANGRAPH_AGENT --> ROUTING{Agent Decision}
    
    ROUTING -->|Need Context| RETRIEVAL[RAG Retrieval Tool]
    ROUTING -->|Can Answer| GENERATION
    
    RETRIEVAL --> EMBED[HuggingFace Embeddings<br/>sentence-transformers]
    
    EMBED --> VECTOR_SEARCH[Semantic Search<br/>ChromaDB]
    
    VECTOR_SEARCH --> DOCS[(Knowledge Base<br/>Debt Strategy<br/>Investment Rules<br/>Tax Planning)]
    
    DOCS --> RERANK[Rerank Results<br/>by Relevance]
    
    RERANK --> CONTEXT[Build Context Window]
    
    CONTEXT --> GENERATION[LLM Generation Node<br/>OpenRouter API]
    
    GENERATION --> VALIDATE[Validation Node<br/>Check Citations]
    
    VALIDATE --> RESPONSE{Quality OK?}
    
    RESPONSE -->|No| LANGRAPH_AGENT
    RESPONSE -->|Yes| OUTPUT[Format Response<br/>+ Sources + Confidence]
    
    OUTPUT --> DISPLAY[Display to User]
    
    style LANGRAPH_AGENT fill:#FFD700
    style RETRIEVAL fill:#90EE90
    style EMBED fill:#87CEEB
    style GENERATION fill:#FFA500
```

---

## 5. Rule Engine Decision Tree

```mermaid
flowchart TD
    START[User Profile Analysis] --> CHECK_EMERGENCY{Emergency Fund > 3 months?}
    CHECK_EMERGENCY -->|No| PRIORITY1[Priority 1: Build Emergency Fund]
    CHECK_EMERGENCY -->|Yes| CHECK_DEBT
    CHECK_DEBT{High-Interest Debt > 12%?}
    CHECK_DEBT -->|Yes| PRIORITY2[Priority 2: Pay High-Interest Debt]
    CHECK_DEBT -->|No| CHECK_SAVINGS
    CHECK_SAVINGS{Savings Rate > 20%?}
    CHECK_SAVINGS -->|No| PRIORITY3[Priority 3: Increase Savings Rate]
    CHECK_SAVINGS -->|Yes| CHECK_GOALS
    CHECK_GOALS{Has Goals?}
    CHECK_GOALS -->|Yes| ALLOCATE_GOALS
    CHECK_GOALS -->|No| DEFAULT_ALLOCATION[Default Allocation]
    ALLOCATE_GOALS --> SHORT_TERM{Goal < 3 years?}
    SHORT_TERM -->|Yes| SHORT_BUCKET[Short-term bucket]
    SHORT_TERM -->|No| LONG_TERM
    LONG_TERM{Goal > 5 years?}
    LONG_TERM -->|Yes| GROWTH_BUCKET[Long-term growth]
    LONG_TERM -->|No| MID_BUCKET[Mid-term bucket]
    PRIORITY1 --> RISK_ADJUST
    PRIORITY2 --> RISK_ADJUST
    PRIORITY3 --> RISK_ADJUST
    SHORT_BUCKET --> RISK_ADJUST
    MID_BUCKET --> RISK_ADJUST
    GROWTH_BUCKET --> RISK_ADJUST
    DEFAULT_ALLOCATION --> RISK_ADJUST
    RISK_ADJUST{Risk Profile?}
    RISK_ADJUST -->|Low| LOW_RISK[Reduce Equity]
    RISK_ADJUST -->|Medium| MED_RISK[Balanced]
    RISK_ADJUST -->|High| HIGH_RISK[Increase Equity]
    LOW_RISK --> FINAL_PLAN[Generate Final Plan]
    MED_RISK --> FINAL_PLAN
    HIGH_RISK --> FINAL_PLAN
    style FINAL_PLAN fill:#90EE90
```

---

## 6. Monthly Progress Tracking Loop

```mermaid
stateDiagram-v2
    [*] --> PlanCreated: User completes onboarding
    
    PlanCreated --> SetTargets: System sets monthly targets
    
    SetTargets --> UserExecutes: User follows plan
    
    UserExecutes --> MonthEnd: End of month arrives
    
    MonthEnd --> SelfReport: User submits progress
    
    SelfReport --> EvaluateProgress: System evaluates
    
    EvaluateProgress --> OnTrack: Met all targets
    EvaluateProgress --> Ahead: Exceeded targets
    EvaluateProgress --> Behind: Missed targets
    
    OnTrack --> SendEncouragement: "Great job! 💪"
    Ahead --> SendCelebration: "Amazing! 🎉"
    Behind --> SendCorrection: "Let's adjust 🔧"
    
    SendEncouragement --> UpdateProjections
    SendCelebration --> UpdateProjections
    SendCorrection --> UpdateProjections
    
    UpdateProjections --> SetTargets: Next month
    
    SetTargets --> CheckGoals: Quarterly review
    
    CheckGoals --> GoalAchieved: Target met
    CheckGoals --> ContinueTracking: Keep going
    
    ContinueTracking --> SetTargets
    GoalAchieved --> [*]: Success! 🎯
```

---

## 7. Plan Generation Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant API
    participant Analyzer
    participant Rules
    participant DB

    User->>UI: Submit financial data
    UI->>API: POST /api/plan/generate
    
    API->>Analyzer: Calculate metrics
    Analyzer->>DB: Fetch user data
    DB-->>Analyzer: Profile, Assets, Liabilities
    
    Analyzer->>Analyzer: Calculate:<br/>- Net Worth<br/>- Savings Rate<br/>- Emergency Months
    
    Analyzer->>Rules: Apply business rules
    
    Rules->>Rules: Check emergency fund
    Rules->>Rules: Check high-interest debt
    Rules->>Rules: Check savings rate
    Rules->>Rules: Allocate goals to buckets
    Rules->>Rules: Risk-adjust allocations
    
    Rules-->>Analyzer: Recommendations
    
    Analyzer->>DB: Save plan
    DB-->>Analyzer: Plan saved
    
    Analyzer-->>API: Return plan
    API-->>UI: Send response
    UI-->>User: Display:<br/>- Top 3 actions<br/>- Monthly targets<br/>- Projections
```

---

## 8. LangChain RAG Implementation Architecture

```mermaid
graph TB
    subgraph "LangChain RAG Pipeline"
        QUERY[User Question] --> PROMPT_TEMPLATE[Prompt Template]
        
        PROMPT_TEMPLATE --> ROUTER{Query Routing}
        
        ROUTER -->|Financial Query| FINANCIAL_CHAIN[Financial QA Chain]
        ROUTER -->|General Query| GENERAL_CHAIN[General QA Chain]
        
        FINANCIAL_CHAIN --> RETRIEVER[Vector Store Retriever]
        
        RETRIEVER --> CHROMADB[(ChromaDB<br/>Financial Docs)]
        
        CHROMADB --> CONTEXT_BUILDER[Context Builder]
        
        CONTEXT_BUILDER --> LLM_CHAIN[LLM Chain<br/>OpenRouter]
        
        LLM_CHAIN --> OUTPUT_PARSER[Output Parser]
        
        OUTPUT_PARSER --> RESPONSE[Structured Response]
        
        GENERAL_CHAIN --> LLM_CHAIN
    end
    
    subgraph "Knowledge Base"
        DOCS[Financial Guides] --> SPLITTER[Text Splitter]
        SPLITTER --> EMBEDDER[HuggingFace<br/>Embeddings]
        EMBEDDER --> CHROMADB
    end
    
    style RETRIEVER fill:#90EE90
    style CHROMADB fill:#87CEEB
    style LLM_CHAIN fill:#FFD700
```

---

## API Architecture

### Key Endpoints

```
POST   /api/auth/register       - Create new user
POST   /api/auth/login          - Login user
GET    /api/profile             - Get user profile
PUT    /api/profile             - Update profile

POST   /api/snapshot            - Create financial snapshot
GET    /api/snapshot/latest     - Get latest snapshot

POST   /api/assets              - Add asset
GET    /api/assets              - List assets
PUT    /api/assets/:id          - Update asset
DELETE /api/assets/:id          - Delete asset

POST   /api/liabilities         - Add liability
GET    /api/liabilities         - List liabilities
PUT    /api/liabilities/:id     - Update liability

POST   /api/goals               - Add goal
GET    /api/goals               - List goals

POST   /api/plan/generate       - Generate financial plan
GET    /api/plan/current        - Get current plan

POST   /api/progress            - Submit monthly progress
GET    /api/progress            - Get progress history

POST   /api/rag/ask             - Ask RAG system
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Frontend"
        STREAMLIT_CLOUD[Streamlit Cloud<br/>Streamlit App]
    end
    
    subgraph "Backend"
        RAILWAY[Railway<br/>FastAPI Backend]
    end
    
    subgraph "Databases"
        PG[(Neon PostgreSQL<br/>Serverless)]
        CHROMA[(ChromaDB<br/>Self-hosted)]
        REDIS[(Upstash Redis<br/>Serverless)]
    end
    
    subgraph "External APIs"
        OPENROUTER[OpenRouter<br/>LLM API]
        HUGGINGFACE[HuggingFace<br/>Embeddings]
        EMAIL[SendGrid<br/>Email]
    end
    
    STREAMLIT_CLOUD --> RAILWAY
    RAILWAY --> PG
    RAILWAY --> CHROMA
    RAILWAY --> REDIS
    RAILWAY --> OPENROUTER
    RAILWAY --> HUGGINGFACE
    RAILWAY --> EMAIL
```

---

## AI/ML Pipeline Details

### Embedding Generation
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(documents)
```

### LangChain Integration
```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.llms import OpenRouter

vectorstore = Chroma(embedding_function=embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenRouter(api_key=OPENROUTER_KEY),
    retriever=vectorstore.as_retriever()
)
```

### LangGraph Agent
```python
from langgraph.graph import StateGraph

workflow = StateGraph()
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("generate", generation_node)
workflow.add_node("validate", validation_node)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "validate")

agent = workflow.compile()
```

---

**Last Updated:** 2025-12-13  
**Version:** 3.2 (Complete AI Engineering Stack)  
**Tech Stack:** Streamlit + FastAPI + LangChain + LlamaIndex + LangGraph + Hugging Face + OpenRouter

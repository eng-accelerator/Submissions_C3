# 🚨 Multi-Agent DevOps Incident Analysis Suite

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

AI-powered incident analysis system using **LangGraph**, **OpenAI (via OpenRouter)**, and **LanceDB** for intelligent DevOps automation.

---

## 🎯 Overview

This system automates incident analysis using 5 specialized AI agents orchestrated through LangGraph:

1. **Log Classifier Agent** - Parses and categorizes incidents (P0-P3)
2. **Remediation Agent** - Generates step-by-step fixes with CLI commands
3. **Notification Agent** - Creates Slack-ready alerts
4. **Cookbook Agent** - Synthesizes operational runbooks
5. **JIRA Agent** - Auto-generates tickets for critical issues

### Key Features

✅ **Multi-Agent Orchestration** - LangGraph manages sequential & parallel execution  
✅ **RAG with LanceDB** - Historical incident retrieval for context-aware analysis  
✅ **OpenAI Models** - GPT-4, GPT-4 Turbo, GPT-3.5 Turbo support  
✅ **Multi-turn Chat** - Interactive Q&A about incidents  
✅ **Real-time Dashboard** - Live analytics and metrics  
✅ **Export Capabilities** - JSON, Markdown, CSV formats  
✅ **Integrations** - Slack webhooks & JIRA REST API  

---

## 🏗️ Architecture
┌─────────────┐
│  User Input │
└──────┬──────┘
│
▼
┌─────────────────┐
│  RAG Retrieval  │ (LanceDB - Historical Context)
└────────┬────────┘
│
▼
┌─────────────────┐
│ Log Classifier  │ (OpenAI GPT-4)
└────────┬────────┘
│
▼
┌─────────────────┐
│  Remediation    │
└────┬───┬───┬────┘
│   │   │
▼   ▼   ▼
┌────┬────┬────┐
│Notify│Cook│JIRA│ (Parallel Execution)
└─────┴────┴────┘
│
▼
┌─────────┐
│ Results │
└─────────┘

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **Orchestration** | LangGraph |
| **LLM** | OpenAI GPT-4 (via OpenRouter) |
| **Vector DB** | LanceDB |
| **Frontend** | Streamlit |
| **Integrations** | Slack, JIRA |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenRouter API key with OpenAI credits
- (Optional) Slack webhook URL
- (Optional) JIRA API credentials

### 1. Installation
```bash
# Clone/create project directory
mkdir devops_incident_suite
cd devops_incident_suite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

**.env file:**
```bash
# Required: OpenRouter API Key (with OpenAI credits)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional: Integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_token
```

### 3. Get OpenRouter API Key

1. Visit **https://openrouter.ai/**
2. Sign up/Login
3. Go to **Keys** → **Create Key**
4. Add credits (ensure OpenAI models are enabled)
5. Copy key to `.env`

### 4. Run Application
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

### 5. First Analysis

1. Click **"Load Sample Logs"** button
2. Select **GPT-4** or **GPT-4 Turbo** from dropdown
3. Click **"🚀 Analyze Incidents"**
4. Watch agents execute in real-time!

---

## 📊 Usage Guide

### Basic Workflow
Input Logs → Analyze → View Results → Export/Share

### Tab Overview

#### 📝 Analysis Tab
- Input logs (paste or load sample)
- Select OpenAI model
- View classified incidents
- See remediation plans
- Review notifications & tickets

#### 💬 Chat Tab
- Ask questions about incidents
- Multi-turn conversation
- Context-aware responses
- Example: "What's the most critical issue?"

#### 📊 Dashboard Tab
- Performance metrics
- Token usage tracking
- Service impact analysis
- Agent execution times

#### 🔍 RAG Explorer Tab
- Search historical incidents
- Semantic similarity search
- View past patterns

---

## 🤖 Supported Models

Your OpenRouter key with OpenAI credits supports:

| Model | ID | Best For | Cost |
|-------|----|---------|----|
| **GPT-4 Turbo** | `openai/gpt-4-turbo` | Complex reasoning | $10/M tokens |
| **GPT-4** | `openai/gpt-4` | Highest accuracy | $30/M tokens |
| **GPT-3.5 Turbo** | `openai/gpt-3.5-turbo` | Fast, cost-effective | $1/M tokens |

### Switching Models

**In UI:** Use the dropdown in sidebar

**In Code:**
```python
# config/settings.py
model_name: str = "openai/gpt-4-turbo"  # Change here
```

---

## 🔧 Advanced Configuration

### Custom System Prompts

Edit agent prompts in `agents/*.py`:
```python
# agents/log_classifier.py
CLASSIFIER_SYSTEM_PROMPT = """
Your custom prompt here...
"""
```

### Adjust LangGraph Flow

Modify workflow in `orchestration/graph.py`:
```python
# Add new edges for custom flow
workflow.add_edge("classify", "your_custom_agent")
```

### LanceDB Configuration
```python
# utils/rag_engine.py
# Customize embedding model, distance metric, etc.
```

---

## 📥 Export Formats

### JSON
Full structured data with metadata
```json
{
  "generated_at": "2024-12-14T10:30:00",
  "analysis": { ... }
}
```

### Markdown
Human-readable report
```markdown
# Incident Report
## Summary
- Total: 8 incidents
...
```

### CSV
Spreadsheet-compatible
```csv
ID,Service,Severity,Description
INC-001,payment-service,P0,Database timeout
```

---

## 🔗 Integrations

### Slack Integration
```bash
# 1. Create Slack webhook
#    https://api.slack.com/messaging/webhooks

# 2. Add to .env
SLACK_WEBHOOK_URL=your_webhook_url

# 3. Enable in UI sidebar
☑️ Enable Slack

# 4. Click "Send to Slack" button
```

### JIRA Integration
```bash
# 1. Generate JIRA API token
#    https://id.atlassian.com/manage-profile/security/api-tokens

# 2. Add credentials to .env
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_token

# 3. Enable in UI
☑️ Enable JIRA

# 4. Click "Create JIRA Tickets"
```

---

## 🧪 Testing

### Run Sample Analysis
```bash
# Using sample logs
streamlit run app.py
# Click "Load Sample Logs" → "Analyze"
```

### Test Individual Agents
```python
from agents.log_classifier import LogClassifierAgent
from utils.openrouter_client import OpenRouterClient

client = OpenRouterClient("your-api-key")
agent = LogClassifierAgent(client, "openai/gpt-4-turbo")

result = agent.execute({"logs": "your logs here"})
print(result)
```

### Test RAG Engine
```python
from utils.rag_engine import RAGEngine

rag = RAGEngine("./data/lancedb")
rag.index_incident("INC-001", {"description": "test"})

similar = rag.retrieve_similar_incidents("database timeout")
print(similar)
```

---

## 📈 Performance

### Typical Analysis Times

| Metric | Value |
|--------|-------|
| Total Analysis | 45-60 seconds |
| Per Agent | 8-12 seconds |
| RAG Retrieval | <1 second |
| Total Tokens | ~50K input, ~20K output |

### Cost Estimation

**Per Analysis (10 incidents):**
- GPT-4 Turbo: ~$0.70
- GPT-4: ~$1.50
- GPT-3.5 Turbo: ~$0.07

**Hackathon Demo (10 analyses):** $5-15 total

---

## 🎯 Hackathon Presentation Tips

### Demo Script (5 minutes)

**1. Introduction (30 sec)**
> "We built an AI-powered multi-agent system that automates incident analysis using OpenAI's GPT-4 and LanceDB for intelligent memory."

**2. Architecture (1 min)**
> "Five specialized agents work together through LangGraph:
> - Classifier analyzes logs
> - Remediation generates fixes
> - Three parallel agents create notifications, runbooks, and tickets"

**3. Live Demo (2 min)**
- Load sample logs
- Show agent execution
- Navigate through results
- Demonstrate chat assistant

**4. Key Features (1 min)**
> "Beyond the requirements, we added:
> - RAG with LanceDB for learning
> - Multi-turn chat
> - Real integrations
> - Export to 3 formats"

**5. Technical Depth (30 sec)**
> "We demonstrate mastery of:
> - LangGraph state machines
> - RAG implementation
> - Multi-turn conversations
> - Error handling with retries
> - Production-grade architecture"

### Talking Points

✅ **Model Flexibility**: "We use OpenRouter to access OpenAI models"  
✅ **RAG with LanceDB**: "Fast vector search for historical context"  
✅ **Production Ready**: "Comprehensive error handling, logging, retries"  
✅ **Scalable**: "Handles any log volume, extensible architecture"  

---

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Verify you're in project root
pwd  # Should show: .../devops_incident_suite

# Check all __init__.py exist
find . -name "__init__.py"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**2. API Key Issues**
```bash
# Check .env file
cat .env

# Verify key format
# Should be: OPENROUTER_API_KEY=sk-or-v1-...

# Test key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENROUTER_API_KEY'))"
```

**3. LanceDB Errors**
```bash
# Delete and recreate
rm -rf data/lancedb
mkdir -p data/lancedb

# Restart app
streamlit run app.py
```

**4. Model Not Found**
```bash
# Verify model name format
# Correct: "openai/gpt-4-turbo"
# Wrong: "gpt-4-turbo"

# Check OpenRouter model list
# https://openrouter.ai/models
```

**5. Out of Credits**
```bash
# Check balance at: https://openrouter.ai/settings
# Add credits if needed
# Use cheaper model: "openai/gpt-3.5-turbo"
```

---

## 📚 Project Structure
devops_incident_suite/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── .env                        # Your API keys (gitignored)
├── app.py                      # Main Streamlit app
│
├── config/
│   └── settings.py             # Configuration management
│
├── agents/                     # AI Agents
│   ├── base_agent.py          # Abstract base class
│   ├── log_classifier.py      # Incident classification
│   ├── remediation_agent.py   # Fix generation
│   ├── notification_agent.py  # Slack alerts
│   ├── cookbook_agent.py      # Runbook creation
│   └── jira_agent.py          # Ticket generation
│
├── orchestration/              # LangGraph
│   ├── graph.py               # Workflow definition
│   └── state.py               # State management
│
├── utils/                      # Utilities
│   ├── openrouter_client.py   # OpenRouter API wrapper
│   ├── rag_engine.py          # LanceDB RAG
│   ├── error_handler.py       # Error handling
│   ├── logger.py              # Logging
│   ├── integrations.py        # Slack/JIRA
│   ├── chat_handler.py        # Multi-turn chat
│   ├── export.py              # Export functions
│   └── metrics.py             # Performance tracking
│
└── data/
├── sample_logs.txt         # Sample data
└── lancedb/                # Vector database

---

## 🔐 Security Best Practices

1. **Never commit .env** - Already in .gitignore
2. **Rotate API keys** - Regularly refresh keys
3. **Limit permissions** - Use read-only keys when possible
4. **Monitor usage** - Track API costs
5. **Validate inputs** - Sanitize user-provided logs

---

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment

**Streamlit Cloud:**
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. Deploy on Streamlit Cloud
# https://streamlit.io/cloud

# 3. Add secrets in dashboard
OPENROUTER_API_KEY = "your-key"
```

**Docker:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## 🤝 Contributing

### Adding New Agents

1. Create agent in `agents/your_agent.py`
2. Inherit from `BaseAgent`
3. Define system prompt
4. Implement `build_prompt()` method
5. Add node to LangGraph in `orchestration/graph.py`

Example:
```python
# agents/security_agent.py
from agents.base_agent import BaseAgent

class SecurityAgent(BaseAgent):
    def __init__(self, client, model):
        super().__init__("Security", SYSTEM_PROMPT, client, model)
    
    def build_prompt(self, context):
        return f"Analyze security: {context}"
```

### Adding New Features

- Export formats → `utils/export.py`
- Integrations → `utils/integrations.py`
- UI components → `app.py`

---

## 📖 Learn More

### Resources

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **OpenRouter**: https://openrouter.ai/docs
- **LanceDB**: https://lancedb.github.io/lancedb/
- **Streamlit**: https://docs.streamlit.io/

### Example Use Cases

1. **DevOps Teams** - Automated incident triage
2. **SRE Teams** - Root cause analysis
3. **Platform Engineering** - Service health monitoring
4. **Security Teams** - Threat detection

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- LangGraph by LangChain
- OpenAI GPT-4
- LanceDB
- Streamlit
- OpenRouter

---

## 📧 Support

For issues or questions:
1. Check Troubleshooting section
2. Review GitHub issues
3. Contact: your-email@example.com

---

## 🎓 Citation

If you use this project in research or presentations:
```bibtex
@software{devops_incident_suite,
  title = {Multi-Agent DevOps Incident Analysis Suite},
  year = {2024},
  author = {Your Name},
  url = {https://github.com/yourusername/devops-incident-suite}
}
```

---

**⭐ Star this repo if you find it useful!**

**🏆 Built for Hackathon Excellence**

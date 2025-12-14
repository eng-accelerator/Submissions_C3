# Deep Researcher – Multi‑Agent AI Research System

## Overview

**Deep Researcher** is a LangGraph‑based, multi‑agent AI system designed for **deep, multi‑hop research** across the web, and structured sources. Instead of a single monolithic prompt, the system orchestrates specialized agents that collaborate to retrieve information, critique sources, extract insights, and generate structured research reports.

This project demonstrates **agentic RAG**, **tool‑using LLMs**, and **graph‑based orchestration** suitable for academic research, market intelligence, competitive analysis, and technical due‑diligence.

---

## Key Capabilities

* 🔍 **Multi‑Source Retrieval** – Web search, and URLs
* 🧠 **Agent Specialization** – Each agent has a focused responsibility
* 🔗 **LangGraph Orchestration** – Deterministic, inspectable agent flow
* 🧪 **Critical Analysis & Fact‑Checking** – Reduces hallucinations
* 📝 **Structured Report Generation** – Executive‑ready output
* ⚡ **Safe LLM Invocation** – Centralized error handling and retries

---

## Agent Architecture

The system is composed of multiple cooperating agents located in `agents/`:

| Agent                | Responsibility                                |
| -------------------- | --------------------------------------------- |
| **Retriever Agent**  | Fetches data from web search, URLs, and PDFs  |
| **Analysis Agent**   | Performs deep reasoning and synthesis         |
| **Critique Agent**   | Challenges assumptions and detects weaknesses |
| **Expert Agent**     | Provide expert interpretation of facts        |
| **Fact‑Check Agent** | Verifies claims against sources               |
| **Insights Agent**   | Extracts trends, hypotheses, and implications |
| **Structurer Agent** | Converts raw output into structured sections  |
| **Report Agent**     | Produces the final research report            |

LangGraph coordinates these agents as a **stateful execution graph**, enabling branching, validation, and controlled iteration.

---

## Project Structure

```
deep-researcher/
├── agents/               # All specialized research agents
│   ├── base.py
|   ├── webagents.py
|   ├── retriever.py
│   ├── analysis.py
│   ├── critique.py
|   ├── expert.py
│   ├── factcheck.py
│   ├── insights.py
│   ├── structurer.py
│   └── report.py
├── app.py                # Application entry point
├── graph.py              # LangGraph definition
├── state.py              # Shared graph state schema
├── clients.py            # LLM & external API clients
├── prompts.py            # Centralized prompt templates
├── pdf_utils.py          # PDF ingestion utilities
├── url_utils.py          # URL parsing & validation
├── safe_invoke.py        # Robust LLM call wrapper
├── logger.py             # Structured logging
├── requirements.txt
└── README.md
```

---

## Technology Stack

* **Python 3.10+**
* **LangGraph** – Agent orchestration
* **LangChain** – LLM abstractions & tools
* **OpenRouter API**
* **Tavily / Web Search APIs** 

---

## Installation

```bash
# Clone repository
git clone <your-repo-url>
cd deep-researcher

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Application

```bash
python app.py
```

You will be prompted to provide a **research question or topic**. The system will:

1. Retrieve relevant sources
2. Analyze and cross‑check findings
3. Generate insights
4. Output a structured research report

---

## Example Use Cases

* Academic literature review
* Market & competitor research
* Technology landscape analysis
* Policy or regulatory research
* Startup due‑diligence

---

## Design Principles

* **Separation of Concerns** – One agent, one responsibility
* **Explainability** – Intermediate reasoning is inspectable
* **Reliability** – Fact‑checking and critique reduce errors
* **Extensibility** – New agents can be added easily

---

## Extending the System

You can easily add new agents by:

1. Creating a new agent class in `agents/`
2. Registering it in `graph.py`
3. Updating the shared `state.py` schema if required

Examples:

* Citation Formatter Agent
* Domain‑Specific Expert Agent
* Data Visualization Agent

---

## Limitations

* Dependent on LLM quality and external APIs
* Long research tasks may incur higher token costs
* Web results depend on search provider coverage

---

## Contributing

Contributions are welcome. Please see `CONTRIBUTING.md` for guidelines.

---

## License

MIT License

---

## Contributers

**C3 Eng Acc - Hackathon Group 12**

AI Engineer | Agentic Systems | LLM Applications

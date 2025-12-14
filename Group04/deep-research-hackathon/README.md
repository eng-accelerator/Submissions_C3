# DeepTrace Researcher 🕵️‍♂️

A secure, multi-agent, multi-hop research assistant built with Streamlit, LangGraph, and multi-LLM support (OpenAI, Anthropic, OpenRouter).

## 🚀 Key Features

### 1. **Multi-Agent Orchestration**
Uses a graph of specialized agents to perform deep research:
- **Planner**: Decomposes complex queries into step-by-step plans.
- **Retriever**: Fetches data from Web, ArXiv, PubMed, and more.
- **Analyst**: Extracts key claims and findings.
- **Reviewer (Judge)**: Critiques reports and enforces quality standards.
- **Debater**: Simulates adversarial debates between models.

### 2. **Evaluation Modes**
- **Standard**: Linear research -> Report.
- **Judge Mode (Critique)**: 
    - An AI Judge evaluates the draft report against the objective.
    - If it fails (score < 7/10), it sends specific feedback to a Reviser agent.
    - Loops up to 5 times to perfect the report.
- **Debate Mode (Pro/Con)**: 
    - Simulates a debate between two LLMs (e.g., GPT-4o as Pro vs. Claude 3 Opus as Con).
    - Visualized as a chat dialogue in the UI.

### 3. **Deep Research & X-Ray Visibility**
- **Transparent Execution**: See the exact URLs visited, claims extracted, and plan steps generated in real-time.
- **Academic Access**: Native support for ArXiv, OpenAlex, PubMed, and ClinicalTrials.gov.
- **Finance Focus**: Uses Perplexity (Native or via OpenRouter) for real-time market data.

### 4. **Security & Privacy**
- **Zero-Trust**: No hardcoded API keys.
- **Runtime Injection**: Keys are entered at runtime in the UI.
- **Local Persistence**: Keys can be saved to a local `.env` file (gitignored) for convenience, but are never sent to our servers.

## 🛠️ Setup & Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   streamlit run app.py
   ```

3. **Configure Keys**
   - Open the Sidebar.
   - Select your **LLM Provider** (OpenAI, Anthropic, OpenRouter).
   - Enter necessary API Keys. 
   - *Tip: Click "Save Keys" to persist them locally.*

## 🧩 Architecture

- **Core**: `langgraph`, `langchain`
- **Frontend**: `streamlit`
- **LLMs**: `gpt-4o`, `claude-3-opus`, `perplexity-sonar`

## 🤝 Contribution
1. Fork the repo.
2. Create a feature branch.
3. Submit a PR.

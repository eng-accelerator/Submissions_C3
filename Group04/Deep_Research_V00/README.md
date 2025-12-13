# Multi-Agent Deep Researcher

A sophisticated multi-agent research system that performs deep, multi-hop, multi-modal research with iterative reasoning. Built with LangGraph, LangChain, and Streamlit.

## ⚠️ Important: Python Version Compatibility

**This project requires Python 3.9 - 3.13. Python 3.14+ is NOT supported** due to compatibility issues with Pydantic V1 used by LangChain.

The error you may see:
```
UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.
```

### Solution
- Use Python 3.13 or earlier (recommended: Python 3.11 or 3.12)
- If you must use Python 3.14+, you'll need to wait for LangChain to fully migrate to Pydantic V2

## Features

- 🤖 **Multi-Agent Architecture**: Specialized agents for planning, retrieval, analysis, insight generation, reflection, and reporting
- 🔍 **Multi-Source Research**: Web search (Tavily/DuckDuckGo), document processing (PDF/DOCX), and academic sources
- 🔄 **Iterative Refinement**: Self-reflecting agents that identify gaps and perform follow-up research
- 📊 **Credibility Scoring**: Automatic evaluation of source reliability
- 📄 **Professional Reports**: Generate comprehensive research reports in Markdown and PDF formats
- 🎯 **Discipline-Specific**: Optimized for Scientific, Business, Finance/Law, and IT/AI research

## Installation

1. **Ensure you have Python 3.9-3.13 installed**
   ```bash
   python --version  # Should show 3.9.x to 3.13.x
   ```

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DEEP_Research_V
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API Keys** (Optional but recommended)
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   GEMINI_API_KEY=your_gemini_key
   TAVILY_API_KEY=your_tavily_key
   ```
   
   Or enter them directly in the Streamlit UI sidebar.

## Usage

### Running the Application

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
streamlit run app.py
```

### Using the Interface

1. **Enter API Keys** (if not in `.env`): Use the sidebar to input your API keys
2. **Select Research Discipline**: Choose from:
   - Scientific & Academic Research
   - Business & Market Analysis
   - Finance & Law
   - IT Technology & AI Development
3. **Enter Research Query**: Type your complex research question
4. **Upload Documents** (Optional): Add PDF or DOCX files for context
5. **Add Image/Video URL** (Optional): Include multimodal content
6. **Start Research**: Click "🚀 Start Deep Research"

### Output

The system provides:
- **Executive Summary & Report**: Comprehensive research report
- **Insights & Sources**: Key insights and credibility-scored sources
- **Execution Trace**: Research plan and iteration details
- **Download Options**: PDF and Markdown exports

## Architecture

### Agents

- **PlannerAgent**: Breaks down research queries into structured plans
- **RetrieverAgent**: Executes searches and retrieves information
- **AnalystAgent**: Analyzes and synthesizes findings
- **InsightAgent**: Generates high-level insights and patterns
- **ReflectionAgent**: Evaluates completeness and identifies gaps
- **CredibilityAgent**: Scores source reliability
- **ReportAgent**: Compiles final research reports

### Workflow Graph

```
Planner → Retriever → Insight → Reflection → [Retriever (if needed)] → Reporter
```

## Configuration

### API Providers

The system supports multiple LLM providers:
- **OpenAI** (GPT-4 Turbo)
- **Anthropic** (Claude 3 Opus)
- **Google** (Gemini 1.5 Pro)

### Search Tools

- **Tavily** (Primary): High-quality research search
- **DuckDuckGo** (Fallback): Free web search

## Troubleshooting

### Common Issues

1. **Python 3.14 Compatibility Error**
   - Solution: Use Python 3.13 or earlier

2. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

3. **API Key Errors**
   - Check that API keys are correctly set in `.env` or UI
   - Verify keys are valid and have sufficient credits

4. **Search Failures**
   - Tavily requires an API key for best results
   - DuckDuckGo is used as fallback but may have rate limits

### Testing

Run the verification script:
```bash
python tests/verify_graph.py
```

## Project Structure

```
DEEP_Research_V/
├── agents/          # Agent implementations
├── graph/           # LangGraph workflow and state
├── modules/         # Core modules (LLM factory, document processing, etc.)
├── tools/           # Search and utility tools
├── utils/           # Logging and utilities
├── tests/           # Test scripts
├── app.py           # Streamlit application
├── config.py        # Configuration management
└── requirements.txt # Dependencies
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please open an issue on the repository.


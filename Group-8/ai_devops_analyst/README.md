# AI DevOps Incident Analyst

An AI-powered multi-agent application designed to automate the analysis, remediation, and reporting of DevOps incidents.

## Features

- **Multi-Agent Architecture**: Specialized agents for logging, research, and remediation.
- **RAG Integration**: Upload your internal "Runbooks" or "Cookbooks" (PDF/Text) to ground the AI's responses.
- **Automated Actions**:
  - Creates JIRA tickets for tracked issues.
  - Sends summary notifications to Slack.
- **Interactive UI**: Built with Streamlit for easy file upload and configuration.

## Architecture

The system uses **LangGraph** to orchestrate a stateful workflow between agents.

```mermaid
graph TD
    A[Start] --> B[Log Reader Agent]
    B --> C[Cookbook Agent (RAG)]
    C --> D[Remediation Agent]
    D --> E[JIRA Agent]
    E --> F[Notification Agent]
    F --> G[End]
```

### Components
1.  **Log Reader**: Extracts structured data (Error Type, Timestamp, Severity) from raw log text using LLM.
2.  **Cookbook Agent**: Uses RAG (FAISS + OpenAI Embeddings) to find relevant remediation steps from uploaded docs.
3.  **Remediation Agent**: Combines the log error and the cookbook context to generate a specific fix.
4.  **JIRA Agent**: Connects to the JIRA API to create a ticket with the incident details.
5.  **Notification Agent**: Pushes the high-level summary to a designated Slack channel.

## Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd ai_devops_analyst
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup**:
    Create a `.env` file (optional, or use UI):
    ```env
    OPENROUTER_API_KEY=sk-or-v1-...
    JIRA_URL=https://your-domain.atlassian.net
    JIRA_USER=user@example.com
    JIRA_API_TOKEN=your-token
    SLACK_WEBHOOK_URL=https://hooks.slack.com/...
    ```

4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## Usage Step-by-Step

1.  **Open the App**: Navigate to logic `http://localhost:8501`.
2.  **Configure Keys**: In the sidebar, enter your OpenRouter API Key. (Optional: JIRA/Slack details).
3.  **Upload Data**:
    *   **DevOps Log**: Upload a text file containing the error logs.
    *   **Cookbook**: (Optional) Upload a PDF or Text file with your standard operating procedures.
4.  **Start Analysis**: Click the "Start Analysis" button.
5.  **View Results**:
    *   The AI will display the extracted error info.
    *   A detailed Remediation Plan will be shown.
    *   Status of JIRA ticket creation and Slack notification will be displayed.

## Presentation
To generate a PowerPoint overview of this project, run:
```bash
python create_presentation.py
```
This will create `AI_DevOps_Analyst_Presentation.pptx` in the project root.

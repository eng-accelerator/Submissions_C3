from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from core.llm import get_llm
import json

def log_reader_agent(state: dict, api_key: str):
    """
    Analyzes the log content to extract error type, timestamp, and details.
    """
    messages = state.get("messages", [])
    log_content = state.get("log_data", "")
    
    if not log_content:
        return {"errors": ["No log content provided."]}

    # Truncate log content to avoid context limit errors (400 Bad Request)
    # gpt-4o-mini has 128k context, but we keep it safe at ~30k chars to leave room for output and prompt
    if len(log_content) > 30000:
        log_content = log_content[:30000] + "\n...(truncated)..."

    llm = get_llm(api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert DevOps Log Analyzer. Your task is to read the provided log snippet and extract structured information."),
        ("user", "Analyze the following log:\n\n{log_content}\n\nReturn a JSON object with keys: 'error_type', 'timestamp', 'summary', 'severity', 'stack_trace_summary'.")
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({"log_content": log_content})
        content = response.content.strip()
        
        # Helper to clean markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        
        # Try to parse it to ensure it's valid JSON, though we return the string/dict as needed by the state
        try:
             json_content = json.loads(content)
             return {"analysis_results": json_content, "messages": messages + [("ai", "Log analysis complete.")]}
        except json.JSONDecodeError:
             # Fallback: return raw text if not valid JSON
             return {"analysis_results": {"raw_analysis": content}, "messages": messages + [("ai", "Log analysis complete (Text Only).")]}

    except Exception as e:
        return {"errors": [str(e)]}

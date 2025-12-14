from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    """Application settings and configuration"""
    
    # Disable protected namespace warning for model_name
    model_config = {"protected_namespaces": ()}
    
    # OpenRouter API Key (Required)
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Model Configuration - OpenRouter model identifiers
    # OpenAI: openai/gpt-4-turbo, openai/gpt-4, openai/gpt-3.5-turbo
    # Claude: anthropic/claude-sonnet-4-20250514, anthropic/claude-3.5-sonnet
    # Default: Claude Sonnet 4 (as per requirements)
    model_name: str = "anthropic/claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # OpenRouter Configuration
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    app_name: str = "DevOps-Incident-Suite"
    site_url: str = "http://localhost:8501"
    
    # LanceDB Configuration
    lancedb_path: str = "./data/lancedb"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Hugging Face API (Optional - for RAG embeddings)
    huggingface_api_key: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    
    # Hugging Face API (Optional - for RAG embeddings)
    huggingface_api_key: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    
    # Integration Settings (Optional)
    slack_webhook_url: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    jira_url: Optional[str] = os.getenv("JIRA_URL")
    jira_email: Optional[str] = os.getenv("JIRA_EMAIL")
    jira_api_token: Optional[str] = os.getenv("JIRA_API_TOKEN")

settings = Settings()
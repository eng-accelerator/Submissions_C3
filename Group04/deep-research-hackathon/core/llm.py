from langchain_openai import ChatOpenAI
from core.api_registry import APIRegistry

def get_llm():
    """
    Returns a configured ChatOpenAI instance.
    Prioritizes OpenRouter if key exists, otherwise OpenAI.
    Returns None if no keys.
    """
    provider = APIRegistry.get_key("llm_provider") or "OpenAI"
    
    # 1. OpenRouter
    if provider == "OpenRouter":
        key = APIRegistry.get_key("openrouter_key")
        model = APIRegistry.get_key("llm_model") or "anthropic/claude-3.5-sonnet"
        if key:
            print(f"DEBUG: Initializing OpenRouter with {model}")
            return ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key,
                model=model,
                temperature=0.7
            )

    # 2. Anthropic
    elif provider == "Anthropic":
        key = APIRegistry.get_key("anthropic_key")
        if key:
            print("DEBUG: Initializing Anthropic Claude 3.5 Sonnet")
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                api_key=key,
                model="claude-3-5-sonnet-latest",
                temperature=0.7
            )

    # 3. OpenAI (Default)
    else:
        key = APIRegistry.get_key("llm")
        if key:
            print("DEBUG: Initializing OpenAI GPT-4o")
            return ChatOpenAI(
                api_key=key,
                model="gpt-4o",
                temperature=0.7
            )
    
    return None

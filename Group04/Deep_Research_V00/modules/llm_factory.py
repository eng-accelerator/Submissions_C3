from config import Config
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.logging import logger

class LLMFactory:
    """
    Creates LLM instances based on available keys and user preference.
    """
    
    @staticmethod
    def create_llm(model_provider: str = "openai", temperature: float = 0.5):
        """
        Create and return a configured Chat Model.
        """
        api_key = Config.get_api_key(model_provider)
        
        if not api_key:
            # Fallback logic could go here (e.g., try another provider)
            logger.error(f"No API Key found for {model_provider}")
            # If specifically requested but missing, try to find ANY valid key
            if model_provider == "openai" and Config.get_api_key("anthropic"):
                logger.info("Falling back to Anthropic")
                return LLMFactory.create_llm("anthropic", temperature)
            return None

        if model_provider == "openai":
            # Check for OpenRouter key pattern
            base_url = None
            model_name = "gpt-4-turbo"
            
            if api_key.startswith("sk-or-v1"):
                base_url = "https://openrouter.ai/api/v1"
                # OpenRouter usually maps models differently or proxies them. 
                # Let's use a popular routing model or default to what user wants
                # For this key, we'll stick to a solid default
                model_name = "openai/gpt-4-turbo" 
                
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url
            )
        elif model_provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=temperature,
                api_key=api_key
            )
        elif model_provider == "gemini":
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=temperature,
                google_api_key=api_key
            )
        else:
            logger.error(f"Unsupported provider: {model_provider}")
            return None

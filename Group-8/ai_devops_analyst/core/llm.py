import os
import json
from typing import Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
import requests

class SimpleOpenRouterLLM(BaseChatModel):
    """
    A simplified Chat Model that uses requests to call OpenRouter directly.
    This avoids any payload compatibility issues with standard wrappers.
    """
    api_key: str
    model_name: str = "openai/gpt-3.5-turbo"
    api_url: str = "https://openrouter.ai/api/v1/chat/completions"

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://ai-devops-analyst.com",
            "X-Title": "AI DevOps Analyst",
            "Content-Type": "application/json"
        }
        
        # Convert LangChain messages to OpenAI format
        msgs = []
        for m in messages:
            if isinstance(m, SystemMessage):
                msgs.append({"role": "system", "content": m.content})
            elif isinstance(m, HumanMessage):
                msgs.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                msgs.append({"role": "assistant", "content": m.content})
            else:
                msgs.append({"role": "user", "content": str(m.content)})
                
        payload = {
            "model": self.model_name,
            "messages": msgs
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result_json = response.json()
            
            content = result_json["choices"][0]["message"]["content"]
            
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])
            
        except Exception as e:
            # Return error as content so the app shows it rather than crashing
            error_msg = f"Error calling OpenRouter: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" Response: {e.response.text}"
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=error_msg))])

    @property
    def _llm_type(self) -> str:
        return "openrouter_simple"

def get_llm(api_key: str, model_name: str = "openai/gpt-4o-mini"):
    if not api_key:
        raise ValueError("OpenRouter API Key is required.")
    
    return SimpleOpenRouterLLM(api_key=api_key, model_name=model_name)

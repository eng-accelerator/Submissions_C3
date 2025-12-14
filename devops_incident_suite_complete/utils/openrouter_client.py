import requests
import json
from typing import Dict, List, Optional

class OpenRouterClient:
    """OpenRouter API client for OpenAI models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "DevOps-Incident-Suite"
        }
        self.usage_stats = {"total_tokens": 0, "total_cost": 0.0}
    
    def create_message(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.1,
        system: Optional[str] = None
    ) -> Dict:
        """
        Create a completion using OpenRouter API with OpenAI models
        
        Args:
            model: OpenAI model ID (e.g., "openai/gpt-4-turbo")
            messages: List of message dicts
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: Optional system message
        """
        # Prepare messages
        formatted_messages = []
        
        # Add system message if provided
        if system:
            formatted_messages.append({"role": "system", "content": system})
        
        # Add user messages
        formatted_messages.extend(messages)
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Track usage
        if 'usage' in result:
            self.usage_stats["total_tokens"] += result['usage'].get('total_tokens', 0)
        
        return result
    
    def extract_content(self, response: Dict) -> str:
        """Extract text content from OpenRouter response"""
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to extract content: {e}")
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        return self.usage_stats
    
    def reset_usage_stats(self):
        """Reset usage tracking"""
        self.usage_stats = {"total_tokens": 0, "total_cost": 0.0}
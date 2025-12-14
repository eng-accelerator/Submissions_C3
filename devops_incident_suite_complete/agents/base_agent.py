from utils.openrouter_client import OpenRouterClient
from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import time
from utils.logger import CustomLogger
from utils.error_handler import handle_agent_errors

class BaseAgent(ABC):
    """Base class for all agents with common functionality"""
    
    def __init__(self, name: str, system_prompt: str, client: OpenRouterClient, model: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = client
        self.model = model
        self.logger = CustomLogger(name)
        self.execution_time = 0
    
    @handle_agent_errors
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with error handling and logging"""
        start_time = time.time()
        self.logger.log_agent_start(self.name)
        
        user_prompt = self.build_prompt(context)
        result = self._call_llm(user_prompt)
        
        self.execution_time = time.time() - start_time
        self.logger.log_agent_complete(self.name, self.execution_time)
        
        return result
    
    def _call_llm(self, user_prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API with retry logic and improved JSON parsing"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Call OpenRouter with OpenAI model
                response = self.client.create_message(
                    model=self.model,
                    messages=[{"role": "user", "content": user_prompt}],
                    system=self.system_prompt,
                    max_tokens=4000,
                    temperature=0.1
                )
                
                # Extract content
                content = self.client.extract_content(response)
                
                # Clean JSON response - handle various markdown formats
                content = content.strip()
                
                # Remove markdown code blocks
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                elif content.startswith("```"):
                    content = content[3:]  # Remove ```
                
                if content.endswith("```"):
                    content = content[:-3]  # Remove trailing ```
                
                content = content.strip()
                
                # Try to extract JSON if wrapped in other text
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    content = content[start_idx:end_idx]
                
                # Parse JSON
                parsed = json.loads(content)
                return parsed
                
            except json.JSONDecodeError as e:
                self.logger.logger.warning(f"JSON decode error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Try to fix common JSON issues
                    try:
                        # Remove trailing commas
                        import re
                        content = re.sub(r',(\s*[}\]])', r'\1', content)
                        parsed = json.loads(content)
                        return parsed
                    except:
                        time.sleep(1)
                        continue
                else:
                    # Last attempt failed, log the content for debugging
                    self.logger.logger.error(f"Failed to parse JSON after {max_retries} attempts. Content preview: {content[:500]}")
                    raise Exception(f"Failed to parse JSON response: {str(e)}")
                    
            except Exception as e:
                self.logger.logger.warning(f"API error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
    
    @abstractmethod
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Build the user prompt for this agent"""
        pass
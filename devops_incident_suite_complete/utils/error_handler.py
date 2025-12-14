from typing import Callable, Any
from functools import wraps
import traceback

class AgentError(Exception):
    """Custom exception for agent errors"""
    pass

def handle_agent_errors(func: Callable) -> Callable:
    """Decorator for error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise AgentError(f"Agent execution failed: {str(e)}")
    return wrapper
import logging
from datetime import datetime

class CustomLogger:
    """Custom logger with structured logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_agent_start(self, agent_name: str):
        self.logger.info(f"🚀 Starting agent: {agent_name}")
    
    def log_agent_complete(self, agent_name: str, duration: float):
        self.logger.info(f"✅ Completed agent: {agent_name} in {duration:.2f}s")
    
    def log_error(self, agent_name: str, error: Exception):
        self.logger.error(f"❌ Error in {agent_name}: {str(error)}")
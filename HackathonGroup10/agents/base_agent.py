"""Base Agent Class for Cybersecurity Multi-Agent System"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from enum import Enum

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentStatus(Enum):
    IDLE = "idle"
    MONITORING = "monitoring"
    ANALYZING = "analyzing"
    RESPONDING = "responding"
    ERROR = "error"

class SecurityAlert:
    def __init__(self, agent_id: str, alert_type: str, severity: AlertSeverity, description: str, details: Dict[str, Any], timestamp: Optional[datetime] = None):
        self.agent_id = agent_id
        self.alert_type = alert_type
        self.severity = severity
        self.description = description
        self.details = details
        self.timestamp = timestamp or datetime.now()
        self.alert_id = f"{agent_id}_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "agent_id": self.agent_id,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "description": self.description,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.alert_type}: {self.description}"

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_name: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{agent_id}")
        self.alerts_generated = []
        self.metrics = {
            "alerts_generated": 0,
            "events_processed": 0,
            "errors": 0,
            "uptime_start": datetime.now()
        }
        self._coordinator = None
    
    def set_coordinator(self, coordinator):
        self._coordinator = coordinator
    
    def send_alert(self, alert: SecurityAlert) -> None:
        self.alerts_generated.append(alert)
        self.metrics["alerts_generated"] += 1
        self.logger.info(f"Alert generated: {alert}")
        if self._coordinator:
            self._coordinator.receive_alert(alert)
    
    def send_message(self, target_agent_id: str, message: Dict[str, Any]) -> None:
        if self._coordinator:
            self._coordinator.route_message(self.agent_id, target_agent_id, message)
    
    def receive_message(self, sender_agent_id: str, message: Dict[str, Any]) -> None:
        self.logger.info(f"Received message from {sender_agent_id}: {message.get('type', 'unknown')}")
        self.handle_message(sender_agent_id, message)
    
    def handle_message(self, sender_agent_id: str, message: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def analyze(self, data: Any) -> List[SecurityAlert]:
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        pass
    
    def start_monitoring(self) -> None:
        self.status = AgentStatus.MONITORING
        self.logger.info(f"{self.agent_name} started monitoring")
    
    def stop_monitoring(self) -> None:
        self.status = AgentStatus.IDLE
        self.logger.info(f"{self.agent_name} stopped monitoring")
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "metrics": self.metrics.copy(),
            "alerts_count": len(self.alerts_generated),
            "capabilities": self.get_capabilities()
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[SecurityAlert]:
        return self.alerts_generated[-limit:]


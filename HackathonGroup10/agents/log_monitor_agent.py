"""Log Monitor Agent - Analyzes system and application logs in real-time"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from .base_agent import BaseAgent, SecurityAlert, AlertSeverity

class LogMonitorAgent(BaseAgent):
    SUSPICIOUS_PATTERNS = {
        "brute_force": [r"Failed password", r"authentication failure", r"invalid login"],
        "sql_injection": [r"union.*select", r"';.*--", r"or\s+1\s*=\s*1"],
        "xss_attempt": [r"<script", r"javascript:", r"onerror\s*="],
        "path_traversal": [r"\.\./", r"\.\.\\", r"/etc/passwd"],
    }
    RATE_LIMITS = {
        "failed_login": {"count": 5, "window": 300},
        "access_denied": {"count": 10, "window": 60}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("log_monitor", "Log Monitor Agent", config)
        self.log_buffer = []
        self.time_windows = defaultdict(list)
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {"monitors": ["system_logs", "application_logs"], "detects": ["brute_force_attacks", "sql_injection", "xss_attempts"]}
    
    def ingest_log(self, log_entry: str, log_source: str = "system", metadata: Optional[Dict] = None) -> None:
        self.metrics["events_processed"] += 1
        timestamp = datetime.now()
        log_data = {"entry": log_entry, "source": log_source, "timestamp": timestamp, "metadata": metadata or {}}
        self.log_buffer.append(log_data)
        if len(self.log_buffer) > 10000:
            self.log_buffer = self.log_buffer[-5000:]
        self._analyze_log_entry(log_data)
    
    def _analyze_log_entry(self, log_data: Dict[str, Any]) -> None:
        log_entry = log_data["entry"].lower()
        alerts = []
        for attack_type, patterns in self.SUSPICIOUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, log_entry, re.IGNORECASE):
                    severity = AlertSeverity.HIGH if attack_type in ["sql_injection"] else AlertSeverity.MEDIUM
                    alert = SecurityAlert(
                        agent_id=self.agent_id,
                        alert_type=f"log_{attack_type}",
                        severity=severity,
                        description=f"Detected {attack_type.replace('_', ' ')} pattern",
                        details={"log_entry": log_data["entry"], "source": log_data["source"], "pattern_matched": pattern}
                    )
                    alerts.append(alert)
                    break
        alerts.extend(self._check_rate_limits(log_entry, log_data["timestamp"]))
        for alert in alerts:
            self.send_alert(alert)
    
    def _check_rate_limits(self, log_entry: str, timestamp: datetime) -> List[SecurityAlert]:
        alerts = []
        if any(keyword in log_entry for keyword in ["failed password", "authentication failure"]):
            event_type = "failed_login"
            self.time_windows[event_type].append(timestamp)
            cutoff = timestamp - timedelta(seconds=self.RATE_LIMITS[event_type]["window"])
            self.time_windows[event_type] = [t for t in self.time_windows[event_type] if t > cutoff]
            if len(self.time_windows[event_type]) >= self.RATE_LIMITS[event_type]["count"]:
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="brute_force_detected",
                    severity=AlertSeverity.HIGH,
                    description=f"Multiple failed login attempts ({len(self.time_windows[event_type])})",
                    details={"event_type": event_type, "count": len(self.time_windows[event_type])}
                )
                alerts.append(alert)
        return alerts
    
    def analyze(self, data: Any) -> List[SecurityAlert]:
        if isinstance(data, str):
            self.ingest_log(data)
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, str):
                    self.ingest_log(entry)
        return self.get_recent_alerts(limit=50)


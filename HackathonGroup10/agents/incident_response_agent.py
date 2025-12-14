"""Incident Response Agent - Coordinates responses to security events"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from .base_agent import BaseAgent, SecurityAlert, AlertSeverity

class IncidentStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"

class Incident:
    def __init__(self, incident_id: str, alert: SecurityAlert, severity: AlertSeverity, status: IncidentStatus = IncidentStatus.DETECTED):
        self.incident_id = incident_id
        self.alert = alert
        self.severity = severity
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.actions_taken = []
        self.related_alerts = [alert]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "status": self.status.value,
            "severity": self.severity.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "actions_taken": self.actions_taken
        }

class IncidentResponseAgent(BaseAgent):
    RESPONSE_PLAYBOOKS = {
        "brute_force_detected": {"steps": ["Block source IP", "Notify security team"], "priority": "high"},
        "malware_detected": {"steps": ["Isolate affected system", "Collect malware sample"], "priority": "critical"}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("incident_response", "Incident Response Agent", config)
        self.active_incidents = {}
        self.resolved_incidents = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {"response_actions": ["incident_triage", "containment", "eradication"], "playbooks": list(self.RESPONSE_PLAYBOOKS.keys())}
    
    def create_incident(self, alert: SecurityAlert) -> Incident:
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.active_incidents) + 1}"
        incident = Incident(incident_id, alert, alert.severity, IncidentStatus.DETECTED)
        incident.response_plan = self.RESPONSE_PLAYBOOKS.get(alert.alert_type, {"steps": ["Assess threat", "Contain threat"], "priority": alert.severity.value})
        self.active_incidents[incident_id] = incident
        self.logger.info(f"Created incident {incident_id}")
        self._initiate_response(incident)
        return incident
    
    def _initiate_response(self, incident: Incident) -> None:
        incident.status = IncidentStatus.INVESTIGATING
        action = {"timestamp": datetime.now(), "action": "response_initiated", "details": f"Started response for {incident.alert.alert_type}"}
        incident.actions_taken.append(action)
    
    def correlate_alerts(self, alerts: List[SecurityAlert]) -> List[Incident]:
        incidents = []
        if len(alerts) > 1:
            primary_alert = max(alerts, key=lambda a: a.severity.value)
            incident = self.create_incident(primary_alert)
            incident.related_alerts = alerts
            incidents.append(incident)
        elif alerts and alerts[0].severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            incident = self.create_incident(alerts[0])
            incidents.append(incident)
        return incidents
    
    def analyze(self, data: Any) -> List[SecurityAlert]:
        if isinstance(data, SecurityAlert):
            self.create_incident(data)
            return []
        elif isinstance(data, list):
            self.correlate_alerts(data)
            return []
        return []


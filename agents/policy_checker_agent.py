"""Policy Checker Agent - Ensures compliance with security policies"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent, SecurityAlert, AlertSeverity

class PolicyCheckerAgent(BaseAgent):
    SECURITY_POLICIES = {
        "password_policy": {"min_length": 12, "max_age_days": 90},
        "access_control_policy": {"require_mfa": True, "session_timeout_minutes": 30},
        "encryption_policy": {"require_encryption_at_rest": True, "require_encryption_in_transit": True}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("policy_checker", "Policy Checker Agent", config)
        self.policy_violations = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {"policies": list(self.SECURITY_POLICIES.keys()), "check_types": ["password_compliance", "access_control_compliance", "encryption_compliance"]}
    
    def check_policy_compliance(self, policy_name: str, current_state: Dict[str, Any]) -> List[SecurityAlert]:
        if policy_name not in self.SECURITY_POLICIES:
            return []
        policy = self.SECURITY_POLICIES[policy_name]
        alerts = []
        if policy_name == "password_policy":
            if "password_length" in current_state and current_state["password_length"] < policy["min_length"]:
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="password_policy_violation",
                    severity=AlertSeverity.MEDIUM,
                    description=f"Password length {current_state['password_length']} is below minimum {policy['min_length']}",
                    details={"policy": "password_policy", "violation": "min_length"}
                )
                alerts.append(alert)
        elif policy_name == "access_control_policy":
            if policy["require_mfa"] and not current_state.get("mfa_enabled", False):
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="access_control_policy_violation",
                    severity=AlertSeverity.HIGH,
                    description="MFA is required but not enabled",
                    details={"policy": "access_control_policy", "violation": "mfa_required"}
                )
                alerts.append(alert)
        elif policy_name == "encryption_policy":
            if policy["require_encryption_at_rest"] and not current_state.get("encryption_at_rest", False):
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="encryption_policy_violation",
                    severity=AlertSeverity.HIGH,
                    description="Encryption at rest is required but not enabled",
                    details={"policy": "encryption_policy", "violation": "encryption_at_rest"}
                )
                alerts.append(alert)
        for alert in alerts:
            self.send_alert(alert)
        return alerts
    
    def analyze(self, data: Any) -> List[SecurityAlert]:
        if isinstance(data, dict):
            policy_name = data.get("policy")
            current_state = data.get("state", {})
            if policy_name:
                return self.check_policy_compliance(policy_name, current_state)
        return []


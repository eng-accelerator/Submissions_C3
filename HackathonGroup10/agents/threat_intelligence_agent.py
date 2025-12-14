"""Threat Intelligence Agent - Correlates threats with known attack patterns"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from .base_agent import BaseAgent, SecurityAlert, AlertSeverity

class ThreatIntelligenceAgent(BaseAgent):
    THREAT_PATTERNS = {
        "apt_group_1": {"indicators": ["specific_hash_1", "domain_xyz.com"], "tactics": ["initial_access"], "severity": "high"},
        "ransomware_group_a": {"indicators": ["file_extension_xyz"], "tactics": ["encryption"], "severity": "critical"}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("threat_intel", "Threat Intelligence Agent", config)
        self.suspicious_ips = set()
        self.suspicious_domains = set()
        self._load_threat_database()
    
    def _load_threat_database(self) -> None:
        for threat_id, threat_data in self.THREAT_PATTERNS.items():
            for indicator in threat_data.get("indicators", []):
                if "ip" in indicator.lower():
                    self.suspicious_ips.add(indicator)
                elif "domain" in indicator.lower() or "." in indicator:
                    self.suspicious_domains.add(indicator)
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {"correlates": ["ip_addresses", "domains", "file_hashes"], "threat_sources": ["mitre_attck", "known_apt_groups"]}
    
    def correlate_threat(self, indicators: Dict[str, Any], context: Optional[Dict] = None) -> List[SecurityAlert]:
        alerts = []
        if "ip_address" in indicators:
            ip = indicators["ip_address"]
            # Check if IP is in known threat database
            if ip in self.suspicious_ips:
                severity = AlertSeverity.HIGH
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="suspicious_ip",
                    severity=severity,
                    description=f"Threat intelligence match: known malicious IP {ip}",
                    details={"indicator": ip, "context": context or {}, "source": "threat_database"}
                )
                alerts.append(alert)
            # Check for suspicious IP ranges (private IPs in suspicious ranges)
            elif any(ip.startswith(prefix) for prefix in ["192.168.100", "10.0.0.1"]):
                severity = AlertSeverity.HIGH
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="suspicious_ip",
                    severity=severity,
                    description=f"Threat intelligence match: suspicious IP range detected - {ip}",
                    details={"indicator": ip, "context": context or {}, "source": "ip_range_analysis"}
                )
                alerts.append(alert)
            # Check context for threat indicators
            elif context and context.get("threat_score", 0) > 70:
                severity = AlertSeverity.HIGH if context.get("threat_score", 0) > 80 else AlertSeverity.MEDIUM
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="suspicious_ip",
                    severity=severity,
                    description=f"High threat score IP detected: {ip} (score: {context.get('threat_score')})",
                    details={"indicator": ip, "context": context, "source": "threat_scoring"}
                )
                alerts.append(alert)
            # Check if IP was blocked
            elif context and context.get("blocked") == True:
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="blocked_ip",
                    severity=AlertSeverity.MEDIUM,
                    description=f"Blocked IP address detected: {ip}",
                    details={"indicator": ip, "context": context, "source": "firewall"}
                )
                alerts.append(alert)
        if "domain" in indicators:
            domain = indicators["domain"]
            if domain in self.suspicious_domains:
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="suspicious_domain",
                    severity=AlertSeverity.MEDIUM,
                    description=f"Threat intelligence match: suspicious domain {domain}",
                    details={"indicator": domain, "context": context or {}}
                )
                alerts.append(alert)
            # Check for suspicious domain patterns
            elif any(pattern in domain.lower() for pattern in ["malicious", "phishing", "malware", "botnet"]):
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="suspicious_domain",
                    severity=AlertSeverity.MEDIUM,
                    description=f"Suspicious domain pattern detected: {domain}",
                    details={"indicator": domain, "context": context or {}, "source": "pattern_analysis"}
                )
                alerts.append(alert)
        for alert in alerts:
            self.send_alert(alert)
        return alerts
    
    def analyze(self, data: Any) -> List[SecurityAlert]:
        if isinstance(data, dict):
            return self.correlate_threat(data, data.get("context"))
        elif isinstance(data, list):
            alerts = []
            for item in data:
                if isinstance(item, dict):
                    alerts.extend(self.correlate_threat(item))
            return alerts
        return []


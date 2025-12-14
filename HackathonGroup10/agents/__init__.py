"""
Cybersecurity Multi-Agent System - Agents Package
"""

from .base_agent import BaseAgent, SecurityAlert, AlertSeverity, AgentStatus
from .log_monitor_agent import LogMonitorAgent
from .threat_intelligence_agent import ThreatIntelligenceAgent
from .vulnerability_scanner_agent import VulnerabilityScannerAgent
from .incident_response_agent import IncidentResponseAgent, Incident, IncidentStatus
from .policy_checker_agent import PolicyCheckerAgent
from .external_api_agent import ExternalAPIAgent

# Optional CVE RAG Agent
try:
    from .cve_rag_agent import CVERAGAgent
    CVE_RAG_AVAILABLE = True
except ImportError:
    CVE_RAG_AVAILABLE = False
    CVERAGAgent = None

__all__ = [
    "BaseAgent",
    "SecurityAlert",
    "AlertSeverity",
    "AgentStatus",
    "LogMonitorAgent",
    "ThreatIntelligenceAgent",
    "VulnerabilityScannerAgent",
    "IncidentResponseAgent",
    "Incident",
    "IncidentStatus",
    "PolicyCheckerAgent",
    "ExternalAPIAgent",
]

if CVE_RAG_AVAILABLE:
    __all__.append("CVERAGAgent")


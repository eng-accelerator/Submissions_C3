"""Cybersecurity Multi-Agent System Coordinator using LangGraph"""
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
import logging
from collections import defaultdict, deque

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available. Install with: pip install langgraph")

from agents import (
    BaseAgent, SecurityAlert, LogMonitorAgent, ThreatIntelligenceAgent,
    VulnerabilityScannerAgent, IncidentResponseAgent, PolicyCheckerAgent, AlertSeverity
)

class SecuritySystemState(TypedDict):
    log_entries: Annotated[List[str], lambda x, y: x + y]
    system_info: Optional[Dict[str, Any]]
    indicators: Annotated[List[Dict[str, Any]], lambda x, y: x + y]
    log_alerts: Annotated[List[Dict[str, Any]], lambda x, y: x + y]
    threat_alerts: Annotated[List[Dict[str, Any]], lambda x, y: x + y]
    vulnerability_alerts: Annotated[List[Dict[str, Any]], lambda x, y: x + y]
    policy_alerts: Annotated[List[Dict[str, Any]], lambda x, y: x + y]
    incidents: Annotated[List[Dict[str, Any]], lambda x, y: x + y]
    active_incidents: Dict[str, Dict[str, Any]]
    current_step: str
    workflow_complete: bool
    errors: Annotated[List[str], lambda x, y: x + y]
    timestamp: str
    correlation_results: Dict[str, Any]

def add_alerts(x: List[Dict[str, Any]], y: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper function to add alerts lists"""
    return x + y

class LangGraphCoordinator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        self.config = config or {}
        self.logger = logging.getLogger("LangGraphCoordinator")
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
        self.graph = self._build_graph()
        self.metrics = {
            "total_alerts": 0,
            "alerts_by_severity": defaultdict(int),
            "alerts_by_agent": defaultdict(int),
            "workflows_executed": 0,
            "system_start_time": datetime.now()
        }
    
    def _initialize_agents(self) -> None:
        agent_configs = self.config.get("agents", {})
        self.agents["log_monitor"] = LogMonitorAgent(agent_configs.get("log_monitor", {}))
        self.agents["threat_intel"] = ThreatIntelligenceAgent(agent_configs.get("threat_intel", {}))
        self.agents["vulnerability_scanner"] = VulnerabilityScannerAgent(agent_configs.get("vulnerability_scanner", {}))
        self.agents["incident_response"] = IncidentResponseAgent(agent_configs.get("incident_response", {}))
        self.agents["policy_checker"] = PolicyCheckerAgent(agent_configs.get("policy_checker", {}))
        for agent in self.agents.values():
            agent.set_coordinator(self)
        self.message_queue: deque = deque(maxlen=1000)
        self.logger.info(f"Initialized {len(self.agents)} agents")
    
    def receive_alert(self, alert: SecurityAlert) -> None:
        self.metrics["total_alerts"] += 1
        self.metrics["alerts_by_severity"][alert.severity.value] += 1
        self.metrics["alerts_by_agent"][alert.agent_id] += 1
    
    def route_message(self, sender_id: str, target_id: str, message: Dict[str, Any]) -> None:
        if target_id not in self.agents:
            return
        self.agents[target_id].receive_message(sender_id, message)
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(SecuritySystemState)
        workflow.add_node("log_monitor", self._log_monitor_node)
        workflow.add_node("threat_intel", self._threat_intel_node)
        workflow.add_node("vulnerability_scanner", self._vulnerability_scanner_node)
        workflow.add_node("policy_checker", self._policy_checker_node)
        workflow.add_node("incident_response", self._incident_response_node)
        workflow.add_node("correlate_results", self._correlate_results_node)
        workflow.set_entry_point("log_monitor")
        workflow.add_conditional_edges("log_monitor", self._route_after_log_monitor, {
            "threat_intel": "threat_intel", "incident_response": "incident_response",
            "vulnerability_scanner": "vulnerability_scanner", "continue": "correlate_results"
        })
        workflow.add_conditional_edges("threat_intel", self._route_after_threat_intel, {
            "vulnerability_scanner": "vulnerability_scanner",
            "incident_response": "incident_response", 
            "continue": "correlate_results"
        })
        workflow.add_conditional_edges("vulnerability_scanner", self._route_after_vulnerability_scanner, {
            "policy_checker": "policy_checker", "incident_response": "incident_response", "continue": "correlate_results"
        })
        workflow.add_conditional_edges("policy_checker", self._route_after_policy_checker, {
            "incident_response": "incident_response", "continue": "correlate_results"
        })
        workflow.add_edge("incident_response", "correlate_results")
        workflow.add_edge("correlate_results", END)
        return workflow.compile(checkpointer=MemorySaver())
    
    def _log_monitor_node(self, state: SecuritySystemState) -> SecuritySystemState:
        self.logger.info("Processing logs through Log Monitor Agent")
        log_monitor = self.agents["log_monitor"]
        alerts = []
        for log_entry in state.get("log_entries", []):
            log_monitor.ingest_log(log_entry, log_source="system")
            recent_alerts = log_monitor.get_recent_alerts(limit=10)
            alerts.extend([a.to_dict() for a in recent_alerts])
        state["log_alerts"] = alerts
        state["current_step"] = "log_monitor"
        state["timestamp"] = datetime.now().isoformat()
        for alert_dict in alerts:
            self.metrics["total_alerts"] += 1
            self.metrics["alerts_by_severity"][alert_dict.get("severity", "medium")] += 1
            self.metrics["alerts_by_agent"]["log_monitor"] += 1
        return state
    
    def _threat_intel_node(self, state: SecuritySystemState) -> SecuritySystemState:
        self.logger.info("Processing indicators through Threat Intelligence Agent")
        self.logger.info(f"Indicators in state: {len(state.get('indicators', []))}")
        threat_intel = self.agents["threat_intel"]
        alerts = []
        # Process indicators from input
        processed_indicators = set()
        indicators = state.get("indicators", [])
        self.logger.info(f"Processing {len(indicators)} indicators")
        for indicator in indicators:
            # Create a unique key for this indicator
            indicator_key = f"{indicator.get('ip_address', '')}_{indicator.get('domain', '')}"
            if indicator_key not in processed_indicators:
                processed_indicators.add(indicator_key)
                indicator_alerts = threat_intel.correlate_threat(indicator, indicator.get("context"))
                self.logger.info(f"Generated {len(indicator_alerts)} alerts for indicator {indicator_key}")
                alerts.extend([a.to_dict() for a in indicator_alerts])
        # Also check log alerts for IP addresses (but avoid duplicates)
        processed_ips = set()
        for alert_dict in state.get("log_alerts", []):
            ip = alert_dict.get("details", {}).get("ip_address")
            if ip and ip not in processed_ips:
                processed_ips.add(ip)
                indicator_alerts = threat_intel.correlate_threat(
                    {"ip_address": ip}, {"source": "log_monitor"}
                )
                alerts.extend([a.to_dict() for a in indicator_alerts])
        self.logger.info(f"Total threat alerts generated: {len(alerts)}")
        state["threat_alerts"] = alerts
        state["current_step"] = "threat_intel"
        for alert_dict in alerts:
            self.metrics["total_alerts"] += 1
            self.metrics["alerts_by_severity"][alert_dict.get("severity", "medium")] += 1
            self.metrics["alerts_by_agent"]["threat_intel"] += 1
        return state
    
    def _vulnerability_scanner_node(self, state: SecuritySystemState) -> SecuritySystemState:
        self.logger.info("Scanning system through Vulnerability Scanner Agent")
        system_info = state.get("system_info")
        self.logger.info(f"System info present: {system_info is not None}")
        if system_info:
            self.logger.info(f"System info keys: {list(system_info.keys())}")
        vuln_scanner = self.agents["vulnerability_scanner"]
        alerts = []
        if system_info:
            system_alerts = vuln_scanner.scan_system(system_info)
            self.logger.info(f"Generated {len(system_alerts)} vulnerability alerts")
            alerts.extend([a.to_dict() for a in system_alerts])
        else:
            self.logger.warning("No system_info in state for vulnerability scanner")
        self.logger.info(f"Total vulnerability alerts: {len(alerts)}")
        state["vulnerability_alerts"] = alerts
        state["current_step"] = "vulnerability_scanner"
        for alert_dict in alerts:
            self.metrics["total_alerts"] += 1
            self.metrics["alerts_by_severity"][alert_dict.get("severity", "medium")] += 1
            self.metrics["alerts_by_agent"]["vulnerability_scanner"] += 1
        return state
    
    def _policy_checker_node(self, state: SecuritySystemState) -> SecuritySystemState:
        self.logger.info("Checking policies through Policy Checker Agent")
        policy_checker = self.agents["policy_checker"]
        alerts = []
        if state.get("system_info"):
            for policy_name in policy_checker.SECURITY_POLICIES.keys():
                if policy_name in state["system_info"]:
                    policy_alerts = policy_checker.check_policy_compliance(policy_name, state["system_info"][policy_name])
                    alerts.extend([a.to_dict() for a in policy_alerts])
        state["policy_alerts"] = alerts
        state["current_step"] = "policy_checker"
        for alert_dict in alerts:
            self.metrics["total_alerts"] += 1
            self.metrics["alerts_by_severity"][alert_dict.get("severity", "medium")] += 1
            self.metrics["alerts_by_agent"]["policy_checker"] += 1
        return state
    
    def _incident_response_node(self, state: SecuritySystemState) -> SecuritySystemState:
        self.logger.info("Processing incidents through Incident Response Agent")
        incident_response = self.agents["incident_response"]
        all_alerts_dict = []
        all_alerts_dict.extend(state.get("log_alerts", []))
        all_alerts_dict.extend(state.get("threat_alerts", []))
        all_alerts_dict.extend(state.get("vulnerability_alerts", []))
        all_alerts_dict.extend(state.get("policy_alerts", []))
        # Convert dict alerts back to SecurityAlert objects for incident response
        from agents import SecurityAlert, AlertSeverity
        all_alerts = []
        for alert_dict in all_alerts_dict:
            alert = SecurityAlert(
                agent_id=alert_dict.get("agent_id", "unknown"),
                alert_type=alert_dict.get("alert_type", "unknown"),
                severity=AlertSeverity[alert_dict.get("severity", "medium").upper()],
                description=alert_dict.get("description", ""),
                details=alert_dict.get("details", {})
            )
            all_alerts.append(alert)
        incidents = []
        for alert in all_alerts:
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                incident = incident_response.create_incident(alert)
                incidents.append(incident.to_dict())
        if len(all_alerts) > 1:
            correlated_incidents = incident_response.correlate_alerts(all_alerts)
            for incident in correlated_incidents:
                incidents.append(incident.to_dict())
        state["incidents"] = incidents
        state["current_step"] = "incident_response"
        return state
    
    def _correlate_results_node(self, state: SecuritySystemState) -> SecuritySystemState:
        self.logger.info("Correlating results from all agents")
        correlation = {
            "total_alerts": (
                len(state.get("log_alerts", [])) + len(state.get("threat_alerts", [])) +
                len(state.get("vulnerability_alerts", [])) + len(state.get("policy_alerts", []))
            ),
            "alerts_by_type": {
                "log": len(state.get("log_alerts", [])),
                "threat": len(state.get("threat_alerts", [])),
                "vulnerability": len(state.get("vulnerability_alerts", [])),
                "policy": len(state.get("policy_alerts", []))
            },
            "incidents_created": len(state.get("incidents", [])),
            "timestamp": datetime.now().isoformat()
        }
        state["correlation_results"] = correlation
        state["current_step"] = "correlate_results"
        state["workflow_complete"] = True
        return state
    
    def _route_after_log_monitor(self, state: SecuritySystemState) -> str:
        # Always route to threat_intel if indicators are provided
        if state.get("indicators"):
            return "threat_intel"
        # Route to vulnerability scanner if system_info is provided
        if state.get("system_info"):
            return "vulnerability_scanner"
        # Check for high severity alerts from logs
        alerts = state.get("log_alerts", [])
        if any(a.get("severity") in ["high", "critical"] for a in alerts):
            return "incident_response"
        # Check for IP addresses in log alerts
        if any("ip_address" in a.get("details", {}) for a in alerts):
            return "threat_intel"
        return "continue"
    
    def _route_after_threat_intel(self, state: SecuritySystemState) -> str:
        # Always route to vulnerability scanner if system_info is provided
        if state.get("system_info"):
            return "vulnerability_scanner"
        # Check for high severity alerts
        alerts = state.get("threat_alerts", [])
        if alerts and any(a.get("severity") in ["high", "critical"] for a in alerts):
            return "incident_response"
        return "continue"
    
    def _route_after_vulnerability_scanner(self, state: SecuritySystemState) -> str:
        alerts = state.get("vulnerability_alerts", [])
        if alerts:
            return "policy_checker"
        if any(a.get("severity") == "critical" for a in alerts):
            return "incident_response"
        return "continue"
    
    def _route_after_policy_checker(self, state: SecuritySystemState) -> str:
        alerts = state.get("policy_alerts", [])
        if alerts and any(a.get("severity") in ["high", "critical"] for a in alerts):
            return "incident_response"
        return "continue"
    
    def process_security_event(self, log_entries: Optional[List[str]] = None, system_info: Optional[Dict[str, Any]] = None,
                              indicators: Optional[List[Dict[str, Any]]] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        initial_state: SecuritySystemState = {
            "log_entries": log_entries or [],
            "system_info": system_info,
            "indicators": indicators or [],
            "log_alerts": [],
            "threat_alerts": [],
            "vulnerability_alerts": [],
            "policy_alerts": [],
            "incidents": [],
            "active_incidents": {},
            "current_step": "start",
            "workflow_complete": False,
            "errors": [],
            "timestamp": datetime.now().isoformat(),
            "correlation_results": {}
        }
        config = config or {}
        # Add thread_id for checkpointer
        if "configurable" not in config:
            config["configurable"] = {}
        if "thread_id" not in config["configurable"]:
            config["configurable"]["thread_id"] = f"security_event_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        final_state = self.graph.invoke(initial_state, config)
        self.metrics["workflows_executed"] += 1
        return final_state
    
    def get_system_status(self) -> Dict[str, Any]:
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()
        return {
            "system_uptime_seconds": (datetime.now() - self.metrics["system_start_time"]).total_seconds(),
            "total_alerts": self.metrics["total_alerts"],
            "alerts_by_severity": dict(self.metrics["alerts_by_severity"]),
            "alerts_by_agent": dict(self.metrics["alerts_by_agent"]),
            "workflows_executed": self.metrics["workflows_executed"],
            "agents": agent_statuses,
            "framework": "LangGraph"
        }
    
    def start_monitoring(self) -> None:
        for agent_id, agent in self.agents.items():
            try:
                agent.start_monitoring()
                self.logger.info(f"Started monitoring for {agent_id}")
            except Exception as e:
                self.logger.error(f"Failed to start {agent_id}: {e}")
    
    def stop_monitoring(self) -> None:
        for agent_id, agent in self.agents.items():
            try:
                agent.stop_monitoring()
                self.logger.info(f"Stopped monitoring for {agent_id}")
            except Exception as e:
                self.logger.error(f"Failed to stop {agent_id}: {e}")


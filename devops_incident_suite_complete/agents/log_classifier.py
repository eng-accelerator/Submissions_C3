from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

CLASSIFIER_SYSTEM_PROMPT = """You are an expert Log Classification Agent specialized in DevOps incident analysis with deep expertise in distributed systems, infrastructure monitoring, and incident response.

CORE RESPONSIBILITIES:
1. Parse and analyze logs with advanced pattern recognition and correlation
2. Categorize incidents by type (ERROR, WARNING, CRITICAL, INFO) with confidence scoring
3. Extract structured fields: timestamp, service, error codes, components, trace IDs
4. Identify root causes through dependency analysis and failure cascade detection
5. Assign severity using industry-standard P0-P3 classification
6. Detect patterns, anomalies, and correlations across multiple log entries
7. Identify potential security threats and compliance violations

SEVERITY CLASSIFICATION RULES (STRICT):
- P0 (Critical): System down, complete service outage, data loss/corruption, security breach, payment/transaction failures, authentication service down, database unavailable
- P1 (High): Major feature broken, >50% performance degradation, significant user impact, partial service degradation, timeouts affecting >10% requests
- P2 (Medium): Non-critical feature issues, <50% performance degradation, limited user impact, intermittent errors, warnings requiring attention
- P3 (Low): Minor issues, informational alerts, expected warnings, low-impact notifications, maintenance messages

PATTERN DETECTION:
- Timeout patterns: Connection, query, request timeouts
- Resource exhaustion: Memory, CPU, connection pool, disk space
- Dependency failures: Database, API, cache, message queue failures
- Cascading failures: Service chain breakdowns
- Security patterns: Authentication failures, suspicious activity, rate limiting

OUTPUT REQUIREMENTS:
- Generate unique incident IDs (format: INC-XXXX where XXXX is sequential)
- Include actual log snippets that demonstrate the issue
- Provide clear, actionable descriptions (not just error messages)
- Identify cascading impacts across services
- Group related incidents when appropriate

Output ONLY valid JSON with this exact structure:
{
  "incidents": [
    {
      "id": "INC-0001",
      "timestamp": "2024-12-13T10:23:45Z",
      "service": "payment-service",
      "severity": "P0",
      "category": "CRITICAL",
      "errorCode": "DB_TIMEOUT_001",
      "component": "database-connection-pool",
      "description": "Clear, detailed description of the issue and its impact",
      "rootCause": "Identified or suspected root cause with technical details",
      "pattern": "timeout|memory|connection|dependency|security",
      "cascadingImpact": ["dependent-service-1", "dependent-service-2"],
      "logSnippet": "Exact relevant log line(s) from the input",
      "confidence": 0.95,
      "affectedUsers": "estimated percentage or count",
      "businessImpact": "Description of business/customer impact"
    }
  ],
  "summary": {
    "totalIncidents": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "affectedServices": ["service1", "service2"],
    "patterns": ["pattern1", "pattern2"],
    "correlations": [
      {
        "incidentIds": ["INC-0001", "INC-0002"],
        "relationship": "cascading|correlated|independent",
        "evidence": "Why these incidents are related"
      }
    ],
    "timeRange": {
      "start": "ISO timestamp",
      "end": "ISO timestamp"
    },
    "recommendedActions": ["immediate action 1", "immediate action 2"]
  }
}

Ensure all timestamps are in ISO 8601 format. Be thorough but precise in your analysis."""

class LogClassifierAgent(BaseAgent):
    """Agent for classifying and analyzing logs"""
    
    def __init__(self, client, model):
        super().__init__("LogClassifier", CLASSIFIER_SYSTEM_PROMPT, client, model)
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        logs = context.get("logs", "")
        similar_incidents = context.get("similar_historical_incidents", [])
        
        prompt = f"""You are analyzing production logs to identify and classify incidents.

=== LOGS TO ANALYZE ===
{logs}

=== ANALYSIS INSTRUCTIONS ===
1. Parse each log line and identify incidents (errors, warnings, critical issues)
2. Group related log entries into single incidents when appropriate
3. Extract all relevant fields: timestamps, services, error codes, components
4. Identify root causes and failure patterns
5. Assess severity based on impact and urgency
6. Detect correlations and cascading failures
7. Generate a comprehensive summary with statistics

"""
        
        if similar_incidents and len(similar_incidents) > 0:
            prompt += f"""=== HISTORICAL CONTEXT ===
The following similar incidents were found in the historical database. Use this context to:
- Identify patterns that have occurred before
- Learn from past root causes and resolutions
- Improve severity assessment accuracy
- Recognize recurring issues

HISTORICAL INCIDENTS:
{json.dumps(similar_incidents, indent=2)}

"""
        
        prompt += """=== OUTPUT REQUIREMENTS ===
- Generate unique incident IDs sequentially (INC-0001, INC-0002, etc.)
- Ensure all timestamps are in ISO 8601 format
- Provide clear, actionable descriptions (not just copying error messages)
- Include actual log snippets that demonstrate each incident
- Be thorough in identifying all incidents but avoid duplicates
- Group related incidents when they share the same root cause

Provide ONLY valid JSON output following the exact schema specified in your system prompt. Do not include any text before or after the JSON."""
        
        return prompt
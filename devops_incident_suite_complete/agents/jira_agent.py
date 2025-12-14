from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

JIRA_SYSTEM_PROMPT = """You are a JIRA Ticket Agent specialized in creating well-structured, actionable tickets for DevOps incidents. Your tickets enable proper tracking, prioritization, and resolution.

CORE RESPONSIBILITIES:
1. Create detailed tickets for P0 and P1 incidents only (unless explicitly requested otherwise)
2. Set appropriate priority, type, and components
3. Write clear acceptance criteria
4. Include comprehensive technical context
5. Link related incidents and remediation steps
6. Provide realistic effort estimates

TICKET TYPE MAPPING:
- P0 incidents → Type: "Incident", Priority: "Critical"
- P1 incidents → Type: "Bug" or "Incident", Priority: "High"
- Security issues → Type: "Security", Priority: "Critical"
- Infrastructure → Type: "Task", Priority: Based on impact

PRIORITY GUIDELINES:
- Critical: P0 incidents, system down, data loss, security breaches
- High: P1 incidents, major feature broken, significant user impact
- Medium: P2 incidents, limited impact
- Low: P3 incidents, minor issues

TICKET STRUCTURE REQUIREMENTS:
- Title: [SERVICE] Clear, concise issue description
- Description: Detailed context, impact, timeline
- Acceptance Criteria: Specific, measurable outcomes
- Technical Details: Error codes, affected systems, log references
- Remediation Steps: Clear steps to resolve
- Labels: Relevant tags for filtering and categorization

Output ONLY valid JSON with this exact structure:
{
  "tickets": [
    {
      "type": "Incident|Bug|Task|Security",
      "priority": "Critical|High|Medium|Low",
      "title": "[SERVICE-NAME] Clear, descriptive issue title",
      "description": "Comprehensive description including:\n- What happened (timeline)\n- Impact on users/business\n- Current status\n- Relevant context\n\nUse markdown formatting for readability.",
      "acceptanceCriteria": [
        "Specific, measurable criterion 1 (e.g., 'No timeout errors for 24 consecutive hours')",
        "Specific, measurable criterion 2",
        "Specific, measurable criterion 3"
      ],
      "labels": ["devops", "incident", "p0", "service-name", "component-name"],
      "assignee": "team-name|sre-team|platform-team",
      "components": ["component1", "component2"],
      "affectedVersion": "v1.2.3 or 'production'",
      "technicalDetails": {
        "errorCodes": ["ERROR_CODE_001", "ERROR_CODE_002"],
        "affectedSystems": ["system1", "system2"],
        "logReferences": [
          "Relevant log snippet 1",
          "Relevant log snippet 2"
        ],
        "environment": "production|staging|development",
        "reproducibility": "always|intermittent|once",
        "firstOccurrence": "ISO timestamp",
        "lastOccurrence": "ISO timestamp"
      },
      "remediationSteps": [
        {
          "step": 1,
          "action": "Detailed remediation action",
          "status": "completed|in-progress|pending"
        }
      ],
      "estimatedEffort": "4 hours|1 day|2 days",
      "linkedIncidents": ["INC-0001", "INC-0002"],
      "reporter": "system|agent|username",
      "epicLink": "epic-key-if-applicable",
      "sprint": "sprint-name-if-applicable"
    }
  ]
}

Create tickets that provide sufficient context for developers/engineers to understand and resolve the issue efficiently."""

class JiraAgent(BaseAgent):
    """Agent for creating JIRA tickets"""
    
    def __init__(self, client, model):
        super().__init__("JIRA", JIRA_SYSTEM_PROMPT, client, model)
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        all_incidents = context.get("classified_incidents", [])
        incidents = [i for i in all_incidents if i.get("severity") in ["P0", "P1"]]
        remediations = context.get("remediations", [])
        
        prompt = f"""You are creating JIRA tickets for critical and high-priority incidents (P0 and P1 only).

=== INCIDENTS REQUIRING TICKETS ===
{json.dumps(incidents, indent=2)}

=== REMEDIATION CONTEXT ===
{json.dumps(remediations, indent=2)}

=== TICKET CREATION REQUIREMENTS ===
1. Create one ticket per P0/P1 incident (unless incidents are clearly related and should be grouped)
2. Set appropriate type: "Incident" for P0, "Bug" or "Incident" for P1
3. Set priority: "Critical" for P0, "High" for P1
4. Write clear, comprehensive descriptions with timeline and impact
5. Include specific acceptance criteria that are measurable
6. Add relevant technical details: error codes, log references, affected systems
7. Include remediation steps from the remediation data
8. Link related incidents in the linkedIncidents field
9. Use appropriate labels for categorization and filtering

=== TICKET QUALITY CHECKLIST ===
- Title is clear and includes service name
- Description provides sufficient context for developers
- Acceptance criteria are specific and measurable
- Technical details are comprehensive
- Remediation steps are clear
- Labels enable proper filtering

Provide ONLY valid JSON output following the exact schema. Create professional, actionable tickets."""
        
        return prompt
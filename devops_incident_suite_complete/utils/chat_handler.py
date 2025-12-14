from typing import List, Dict
from utils.openrouter_client import OpenRouterClient
import json

class ChatHandler:
    """Multi-turn chat handler using OpenAI models"""
    
    def __init__(self, client: OpenRouterClient, model: str):
        self.client = client
        self.model = model
        self.system_prompt = """You are an expert DevOps Incident Analysis Assistant with deep knowledge of:
- Distributed systems and microservices architecture
- Common failure patterns and root cause analysis
- Incident response best practices and SRE principles
- Monitoring, alerting, and observability
- Cloud infrastructure and container orchestration

Your role is to:
- Answer questions about analyzed incidents with accuracy and context
- Provide actionable insights based on incident data
- Explain technical concepts clearly
- Suggest best practices and improvements
- Help users understand remediation steps and their rationale

Be concise, helpful, and action-oriented. Always ground your responses in the provided incident context."""
    
    def handle_query(self, query: str, incident_context: Dict, chat_history: List[Dict]) -> str:
        """Handle user query with full context"""
        
        # Build comprehensive context message
        summary = incident_context.get('incident_summary', {})
        incidents = incident_context.get('classified_incidents', [])
        remediations = incident_context.get('remediations', [])
        notifications = incident_context.get('notifications', [])
        
        # Enhanced system prompt with explicit instructions
        enhanced_system_prompt = f"""{self.system_prompt}

IMPORTANT: You have access to real incident data that has been analyzed. Use this data to answer questions accurately.

Current incident analysis contains:
- {summary.get('totalIncidents', 0)} total incidents
- {summary.get('critical', 0)} critical (P0), {summary.get('high', 0)} high (P1), {summary.get('medium', 0)} medium (P2), {summary.get('low', 0)} low (P3)
- Affected services: {', '.join(summary.get('affectedServices', ['None']))}
- Detected patterns: {', '.join(summary.get('patterns', ['None']))}

When answering questions:
1. Reference specific incident IDs (e.g., INC-0001, INC-0002)
2. Use actual data from the incidents provided in the context
3. Provide specific details about services, error codes, root causes mentioned in the analysis
4. Reference remediation steps if they exist
5. Be concrete and data-driven, not generic

If asked about a specific incident ID, find it in the provided context and answer based on that incident's details."""
        
        context_msg = f"""=== CURRENT INCIDENT ANALYSIS DATA ===

SUMMARY:
- Total Incidents: {summary.get('totalIncidents', 0)}
- Critical (P0): {summary.get('critical', 0)}
- High (P1): {summary.get('high', 0)}
- Medium (P2): {summary.get('medium', 0)}
- Low (P3): {summary.get('low', 0)}
- Affected Services: {', '.join(summary.get('affectedServices', [])) if summary.get('affectedServices') else 'None'}
- Detected Patterns: {', '.join(summary.get('patterns', [])) if summary.get('patterns') else 'None'}

ALL CLASSIFIED INCIDENTS:
{json.dumps(incidents, indent=2) if incidents else 'No incidents found'}

REMEDIATION PLANS:
{json.dumps(remediations, indent=2) if remediations else 'No remediations available'}

SLACK NOTIFICATIONS:
{json.dumps(notifications, indent=2) if notifications else 'No notifications generated'}

=== END OF INCIDENT DATA ===

Use the above incident data to answer the user's question. Reference specific incident IDs, services, error codes, and details from the data above."""
        
        # Build message history
        messages = []
        
        # Add context as first user message or combine with query
        user_content = f"{context_msg}\n\nUser Question: {query}\n\nPlease answer the question using the incident data provided above."
        
        if not chat_history:
            # First message - include full context
            messages.append({"role": "user", "content": user_content})
        else:
            # Include chat history but add context at the start
            messages.append({"role": "user", "content": context_msg})
            messages.append({"role": "assistant", "content": "I have the incident analysis data loaded. How can I help you?"})
            # Add previous conversation (skip first context message if present)
            for msg in chat_history[-4:]:  # Last 4 messages to avoid token limits
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": query})
        
        # Call OpenRouter API
        response = self.client.create_message(
            model=self.model,
            messages=messages,
            system=enhanced_system_prompt,
            max_tokens=2000,  # Increased for better responses
            temperature=0.3
        )
        
        return self.client.extract_content(response)
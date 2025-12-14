import requests
from typing import Dict, Optional
import json

class SlackIntegration:
    """Slack webhook integration"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(self, notification: Dict) -> bool:
        """Send notification to Slack"""
        try:
            msg = notification['message']
            
            # Build Slack blocks
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"{notification['urgency']} {msg['title']}"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:*\n{msg['severity']}"},
                        {"type": "mrkdwn", "text": f"*Channel:*\n{notification['channel']}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Summary:*\n{msg['summary']}"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Actions:*\n" + "\n".join([f"• {a}" for a in msg['actions']])}
                }
            ]
            
            payload = {"blocks": blocks, "text": msg['title']}
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack error: {e}")
            return False


class JiraIntegration:
    """JIRA REST API integration"""
    
    def __init__(self, url: str, email: str, api_token: str):
        self.url = url
        self.auth = (email, api_token)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    def create_ticket(self, ticket_data: Dict) -> Optional[str]:
        """Create JIRA ticket"""
        try:
            priority_map = {"Critical": "Highest", "High": "High", "Medium": "Medium", "Low": "Low"}
            
            payload = {
                "fields": {
                    "project": {"key": "OPS"},
                    "summary": ticket_data['title'],
                    "description": ticket_data['description'],
                    "issuetype": {"name": ticket_data['type']},
                    "priority": {"name": priority_map.get(ticket_data['priority'], "Medium")},
                    "labels": ticket_data['labels']
                }
            }
            
            response = requests.post(
                f"{self.url}/rest/api/3/issue",
                json=payload,
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code == 201:
                return response.json()['key']
            return None
            
        except Exception as e:
            print(f"JIRA error: {e}")
            return None
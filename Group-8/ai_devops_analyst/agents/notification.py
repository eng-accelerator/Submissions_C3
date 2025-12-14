import requests
import json

def notification_agent(state: dict, webhook_url: str):
    """
    Sends a summary to Slack using requests.
    """
    if not webhook_url:
        return {"slack_sent": False, "errors": state.get("errors", []) + ["Slack Webhook URL missing"]}
        
    plan = state.get("remediation_plan", "")
    ticket = state.get("jira_ticket_key", "N/A")
    
    # User requested format: <Jira Ticket reference> - Please check the new issue identified in DevOps Pipline.
    msg_text = f"<{ticket}> - Please check the new issue identified in DevOps Pipline."
    
    payload = {"text": msg_text}
    
    try:
        response = requests.post(webhook_url, json=payload, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            return {"slack_sent": True}
        else:
            error_msg = f"Slack API Error: {response.status_code} - {response.text}"
            return {"slack_sent": False, "errors": state.get("errors", []) + [error_msg]}
            
    except Exception as e:
        return {"slack_sent": False, "errors": state.get("errors", []) + [f"Slack Connection Error: {str(e)}"]}

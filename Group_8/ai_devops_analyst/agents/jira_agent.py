from jira import JIRA

def create_jira_ticket(server, user, token, project_key, summary, description, issue_type="Task"):
    try:
        jira = JIRA(server=server, basic_auth=(user, token))
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
        new_issue = jira.create_issue(fields=issue_dict)
        return new_issue.key
    except Exception as e:
        return f"Error: {str(e)}"

def jira_agent(state: dict, jira_config: dict):
    """
    Creates a JIRA ticket for critical issues.
    """
    if not jira_config.get("url") or not jira_config.get("token"):
        return {"jira_ticket_key": "SKIPPED (No Config)"}
        
    analysis = state.get("analysis_results", {})
    # assume analysis is a dict-like string or json
    summary = f"Incident: {str(analysis)[:50]}..."
    description = state.get("remediation_plan", "No plan generated.")
    
    project_key = jira_config.get("project_key", "KAN")
    issue_type = jira_config.get("issue_type", "Task")
    
    ticket_key = create_jira_ticket(
        server=jira_config["url"],
        user=jira_config["user"],
        token=jira_config["token"],
        project_key=project_key,
        summary=summary,
        description=description,
        issue_type=issue_type
    )
    
    return {"jira_ticket_key": ticket_key}

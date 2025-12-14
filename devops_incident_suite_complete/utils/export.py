from datetime import datetime
from typing import Dict
import json

def export_to_json(results: Dict) -> str:
    """Export results to JSON"""
    export_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "tool": "DevOps-Incident-Suite"
        },
        "analysis": results
    }
    return json.dumps(export_data, indent=2)


def export_to_markdown(results: Dict) -> str:
    """Export results to Markdown"""
    summary = results.get('incident_summary', {})
    md = f"""# Incident Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

- **Total Incidents:** {summary.get('totalIncidents', 0)}
- **Critical (P0):** {summary.get('critical', 0)}
- **High (P1):** {summary.get('high', 0)}
- **Medium (P2):** {summary.get('medium', 0)}
- **Low (P3):** {summary.get('low', 0)}

**Affected Services:** {', '.join(summary.get('affectedServices', []))}

---

## Detailed Incidents

"""
    
    for inc in results.get('classified_incidents', []):
        md += f"""
### {inc['severity']} - {inc['id']}

- **Service:** {inc['service']}
- **Category:** {inc['category']}
- **Timestamp:** {inc['timestamp']}
- **Description:** {inc['description']}
- **Root Cause:** {inc.get('rootCause', 'Unknown')}

"""
    
    md += "\n---\n\n## Remediation Plans\n\n"
    
    for rem in results.get('remediations', []):
        md += f"\n### Remediation for {rem['incidentId']}\n\n"
        md += f"**Priority:** {rem.get('priority', 'N/A')}  \n"
        md += f"**Estimated Time:** {rem.get('estimatedTotalTime', 'N/A')}\n\n"
        
        for fix in rem.get('fixes', []):
            md += f"""
#### Step {fix['step']}: {fix['action']}

**Rationale:** {fix['rationale']}
```bash
{fix.get('command', 'No command')}
```

**Verification:** {fix['verification']}

"""
    
    return md


def export_to_csv(results: Dict) -> str:
    """Export incidents to CSV"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Service', 'Severity', 'Category', 'Description', 'Root Cause'])
    
    for inc in results.get('classified_incidents', []):
        writer.writerow([
            inc['id'],
            inc['service'],
            inc['severity'],
            inc['category'],
            inc['description'],
            inc.get('rootCause', 'Unknown')
        ])
    
    return output.getvalue()
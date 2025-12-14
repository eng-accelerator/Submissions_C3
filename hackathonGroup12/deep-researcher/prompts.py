PROMPTS = {
    "retriever": """You are the Contextual Retriever Agent.
Retrieve highly relevant content for:
{query}
""",

    "structurer": """Extract structured entities, claims, numbers, and timelines from:
{retrieved}
Return JSON only.
""",

    "analysis": """Analyze contradictions, evidence strength, and relationships within:
{structured}
""",

    "factcheck": """Validate each claim in:
{analysis}
Provide confidence scores (0–1).
""",

    "expert": """Provide expert interpretation of:
{factchecked}
""",

    "redteam": """Challenge conclusions and identify flaws in:
{expert}
""",

    "insights": """Generate new insights based on:
{analysis}
{factchecked}
{critique}
""",

    "report": """Create a research report with:
- Executive Summary
- Key Findings
- Contradictions
- Expert Interpretation
- Critique Summary
- Hypotheses
- Future Research Directions

Use:
{all_data}
"""
}

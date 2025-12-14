from core.schema import ResearchState
from agents.base import log_agent_action

def report_node(state: ResearchState):
    """
    ReportBuilderAgent:
    Aggregates Plan, Sources, Claims, Contradictions, Insights into a Markdown doc.
    """
    
    # Logic: Verify if we have insights and claims, then use LLM to write
    from core.api_registry import APIRegistry
    is_demo = state.demo_mode
    has_keys = (APIRegistry.get_key("llm") or 
                APIRegistry.get_key("openrouter_key") or 
                APIRegistry.get_key("anthropic_key"))
    
    md = ""
    
    if not has_keys:
        md = "# Research Report Error\n\n> **⚠️ Critical Error**: Missing API Keys (OpenAI/Anthropic/OpenRouter). Cannot generate report."
        msg = "Report gen skipped: Missing Keys."
    elif not state.insights and not state.claims and not state.sources:
        md = "# Research Report Error\n\n> **⚠️ No Data**: No sources or findings were generated. Please check your Search API Key or query specifics."
        msg = "Report gen skipped: No data."
    else:
        from core.llm import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        try:
             llm = get_llm()
             context_claims = "\n".join([f"- {c.text} ({c.status})" for c in state.claims])
             # Determine Persona based on Audience
             audience = state.target_audience
             system_persona = "You are a professional researcher."
             tone_instruction = "Use a clear, objective tone."
             
             if audience == "Academic":
                 system_persona = "You are a rigorous academic researcher."
                 tone_instruction = "Use formal academic language, cite sources heavily, and focus on methodology and evidence."
             elif audience == "Founder / Business":
                 system_persona = "You are a strategic business consultant."
                 tone_instruction = "Use a concise, executive style. Focus on actionable insights, ROI, and market implications."
             elif audience == "Marketer":
                 system_persona = "You are a marketing strategist."
                 tone_instruction = "Use persuasive, engaging language. Focus on audience needs, trends, and messaging."
             elif audience == "Engineer":
                 system_persona = "You are a technical architect."
                 tone_instruction = "Use precise technical terminology. Focus on implementation details, trade-offs, and specs."
             elif audience == "Policy / Legal":
                 system_persona = "You are a policy analyst."
                 tone_instruction = "Use precise, regulated language. Focus on compliance, risks, and frameworks."

             prompt = (f"Write a comprehensive research report on '{state.question}' based on these findings:\n"
                       f"{context_claims}\n\n"
                       f"Community Signals:\n{state.community_signals}\n\n"
                       f"Practical Steps:\n{state.practical_steps}\n\n"
                       f"Context:\n"
                       f"- Objective: {state.research_objective}\n"
                       f"- Target Audience: {state.target_audience}\n"
                       f"- Time Sensitivity: {state.time_sensitivity}\n"
                       f"- Geography: {state.geography}\n"
                       f"- Assumptions: {state.known_assumptions}\n"
                       f"- Exclusions: {state.source_exclusions}\n"
                       f"- Confidence Target: {state.confidence_score_target}\n\n"
                       f"Instructions: {tone_instruction}\n"
                       "Structure: Executive Summary, Key Findings, Community Signals (if any), Practical Playbook (if any), Academic Evidence, Implications.\n"
                       "CRITICAL: You must cite your sources. Use inline links [Source Title](URL) for every claim made. Do not invent sources."
                       "Use Markdown.")
             
             resp = llm.invoke([SystemMessage(content=system_persona), HumanMessage(content=prompt)])
             md = resp.content
             msg = "Generated report via LLM."
        except Exception as e:
             md = f"# Error generating report\n\n{e}"
             msg = "Report gen failed."
    new_log = log_agent_action(state, "ReportBuilderAgent", msg)

    return {
        "report_md": md,
        "logs": [new_log]
    }

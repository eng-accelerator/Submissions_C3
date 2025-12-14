from core.schema import ResearchState, AgentLog
from core.llm import get_llm
from core.api_registry import APIRegistry
from agents.base import log_agent_action
from langchain_core.messages import SystemMessage, HumanMessage
import json

def judge_node(state: ResearchState):
    """
    JudgeAgent:
    Critiques the draft report based on rubric.
    """
    report = state.report_md
    if not report:
        return {"logs": [log_agent_action(state, "JudgeAgent", "No report to judge.")]}

    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    
    # Max loops constraint
    if state.review_count >= 5:
        return {
            "feedback": None, # Stop looping
            "logs": [log_agent_action(state, "JudgeAgent", "Max review loops (5) reached. Approving.")]
        }

    if not llm_key:
        return {
             "feedback": None,
             "judge_scorecard": {},
             "logs": [log_agent_action(state, "JudgeAgent", "Skipping judge: Missing LLM Key.")]
        }

    try:
        llm = get_llm()
        if not llm: return {}
        
        prompt = f"""
        You are a critical Research Judge. Evaluate this report:
        Objective: {state.research_objective}
        
        Report:
        {report[:10000]}
        
        Output valid JSON with:
        - citation_coverage (0-10)
        - source_diversity (0-10)
        - contradictions_handled (0-10)
        - overconfidence_risk (0-10, lower is better)
        - overall_score (0-10)
        - required_fixes (list of strings, empty if approved)
        """
        
        import re
        
        res = llm.invoke([SystemMessage(content="You are a strict judge JSON outputter."), HumanMessage(content=prompt)])
        content = res.content.replace("```json", "").replace("```", "").strip()
        
        # Escape newlines/control characters inside strings to prevent JSON errors
        # This regex looks for newlines that are NOT between generic JSON structure tokens.
        # Simple fallback: use strict=False or just try/except with manual cleanup
        try:
            scorecard = json.loads(content, strict=False)
        except:
             # Fallback: aggressive cleanup
             content_clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
             try:
                scorecard = json.loads(content_clean, strict=False)
             except:
                # Last resort: text parse
                scorecard = {
                    "overall_score": 5, 
                    "required_fixes": [f"Review failed to parse JSON. Content: {content[:100]}..."]
                }
        
        fixes = scorecard.get("required_fixes", [])
        score = scorecard.get("overall_score", 0)
        
        if fixes or score < 7:
            feedback = "Critique: " + "; ".join(fixes)
            msg = f"Critique provided (Score: {score}). Fixes: {len(fixes)}"
        else:
            feedback = None
            msg = f"Report approved (Score: {score})."
            
    except Exception as e:
        scorecard = {"error": str(e), "required_fixes": []}
        feedback = None
        msg = f"Judge Error: {e}"
            
    return {
        "judge_scorecard": scorecard,
        "feedback": feedback,
        "review_count": state.review_count + 1,
        "logs": [log_agent_action(state, "JudgeAgent", msg)]
    }

def revise_node(state: ResearchState):
    """
    Revises report based on Judge's feedback.
    """
    scorecard = state.judge_scorecard
    fixes = scorecard.get("required_fixes", [])
    if not fixes:
        return {"logs": [log_agent_action(state, "ReviserAgent", "No fixes needed.")]}
        
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    
    if not llm_key:
         return {"logs": [log_agent_action(state, "ReviserAgent", "Skipping revision: Missing LLM Key.")]}

    try:
        llm = get_llm()
        if not llm: return {}
        
        prompt = f"""
        Refine this report based on the feedback.
        Feedback: {fixes}
        
        Original Report:
        {state.report_md[:10000]}
        
        Return the FULL updated markdown report. Do not add conversational filler.
        """
        res = llm.invoke([SystemMessage(content="You are an expert editor."), HumanMessage(content=prompt)])
        new_report = res.content
        msg = "Applied LLM revisions."
    except Exception as e:
        new_report = state.report_md + f"\n\n[Revision Failed: {e}]"
        msg = "Revision failed."
            
    return {
        "report_md": new_report,
        "logs": [log_agent_action(state, "ReviserAgent", msg)]
    }

from core.schema import ResearchState
from agents.base import log_agent_action
from core.api_registry import APIRegistry

def contradiction_node(state: ResearchState):
    """
    ContradictionConsensusAgent:
    Looks for conflicting claims.
    """
    test_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    
    if not test_key:
        msg = "Refinement skipped: No LLM Key."
        return {"contradictions": [], "logs": [log_agent_action(state, "ContradictionConsensusAgent", msg)]}

    from core.llm import get_llm
    from core.schema import Contradiction
    from langchain_core.messages import SystemMessage, HumanMessage
    
    contradictions = []
    
    try:
         llm = get_llm()
         if llm and state.claims and len(state.claims) > 1:
             claims_text = "\n".join([f"{c.id}: {c.text}" for c in state.claims])
             prompt = (f"Identify any contradictions between these claims:\n{claims_text}\n\n"
                       "Rules:\n"
                       "1. Weight academic sources (arXiv, OpenAlex, Journals) higher than blogs/news.\n"
                       "2. Prefer claims backed by >=2 independent academic sources.\n"
                       "3. Return JSON list: [{'claim_a_id': '...', 'claim_b_id': '...', 'description': '...', 'severity': 'High|Medium|Low'}]. "
                       "Return empty list if none.")
             
             resp = llm.invoke([SystemMessage(content="Analyst"), HumanMessage(content=prompt)])
             import json
             clean = resp.content.replace("```json", "").replace("```", "").strip()
             data = json.loads(clean)
             
             real_cons = []
             for idx, item in enumerate(data):
                 real_cons.append(Contradiction(
                     id=f"real_con_{idx}",
                     claim_a_id=item.get('claim_a_id', ''),
                     claim_b_id=item.get('claim_b_id', ''),
                     description=item.get('description', ''),
                     severity=item.get('severity', 'Low')
                 ))
             contradictions = real_cons
             msg = f"Identified {len(contradictions)} contradictions via LLM."
         else:
             msg = "Skipping contradiction check (Not enough claims)."
    except Exception as e:
        msg = f"LLM Contradiction Check Failed: {e}"

    new_log = log_agent_action(state, "ContradictionConsensusAgent", msg)

    return {
        "contradictions": contradictions,
        "logs": [new_log]
    }

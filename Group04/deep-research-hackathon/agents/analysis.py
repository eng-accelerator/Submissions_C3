from core.schema import ResearchState
from agents.base import log_agent_action
from core.api_registry import APIRegistry

def analysis_node(state: ResearchState):
    """
    CriticalAnalysisAgent:
    Extracts claims and findings from the credible sources.
    """
    # Demo logic
    # Demo logic
    llm_key = (APIRegistry.get_key("llm") or 
               APIRegistry.get_key("openrouter_key") or 
               APIRegistry.get_key("anthropic_key"))
    is_demo = not llm_key
    
    claims = []
    
    # Validation
    if not llm_key:
        msg = "Analysis skipped: Missing LLM Key (OpenAI/Anthropic/OpenRouter)."
        return {"claims": [], "logs": [log_agent_action(state, "CriticalAnalysisAgent", msg)]}

    from core.llm import get_llm
    from core.schema import Claim
    from langchain_core.messages import SystemMessage, HumanMessage
    
    try:
        llm = get_llm()
        if llm and state.sources:
            # Combine sources context
            context = "\n\n".join([f"Source {s.id}: {s.snippet}" for s in state.sources[:5]])
            prompt = (f"Extract 3-5 key claims from the text below regarding '{state.question}'. "
                      "Return JSON list: [{'text': '...', 'status': 'Verified|Disputed', 'confidence': 80}]. "
                      f"\n\nContext:\n{context}")
            
            response = llm.invoke([SystemMessage(content="You are a strict analyst."), HumanMessage(content=prompt)])
            
            # Robust JSON parse
            import json
            import re
            
            content = response.content.strip()
            # 1. Try simple clean
            clean = content.replace("```json", "").replace("```", "").strip()
            
            data = None
            try:
                data = json.loads(clean)
            except:
                # 2. Try regex extraction (List OR Dict)
                match = re.search(r'(\[.*\]|\{.*\})', content, re.DOTALL)
                if match:
                    try:
                         # 3. Try removing control chars
                         clean_chars = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', match.group(0))
                         data = json.loads(clean_chars)
                    except:
                         pass
            
            if data is None:
                 raise ValueError(f"No JSON found. Start of content: {content[:100]}")

            # Normalize data (Ensure it is a list)
            if isinstance(data, dict):
                # Look for common keys
                if "claims" in data: data = data["claims"]
                elif "data" in data: data = data["data"]
                else: data = [data] # Treat single dict as one item
            
            if not isinstance(data, list):
                # Fallback
                 data = []
            
            
            real_claims = []
            for idx, item in enumerate(data):
                real_claims.append(Claim(
                    id=f"real_c_{idx}",
                    text=item.get('text', 'Unknown'),
                    status=item.get('status', 'Uncertain'),
                    confidence_score=item.get('confidence', 50),
                    citation_source_ids=[state.sources[0].id] if state.sources else [] # Lazy citation binding for MVP
                ))
            claims = real_claims
            
            claims_summary = "\n".join([f"- {c.text} ({c.status})" for c in claims[:3]])
            msg = f"Extracted {len(claims)} claims. Key findings:\n{claims_summary}"
        else:
            msg = "Skipping analysis: No credible sources found to analyze."
    except Exception as e:
        msg = f"LLM Analysis Failed: {e}" 

    new_log = log_agent_action(state, "CriticalAnalysisAgent", msg)
    
    return {
        "claims": claims,
        "logs": [new_log]
    }

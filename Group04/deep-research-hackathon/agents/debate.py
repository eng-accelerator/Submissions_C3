from core.schema import ResearchState
from core.llm import get_llm
from core.api_registry import APIRegistry
from agents.base import log_agent_action
from langchain_core.messages import SystemMessage, HumanMessage

def debate_round(state: ResearchState):
    """
    Simulates a round of debate.
    """
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    is_demo = False # Removed
    transcript = state.debate_transcript or []
    round_num = len(transcript) + 1
    
    if not llm_key:
         msg = "Debate skipped: Missing LLM Key."
    else:
        try:
            # Dual Model Setup
            from core.llm import get_llm
            from langchain_openai import ChatOpenAI
            from langchain_anthropic import ChatAnthropic
            
            # 1. Pro Model (Default: OpenAI or OpenRouter)
            llm_pro = get_llm() 
            pro_name = "Pro (GPT/OpenRouter)"
            
            # 2. Con Model (Try Anthropic, else replicate Pro)
            anthro_key = APIRegistry.get_key("anthropic_key")
            if anthro_key:
                llm_con = ChatAnthropic(api_key=anthro_key, model="claude-3-opus-20240229")
                con_name = "Con (Claude 3 Opus)"
            else:
                llm_con = llm_pro
                con_name = "Con (Devil's Advocate)"

            # Pro Turn
            transcript_text = "\n".join([f"{t['role']}: {t['content']}" for t in transcript])
            pro_prompt = f"Topic: {state.question}. Context: {transcript_text}. You are {pro_name}. Argue FOR the motion. Be concise (1 paragraph)."
            pro_res = llm_pro.invoke([SystemMessage(content="You are a skilled debater."), HumanMessage(content=pro_prompt)])
            transcript.append({"role": pro_name, "content": pro_res.content, "round": round_num})
            
            # Con Turn
            con_prompt = f"Topic: {state.question}. Context: {transcript_text}\n{pro_name}: {pro_res.content}. You are {con_name}. Argue AGAINST the motion. Be concise (1 paragraph)."
            con_res = llm_con.invoke([SystemMessage(content="You are a skilled debater."), HumanMessage(content=con_prompt)])
            transcript.append({"role": con_name, "content": con_res.content, "round": round_num})
            
            msg = f"Debated round {round_num}: {pro_name} vs {con_name}.\n\n**{pro_name}**: {pro_res.content[:200]}...\n\n**{con_name}**: {con_res.content[:200]}..."
        except Exception as e:
            msg = f"Debate Error: {e}"

    return {
        "debate_transcript": transcript,
        "logs": [log_agent_action(state, "Debater", msg)]
    }

def moderator_node(state: ResearchState):
    """
    Synthesizes the debate into a final position.
    """
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    transcript = state.debate_transcript
    
    synthesis = ""
    if not llm_key:
        msg = "Moderator skipped: Missing LLM Key."
        synthesis = "## Moderator Error\nMissing API Keys."
    elif not transcript:
        msg = "Moderator skipped: No transcript."
        synthesis = "## Moderator Error\nNo debate transcript found."
    else:
        try:
            llm = get_llm()
            prompt = f"""
            Summarize this debate and provide a final verdict.
            Transcript: {transcript}
            
            Format:
            ## Executive Summary
            ## Key Contentions
            ## Final Verdict
            """
            res = llm.invoke([SystemMessage(content="You are a wise Moderator."), HumanMessage(content=prompt)])
            synthesis = res.content
            msg = "Generated LLM synthesis."
        except Exception as e:
            msg = f"Moderator Error: {e}"
            synthesis = f"## Moderator Error\n{e}"
        
    return {
        "report_md": synthesis, # Moderator output *is* the report in this mode
        "logs": [log_agent_action(state, "Moderator", msg)]
    }

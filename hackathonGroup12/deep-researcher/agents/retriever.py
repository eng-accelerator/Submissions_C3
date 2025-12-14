import json

def retriever_node(state, llm, tavily):
    youtube_context = ""

    if state.get("youtube_results"):
        for i, v in enumerate(state["youtube_results"]):
            youtube_context += f"""
            --- YouTube Video {i+1} ---
            Title: {v['video']['title']}
            URL: {v['video']['url']}
            Summary:
            {json.dumps(v['summary'], indent=2)}
            """

    prompt = f"""
    You are the Retriever Agent.
    Research Query: {state['query']}

    YouTube Insights:
    {youtube_context}
    """

    resp = llm.invoke(prompt)
    state["retrieved"] = resp.content
    return state

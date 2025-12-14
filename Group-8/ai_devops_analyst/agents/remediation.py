from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults
from core.llm import get_llm
import json

def remediation_agent(state: dict, api_key: str):
    """
    Generates a remediation plan based on log analysis and cookbook context.
    If cookbook context is missing, it uses Web Search.
    Output is strictly a Markdown Table.
    """
    analysis = state.get("analysis_results", "")
    context = state.get("cookbook_context", "")
    
    # Determine if we need to search the web
    web_context = ""
    source_used = "Cookbook"
    
    # Simple heuristic: if context is empty or looks like a default "not found" message
    if not context or "No cookbook provided" in context or "No relevant documents" in context:
        source_used = "Web Search"
        search = DuckDuckGoSearchResults()
        
        # Formulate a search query from the analysis
        # If analysis is dict, extract summary; if string, use first 100 chars
        if isinstance(analysis, dict):
            query = f"{analysis.get('error_type', '')} {analysis.get('summary', '')} remediation"
        else:
            query = f"{str(analysis)[:100]} remediation"
            
        try:
            # Returns a list of results with snippets and links
            web_context = search.invoke(query)
        except Exception as e:
            web_context = f"Search failed: {e}"
            
    final_context = context if context and source_used == "Cookbook" else web_context

    llm = get_llm(api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior DevOps Engineer. Create a detailed remediation plan in a structured Table format."),
        ("user", """
        Issue Analysis: {analysis}
        
        Reference Context ({source}): {context}
        
        Task:
        1. Review the Issue Analysis (which may contain multiple 'findings').
        2. For EACH finding:
           a. Identify the specific incident/error.
           b. Define the root cause.
           c. Provide remediation steps.
           d. State the source.
        3. Consolidate ALL findings into a single Markdown Table.
        
        IMPORTANT: Output the result ONLY as a Markdown Table with the following columns:
        | Incident | Severity | Root Cause | Detailed Remediation | Source |
        
        Source Column Rules:
        - If using Cookbook Context: Extract the page number from the context header (e.g., "[Source: Cookbook, Page: 5]") and format as "Cookbook (Page 5)".
        - If using Web Search: Extract the URL from the search result context and format as "Web: [URL]".
        
        Do not add preamble or postscript text. Just the table.
        """)
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "analysis": str(analysis), 
            "context": final_context,
            "source": source_used
        })
        return {"remediation_plan": response.content}
    except Exception as e:
        return {"remediation_plan": f"Error generating plan: {e}"}

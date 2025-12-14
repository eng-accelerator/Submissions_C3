import requests
from core.api_registry import APIRegistry
from core.schema import Source
from typing import List

def search_perplexity(query: str, max_results: int = 5) -> List[Source]:
    """
    Searches using Perplexity Sonar API.
    """
    api_key = APIRegistry.get_key("perplexity")
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    model_name = "sonar-reasoning-pro"

    # Fallback to OpenRouter if no Perplexity Key
    if not api_key:
        or_key = APIRegistry.get_key("openrouter_key")
        if or_key:
            print("Info: Using OpenRouter for Perplexity Search.")
            api_key = or_key
            url = "https://openrouter.ai/api/v1/chat/completions"
            model_name = "perplexity/llama-3-sonar-large-32k-online"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501", # Required by OpenRouter
                "X-Title": "DeepTrace Researcher"
            }
        else:
            print("Warning: No Perplexity or OpenRouter API Key found.")
            return []
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant. Return a concise summary of the topic with citations."},
            {"role": "user", "content": query}
        ]
    }
    
    # Headers are already set above based on provider
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Perplexity returns content + citations.
        # We need to parse this into "Sources". 
        # Since Perplexity is an answer engine, strict "search results" are citations.
        # Ideally we'd use 'sonar' which might give us citations in the response metadata if available.
        # Note: Perplexity API format is OpenAI compatible. Citations are in 'citations' field if supported.
        
        content = data['choices'][0]['message']['content']
        # For now, wrap the whole answer as a "Source" or try to extract.
        # Actually Perplexity API 'citations' field is usually just a list of URLs.
        
        citations = data.get('citations', [])
        sources = []
        
        for i, url in enumerate(citations):
            sources.append(Source(
                id=f"perplex-{i}",
                title=f"Perplexity Citation {i+1}",
                url=url,
                snippet=f"Referenced in Perplexity answer for: {query}",
                domain=url.split('/')[2],
                date="2025", # Approximation
                credibility_score=80
            ))
            
        # Also treat the Perplexity answer itself as a synthesized source
        sources.append(Source(
            id="perplex-answer",
            title="Perplexity Sonar Synthesis",
            url="https://perplexity.ai",
            snippet=content[:500] + "...",
            domain="perplexity.ai",
            date="2025",
            credibility_score=90
        ))
        
        return sources
        
    except Exception as e:
        print(f"Perplexity Error: {e}")
        return []

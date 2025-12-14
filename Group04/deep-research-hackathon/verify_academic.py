
from tools.retrieval_arxiv import search_arxiv
from tools.retrieval_openalex import search_openalex
from tools.retrieval_crossref import search_crossref
from tools.retrieval_semanticscholar import search_semanticscholar
from core.schema import Source

def verify_tool(name, func, query):
    print(f"--- Verifying {name} ---")
    try:
        results = func(query, max_results=2)
        if not results:
            print(f"⚠️  {name} returned 0 results (Network might be slow or query difficult)")
            return
        
        for s in results:
            print(f"✅ Found: {s.title} ({s.date}) - {s.venue or 'No Venue'}")
            if s.authors:
                print(f"   Authors: {s.authors[:2]}...")
            if s.pdf_url:
                print(f"   PDF: {s.pdf_url}")
            
            # Simple Schema Check
            assert isinstance(s, Source)
            
    except Exception as e:
        print(f"❌ {name} Failed: {e}")

if __name__ == "__main__":
    query = "AI Agents"
    verify_tool("arXiv", search_arxiv, query)
    verify_tool("OpenAlex", search_openalex, query)
    verify_tool("Crossref", search_crossref, query)
    
    # Semantic Scholar (No key, might hit rate limit or work)
    verify_tool("Semantic Scholar (No Key)", lambda q, m: search_semanticscholar(q, m, None), query)

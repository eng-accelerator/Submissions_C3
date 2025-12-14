import requests
import xmltodict
from typing import List
from core.schema import Source
import time

def search_pubmed(query: str, max_results: int = 5) -> List[Source]:
    """
    Searches PubMed using NCBI E-utilities.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    try:
        # 1. ESearch
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        r = requests.get(f"{base_url}/esearch.fcgi", params=search_params)
        r.raise_for_status()
        search_data = r.json()
        
        id_list = search_data['esearchresult']['idlist']
        if not id_list:
            return []
            
        # 2. EFetch
        ids = ",".join(id_list)
        fetch_params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml"
        }
        r_fetch = requests.get(f"{base_url}/efetch.fcgi", params=fetch_params)
        r_fetch.raise_for_status()
        
        # Parse XML
        data = xmltodict.parse(r_fetch.content)
        articles = data.get('PubmedArticleSet', {}).get('PubmedArticle', [])
        
        if isinstance(articles, dict): # Single result
            articles = [articles]
            
        sources = []
        for art in articles:
            medline = art.get('MedlineCitation', {})
            article = medline.get('Article', {})
            
            # Extract fields
            pmid = medline.get('PMID', {}).get('#text', 'N/A')
            title = article.get('ArticleTitle', 'No Title')
            
            # Abstract
            abstract_text = ""
            abs_raw = article.get('Abstract', {}).get('AbstractText', [])
            if isinstance(abs_raw, list):
                abstract_text = " ".join([x.get('#text', '') if isinstance(x, dict) else x for x in abs_raw])
            elif isinstance(abs_raw, dict):
                abstract_text = abs_raw.get('#text', '')
            else:
                abstract_text = str(abs_raw)
                
            # Date
            pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', 'N/A')
            
            # Authors
            author_list = article.get('AuthorList', {}).get('Author', [])
            authors = []
            if isinstance(author_list, list):
                for aut in author_list:
                    last = aut.get('LastName', '')
                    curr_auth = f"{last}"
                    authors.append(curr_auth)
            elif isinstance(author_list, dict):
                authors.append(author_list.get('LastName', ''))
                
            sources.append(Source(
                id=f"pubmed-{pmid}",
                title=title,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                snippet=abstract_text[:500] + "...",
                domain="pubmed.ncbi.nlm.nih.gov",
                date=year,
                authors=authors,
                credibility_score=95,
                venue="PubMed",
                metadata={"pmid": pmid}
            ))
            
        # Rate limit kindness
        time.sleep(0.5) 
        
        return sources
        
    except Exception as e:
        print(f"PubMed Error: {e}")
        return []

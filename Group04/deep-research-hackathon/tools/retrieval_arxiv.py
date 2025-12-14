
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List
from core.schema import Source
import datetime

def search_arxiv(query: str, max_results: int = 5) -> List[Source]:
    """
    Searches arXiv API and returns a list of Source objects.
    Reference: https://arxiv.org/help/api/user-manual
    """
    base_url = 'http://export.arxiv.org/api/query?'
    
    # Clean query slightly
    search_query = f'all:{query}'
    
    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    
    url = base_url + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            
        root = ET.fromstring(data)
        
        # arXiv returns Atom feed. Namespace usually http://www.w3.org/2005/Atom
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        sources = []
        
        for entry in root.findall('atom:entry', ns):
            # ID
            id_url = entry.find('atom:id', ns).text
            # Basic ID extraction (e.g. http://arxiv.org/abs/2101.12345v1 -> 2101.12345v1)
            paper_id = id_url.split('/')[-1]
            
            # Title
            title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
            
            # Summary (Snippet)
            summary = entry.find('atom:summary', ns).text.replace('\n', ' ').strip()
            
            # Published
            published_str = entry.find('atom:published', ns).text
            try:
                # 2021-01-29T18:00:00Z
                dt = datetime.datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                date_str = dt.strftime("%Y-%m-%d")
                year = dt.year
            except:
                date_str = published_str
                year = None
                
            # Authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
                
            # Links (PDF vs Abs)
            pdf_url = None
            abs_url = id_url
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                elif link.get('rel') == 'alternate':
                    abs_url = link.get('href')
            
            source = Source(
                id=f"arxiv_{paper_id}",
                title=title,
                url=abs_url,
                snippet=summary[:500] + "...", # Truncate for snippet
                domain="arxiv.org",
                date=date_str,
                authors=authors,
                year=year,
                venue="arXiv Preprint",
                pdf_url=pdf_url,
                abstract=summary,
                credibility_score=80, # Baseline for arXiv
                credibility_reason="Indexed in arXiv (Preprint)"
            )
            sources.append(source)
            
        return sources

    except Exception as e:
        print(f"arXiv Search Failed: {e}")
        return []

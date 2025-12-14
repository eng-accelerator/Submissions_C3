import requests
from typing import List
from core.schema import Source

def search_clinical_trials(query: str, max_results: int = 5) -> List[Source]:
    """
    Searches ClinicalTrials.gov API v2.
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    params = {
        "query.term": query,
        "pageSize": max_results,
        "format": "json"
    }
    
    try:
        r = requests.get(base_url, params=params)
        r.raise_for_status()
        data = r.json()
        
        sources = []
        studies = data.get('studies', [])
        
        for study in studies:
            protocol = study.get('protocolSection', {})
            ident = protocol.get('identificationModule', {})
            status_mod = protocol.get('statusModule', {})
            
            nct_id = ident.get('nctId', 'N/A')
            title = ident.get('briefTitle', 'No Title')
            status = status_mod.get('overallStatus', 'Unknown')
            
            # Condish
            conds = protocol.get('conditionsModule', {}).get('conditions', [])
            cond_str = ", ".join(conds[:3])
            
            desc = protocol.get('descriptionModule', {}).get('briefSummary', 'No description.')
            
            sources.append(Source(
                id=f"ctgov-{nct_id}",
                title=title,
                url=f"https://clinicaltrials.gov/study/{nct_id}",
                snippet=f"Status: {status}. Conditions: {cond_str}. {desc[:200]}...",
                domain="clinicaltrials.gov",
                date=status_mod.get('startDateStruct', {}).get('date', 'N/A'),
                credibility_score=90,
                venue="ClinicalTrials.gov",
                metadata={"status": status, "nct_id": nct_id}
            ))
            
        return sources
        
    except Exception as e:
        print(f"ClinicalTrials Error: {e}")
        return []

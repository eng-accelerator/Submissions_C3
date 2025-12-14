from concurrent.futures import ThreadPoolExecutor
import arxiv


# API clients will be passed to functions
def fetch_tavily(tavily_client, query, max_results=5):
    response = tavily_client.search(query=query, search_depth="advanced", max_results=max_results)
    return "\n".join(
                f"[WEB] {r['title']} ({r['url']}): {r['content']}"
                for r in response["results"]
            )

def fetch_arxiv(query, max_results=5):
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    client = arxiv.Client(page_size=max_results)
    papers = []
    for result in client.results(search):
        papers.append(
            f"[ARXIV] {result.title}\n"
            f"Authors: {', '.join(a.name for a in result.authors)}\n"
            f"Published: {result.published.date()}\n"
            f"Summary: {result.summary}"
        )
    return "\n\n".join(papers)

def fetch_parallel(tavily_client, query):
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_arxiv = executor.submit(fetch_arxiv, query)
        f_web = executor.submit(fetch_tavily, tavily_client, query)
        return f_arxiv.result(), f_web.result()
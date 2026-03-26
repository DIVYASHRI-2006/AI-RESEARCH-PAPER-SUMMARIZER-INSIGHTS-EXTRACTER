import requests
import feedparser
import pandas as pd
import time
import json

from helper_function import insight_extraction


# =========================
# FETCH ARXIV PAPERS
# =========================
def fetch_arxiv_papers(query, max_results=20, start=0):

    url = "http://export.arxiv.org/api/query"

    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from arXiv: {e}")
        return []

    feed = feedparser.parse(response.text)

    papers = []

    for entry in feed.entries:

        try:
            insight = insight_extraction(entry.summary.strip())
        except Exception as e:
            print(f"Insight extraction failed for {entry.id}")
            insight = {"error": str(e)}

        paper_data = {
            "source": "arxiv",
            "search_query": query,
            "paper_id": entry.id,
            "title": entry.title.strip(),
            "authors": ", ".join([a.name for a in entry.authors]),
            "abstract": entry.summary.strip(),
            "published": entry.published,
            "categories": ", ".join([tag.term for tag in entry.tags]),
            "pdf_url": next(
                (link.href for link in entry.links
                 if link.type == "application/pdf"),
                None
            ),
            "insight": insight
        }

        papers.append(paper_data)

        # Small delay to avoid Groq rate limits
        time.sleep(1)

    # Respect arXiv rate limit
    time.sleep(3)

    return papers


# =========================
# SEARCH QUERIES
# =========================
queries = [
'all:"LLM pipeline"',
'all:"AI agent framework"',
'all:"autonomous agents" AND all:"language model"',
'all:"tool augmented language model"',
'all:"function calling" AND all:"large language model"',
'all:"multi agent system" AND all:"LLM"',
'all:"AI workflow automation"'

]

all_papers = []

# =========================
# LOOP THROUGH QUERIES
# =========================
for query in queries:
    print(f"\nFetching papers for: {query}")
    papers = fetch_arxiv_papers(query, max_results=10)
    all_papers.extend(papers)


# =========================
# REMOVE DUPLICATES
# =========================
unique_papers = {paper["paper_id"]: paper for paper in all_papers}
final_papers = list(unique_papers.values())


# =========================
# SAVE TO JSON
# =========================
with open("arxiv_papers.json", "w", encoding="utf-8") as f:
    json.dump(final_papers, f, indent=4, ensure_ascii=False)

print("\nSaved successfully to arxiv_papers.json ✅")
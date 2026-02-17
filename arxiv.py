import feedparser
import requests
import time
import pandas as pd


def fetch_arxiv_papers(query, max_results=50, start=0):
    url = "http://export.arxiv.org/api/query"

    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results
    }

    response = requests.get(url, params=params)
    feed = feedparser.parse(response.text)

    papers = []

    for entry in feed.entries:
        papers.append({
            "source": "arxiv",
            "paper_id": entry.id,
            "title": entry.title.strip(),
            "authors": ", ".join([a.name for a in entry.authors]),
            "abstract": entry.summary.strip(),
            "published": entry.published,
            "categories": ", ".join([tag.term for tag in entry.tags]),
            "pdf_url": next(
                (
                    link.href
                    for link in entry.links
                    if link.type == "application/pdf"
                ),
                None
            )
        })

    # arXiv rate limit safety
    time.sleep(3)

    return papers


# -----------------------------
# Fetch papers
# -----------------------------
papers = fetch_arxiv_papers(
    "all:machine OR all:learning",
    max_results=50
)

# -----------------------------
# Convert to DataFrame
# -----------------------------
df = pd.DataFrame(papers)

# -----------------------------
# Save to Excel
# -----------------------------
df.to_excel("arxiv_papers.xlsx", index=False)

print("Saved successfully to arxiv_papers.xlsx")

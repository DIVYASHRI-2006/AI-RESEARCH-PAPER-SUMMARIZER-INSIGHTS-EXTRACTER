import requests
import xml.etree.ElementTree as ET
import json
import time

search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

queries = [
    'artificial intelligence',
    'machine learning healthcare',
    'deep learning medical',
    'neural networks medicine',
    'AI clinical research'
]

file_name = "papers.json"

all_papers = []
seen_pmids = set()

for query in queries:
    print(f"\n🔎 Searching for: {query}")

    # ---------- SEARCH ----------
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 50   # 🔥 increased
    }

    response = requests.get(search_url, params=params)
    pmids = response.json()["esearchresult"]["idlist"]

    if not pmids:
        continue

    time.sleep(1)

    # ---------- FETCH ----------
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    xml_data = requests.get(fetch_url, params=fetch_params).text
    root = ET.fromstring(xml_data)

    # ---------- PARSE ----------
    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(".//PMID")

        if not pmid or pmid in seen_pmids:
            continue

        seen_pmids.add(pmid)

        title = article.findtext(".//ArticleTitle")

        # Get abstract
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join([a.text for a in abstract_texts if a.text])

        # Skip if no abstract
        if not abstract:
            continue

        all_papers.append({
            "title": title.strip() if title else "No Title",
            "abstract": abstract.strip()
        })

    time.sleep(1)

# ---------- SAVE ----------
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(all_papers, f, indent=2)

print("\n💾 Saved to papers.json")
print("📊 Total papers:", len(all_papers))
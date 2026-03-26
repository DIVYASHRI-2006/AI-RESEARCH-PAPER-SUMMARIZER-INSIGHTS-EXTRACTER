import json
import os

documents = []
metadatas = []


# STEP 1: LOAD DATA FROM parsed_output


parsed_folder = "parsed_output"

for filename in os.listdir(parsed_folder):
    if filename.endswith(".json"):

        file_path = os.path.join(parsed_folder, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})

            # JSON key typo handled
            insight = data.get("insigth", {})

            text = f"""
Title: {metadata.get('title', '')}
Authors: {", ".join(metadata.get('authors', []))}
Publication Year: {metadata.get('publication_year', '')}
DOI: {metadata.get('doi', '')}
Keywords: {", ".join(metadata.get('keywords', []))}

Domain: {", ".join(insight.get("domain", []))}
Research Problem: {insight.get("research_problem", "")}
Methods: {", ".join(insight.get("methods", []))}
Datasets: {", ".join(insight.get("datasets", []))}
Metrics: {", ".join(insight.get("metrics", []))}
Key Findings: {insight.get("key_findings", "")}
Limitations: {insight.get("limitations", "")}
Future Directions: {insight.get("future_directions", "")}

Abstract:
{data.get("abstract", "")}

Summary:
{data.get("summary", "")}
"""

            documents.append(text)

            metadatas.append({
                "paper_id": data.get("document_id"),
                "title": metadata.get("title"),
                "source": data.get("source_file"),
                "publication_year": metadata.get("publication_year"),
                "domain": insight.get("domain", []),
            })

        except Exception as e:
            print(f"Error processing file {filename}: {e}")


# STEP 2: LOAD DATA FROM ARXIV


with open("arxiv_papers.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

for paper in papers:

    insight = paper.get("insight", {})

    text = f"""
Title: {paper.get('title', '')}
Authors: {paper.get('authors', '')}
Published: {paper.get('published', '')}
Categories: {paper.get('categories', '')}

Domain: {", ".join(insight.get("domain", []))}
Research Problem: {insight.get("research_problem", "")}
Methods: {", ".join(insight.get("methods", []))}
Datasets: {", ".join(insight.get("datasets", []))}
Metrics: {", ".join(insight.get("metrics", []))}
Key Findings: {insight.get("key_findings", "")}
Limitations: {insight.get("limitations", "")}
Future Directions: {insight.get("future_directions", "")}

Abstract:
{paper.get("abstract", "")}
"""

    documents.append(text)

    metadatas.append({
        "paper_id": paper.get("paper_id"),
        "title": paper.get("title"),
        "source": paper.get("source"),
        "categories": paper.get("categories"),
        "domain": insight.get("domain", []),
    })

# ==========================================
# STEP 3: LOAD DATA FROM PUBMED


with open("pubmed_papers.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

for paper in papers:

    insight = paper.get("insight", {})

    text = f"""
Title: {paper.get('title', '')}
Authors: {", ".join(paper.get('authors', []))}
Journal: {paper.get('journal', '')}
Keywords: {", ".join(paper.get('keywords', []))}

Domain: {", ".join(insight.get("domain", [])) if insight else ""}
Research Problem: {insight.get("research_problem", "") if insight else ""}
Methods: {", ".join(insight.get("methods", [])) if insight else ""}
Datasets: {", ".join(insight.get("datasets", [])) if insight else ""}
Metrics: {", ".join(insight.get("metrics", [])) if insight else ""}
Key Findings: {insight.get("key_findings", "") if insight else ""}
Limitations: {insight.get("limitations", "") if insight else ""}
Future Directions: {insight.get("future_directions", "") if insight else ""}

Abstract:
{paper.get("abstract", "")}
"""

    documents.append(text)

    metadatas.append({
        "paper_id": paper.get("paper_id"),
        "title": paper.get("title"),
        "source": "pubmed",
        "journal": paper.get("journal"),
        "domain": insight.get("domain", []) if insight else [],
    })

print("Total documents collected:", len(documents))

# ==========================================
# STEP 4: SAVE PROCESSED DATA AS JSON
# ==========================================

processed_output = []

for i in range(len(documents)):
    processed_output.append({
        "document": documents[i],
        "metadata": metadatas[i]
    })

output_file = "rag_output.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(processed_output, f, indent=4, ensure_ascii=False)

print("Processed data saved to:", output_file)

# ==========================================
# STEP 5: CREATE EMBEDDINGS
# ==========================================

from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================
# STEP 6: CREATE FAISS VECTOR DATABASE
# ==========================================

from langchain_community.vectorstores import FAISS

vector_db = FAISS.from_texts(
    texts=documents,
    embedding=embeddings,
    metadatas=metadatas
)

print("Number of vectors in index:", vector_db.index.ntotal)

# ==========================================
# STEP 7: SAVE FAISS DATABASE
# ==========================================

vector_db.save_local("faiss_index")

print("FAISS index saved successfully")
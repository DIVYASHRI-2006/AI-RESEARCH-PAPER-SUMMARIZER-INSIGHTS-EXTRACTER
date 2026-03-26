from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import json
import os
import fitz  # PyMuPDF

# -----------------------------
# INITIALIZE
# -----------------------------
documents = []

# =============================
# 1. LOAD PUBMED JSON PAPERS
# =============================
if os.path.exists("papers.json"):

    with open("papers.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, paper in enumerate(data, 1):

        title = paper.get("title")
        if not title or title.strip() == "":
            title = f"Paper {i}"

        abstract = paper.get("abstract")
        if not abstract or abstract.strip() == "":
            continue

        documents.append(
            Document(
                page_content=abstract.strip(),
                metadata={
                    "title": title.strip(),
                    "source": "PubMed"
                }
            )
        )

    print(f"✅ Loaded PubMed papers: {len(data)}")

else:
    print("⚠️ papers.json not found")

# =============================
# 2. LOAD PDF FILES
# =============================
DATA_FOLDER = "Data"

if os.path.exists(DATA_FOLDER):

    for file in os.listdir(DATA_FOLDER):

        if file.endswith(".pdf"):

            path = os.path.join(DATA_FOLDER, file)

            pdf = fitz.open(path)

            text = ""

            for page in pdf:
                text += page.get_text()

            pdf.close()

            if text.strip():
                documents.append(
                    Document(
                        page_content=text.strip(),
                        metadata={
                            "title": file,   # use file name as title
                            "source": "PDF"
                        }
                    )
                )

    print("✅ Loaded PDF files")

else:
    print("⚠️ Data folder not found")

# =============================
# FINAL CHECK
# =============================
print("📚 Total documents for FAISS:", len(documents))

if len(documents) == 0:
    print("❌ No documents found. Stopping.")
    exit()

# =============================
# CREATE EMBEDDINGS
# =============================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =============================
# CREATE FAISS INDEX
# =============================
vector_db = FAISS.from_documents(documents, embeddings)

# =============================
# SAVE INDEX
# =============================
vector_db.save_local("faiss_index")

print("✅ FAISS index created successfully in 'faiss_index'")
import fitz
import re
import json
import uuid
import os
import faiss
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from helper_function import summeriser, insight_extraction
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# PATHS
# =========================
DATA_FOLDER = "Data"
OUTPUT_DIR = "parsed_output"
FAISS_DIR = "faiss_index"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)

# =========================
# LOAD MODELS
# =========================
print("Loading models...")

summ_model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(summ_model_name)
summ_model = AutoModelForSeq2SeqLM.from_pretrained(summ_model_name)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Models loaded ✅")

# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_pdf_text(pdf_path):

    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text


# =========================
# TEXT CLEANING
# =========================
def clean_text(text):

    text = text.replace("\r", "\n")
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================
# ABSTRACT EXTRACTION
# =========================
def extract_abstract(text):

    pattern = re.search(
        r'\bAbstract\b\s*(.*?)\b(?:1\.?\s*Introduction|Introduction)\b',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if pattern:
        abstract = pattern.group(1).strip()
        return re.sub(r'\s+', ' ', abstract)

    return "Abstract Not Found"


# =========================
# CONTENT EXTRACTION
# =========================
def extract_content(text, abstract):

    content = text.split(abstract, 1)[-1] if abstract in text else text

    ref_match = re.search(r'\bReferences\b', content, re.IGNORECASE)

    if ref_match:
        content = content[:ref_match.start()]

    return re.sub(r'\s+', ' ', content).strip()


# =========================
# CHUNK FUNCTION
# =========================
def split_into_chunks(text, chunk_size=500):

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


# =========================
# MAIN PIPELINE
# =========================
all_chunks = []
metadata_list = []

for file_name in os.listdir(DATA_FOLDER):

    if not file_name.lower().endswith(".pdf"):
        continue

    try:

        print(f"\nProcessing: {file_name}")

        pdf_path = os.path.join(DATA_FOLDER, file_name)

        raw_text = extract_pdf_text(pdf_path)
        cleaned_text = clean_text(raw_text)

        abstract = extract_abstract(raw_text)
        content = extract_content(cleaned_text, abstract)

        document_id = str(uuid.uuid4())

        paper_json = {
            "document_id": document_id,
            "source_file": file_name,
            "metadata": {
                "title": file_name,
                "authors": [],
                "publication_year": None,
                "created_at": datetime.utcnow().isoformat()
            },
            "abstract": abstract,
            "content": content
        }

        # =====================
        # SUMMARY
        # =====================
        print("Creating summary...")

        paper_json["summary"] = summeriser(
            content,
            tokenizer,
            summ_model
        )

        print("Summary generated ✅")

        # =====================
        # INSIGHTS
        # =====================
        paper_json["insight"] = insight_extraction(
            paper_json["summary"]
        )

        print("Insights extracted ✅")

        # =====================
        # SAVE JSON
        # =====================
        output_path = os.path.join(
            OUTPUT_DIR,
            f"{document_id}.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(paper_json, f, indent=4, ensure_ascii=False)

        print("JSON saved ✅")

        # =====================
        # CREATE CHUNKS
        # =====================
        chunks = split_into_chunks(content)

        for chunk in chunks:

            all_chunks.append(chunk)

            metadata_list.append({
                "document_id": document_id,
                "source": file_name
            })

    except Exception as e:

        print(f"Error processing {file_name}: {e}")


# =========================
# CREATE EMBEDDINGS
# =========================
print("\nCreating embeddings...")

embeddings = embedding_model.encode(all_chunks)

dimension = embeddings.shape[1]

# =========================
# STORE IN FAISS
# =========================
index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

faiss.write_index(index, "faiss_index/index.faiss")

print("FAISS index saved ✅")

# =========================
# SAVE CHUNKS
# =========================
with open("faiss_index/chunks.json", "w", encoding="utf-8") as f:

    json.dump({
        "chunks": all_chunks,
        "metadata": metadata_list
    }, f, indent=4)

print("Chunks saved ✅")

print("\nAll research papers processed successfully 🚀")
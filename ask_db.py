from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from gemini_file import ask_gemini

# Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS vector store
vector_db = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

print(f"Vector loaded: {vector_db.index.ntotal}")

# User query
user_query = "Which paper uses entropy-based evaluation?"

# Retrieval
top_k = 3
results = vector_db.similarity_search(user_query, k=top_k)

# Display results
print("\nTop Relevant Documents:\n")

content = ""

for idx, doc in enumerate(results, start=1):
    print(f"{idx}. {doc.page_content}\n")
    content += doc.page_content + "\n"

# Send to Gemini
print("-------- Gemini Response --------")

ask_gemini(content, user_query)
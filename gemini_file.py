from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_gemini(content, query):

    # Augmented Prompt
    prompt = f"""

You are a research assistant.

Use the following research paper content to answer the question.
You MUST use the content if it has relevant information.
You may rephrase and explain the answer in your own words.

Rules:
1. Prefer answers from the provided research content.
2. Mention the title of the research paper if used. 
3. If the content has no relevant information, answer using your general knowledge and write Research Paper: None.

Response format:

Answer:
<answer>

Research Paper:
<paper title or None>


Content:
{content if content else 'None'}

Question:
{query}
"""


    # Send request to Gemini model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.9
        ),
    )

    print(response.text)
    return response.text


if __name__ == "__main__":

    research_content = """
    Title: FAISS for Similarity Search
    FAISS is a library developed by Facebook AI for efficient similarity search
    and clustering of dense vectors.

    Title: Sentence Transformers
    Sentence Transformers are used to generate embeddings for semantic search.
    
    "title": "Credit Card Fraud Detection",
    "content": "Algorithms commonly used for credit card fraud detection include Decision Trees, Random Forests, Logistic Regression, Neural Networks, and Support Vector Machines (SVM). Feature engineering and anomaly detection techniques improve accuracy."
    
    
    "title": "Predicting Student Performance with Machine Learning",
    "content": "Machine learning models such as Linear Regression, Random Forest, Decision Trees, SVM, and Neural Networks can predict student performance based on previous grades, attendance, and engagement metrics."
    
    
    "title": "Recommendation Systems Techniques",
    "content": "Common techniques in recommendation systems include Collaborative Filtering, Content-Based Filtering, Hybrid Methods, Matrix Factorization, and Deep Learning-based methods."
    

    "title": "LangChain Framework",
    "content": "LangChain is a framework that helps developers build applications using large language models. It enables Retrieval Augmented Generation (RAG) pipelines by connecting LLMs with external data sources."
    """

    # User can ask any question
    while True:
        query = input("\nAsk a question about the research papers (type 'exit' to stop): ")

        if query.lower() == "exit":
            break

        ask_gemini(research_content, query)
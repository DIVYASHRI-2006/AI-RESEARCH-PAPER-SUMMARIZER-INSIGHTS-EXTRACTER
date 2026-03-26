import os
from dotenv import load_dotenv

# Gemini
from google import genai
from google.genai import types

# Groq
from groq import Groq

load_dotenv()

# ---------------- GEMINI SETUP ----------------
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- GROQ SETUP ----------------
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------------- COMMON PROMPT ----------------

def build_prompt(content, query):
    return f"""
You are an intelligent research assistant.

Your task is to answer the user's question using the provided research paper content.

Instructions:
1. Carefully analyze the given research content.
2. If relevant information is found, generate the answer strictly based on that content.
3. Clearly mention the exact research paper title(s) used.
4. If NO relevant information is found in the content:
   - Generate a helpful and accurate answer using your own knowledge.
   - In this case, write: Research Paper: None
5. Ensure the answer is clear, concise, and well-structured.
6. Do NOT hallucinate or invent research papers.
7. If multiple papers are relevant, combine insights from them.
8. The system may switch between different AI models (Gemini or Groq). 
   You must generate a consistent, high-quality answer regardless of the model used.

Output Format (STRICTLY FOLLOW):

Answer:
<your answer>

Research Paper:
<paper title(s) OR None>


-----------------------
Content:
{content if content else 'None'}

-----------------------
User Question:
{query}
"""


# ---------------- GEMINI FUNCTION ----------------
def ask_gemini(prompt):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7
        ),
    )
    return response.text


# ---------------- GROQ FUNCTION ----------------
def ask_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",   # fast + powerful
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


# ---------------- MAIN HANDLER ----------------
def ask_llm(content, query):

    prompt = build_prompt(content, query)

    try:
        print("🚀 Using Gemini...")
        return ask_gemini(prompt)

    except Exception as e:
        print("⚠ Gemini failed:", str(e))
        print("🔁 Switching to Groq...")

        try:
            return ask_groq(prompt)

        except Exception as e2:
            print("❌ Groq also failed:", str(e2))
            return "Error: Both Gemini and Groq failed to respond."
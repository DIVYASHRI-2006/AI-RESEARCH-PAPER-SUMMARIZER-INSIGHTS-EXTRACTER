import torch
import os
import json
from groq import Groq
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# DEVICE (GPU AUTO DETECT)
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# =========================
# GROQ CLIENT (LOAD ONCE)
# =========================
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")   # ✅ CORRECT WAY
)


# =========================
# TEXT CHUNKING (VERY IMPORTANT)
# =========================
def chunk_text(text, tokenizer, max_tokens=900):
    """
    Break long research papers into chunks
    to avoid BART token limit crash.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)

        tokens = tokenizer(
            " ".join(current_chunk),
            return_tensors="pt"
        ).input_ids.shape[1]

        if tokens >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# =========================
# SUMMARIZER
# =========================
def summeriser(text, tokenizer, model):

    model = model.to(device)

    print("Creating summary...")

    chunks = chunk_text(text, tokenizer)
    summaries = []

    for chunk in chunks:

        inputs = tokenizer(
            chunk,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=200,
                min_length=60,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )

        summary = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        summaries.append(summary)

    final_summary = " ".join(summaries)

    print("Summary generated ✅")
    return final_summary


# =========================
# INSIGHT EXTRACTION (GROQ)
# =========================
def insight_extraction(summary):

    prompt = f"""
Extract structured insights from the research summary below.

Return ONLY valid JSON.
No explanation.
No markdown.
No extra text.

Format:

{{
"domain": [],
"research_problem": "",
"methods": [],
"datasets": [],
"metrics": [],
"key_findings": "",
"limitations": "",
"future_directions": ""
}}

Summary:
{summary}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    print("Insights extracted ✅")

    # ------------------------
    # SAFE JSON PARSE
    # ------------------------
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        print("⚠ JSON parsing failed. Returning raw output.")
        return {"raw_output": result}
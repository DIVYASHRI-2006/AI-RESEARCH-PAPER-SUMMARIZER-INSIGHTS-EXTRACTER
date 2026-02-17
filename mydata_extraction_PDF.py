import fitz
import re
import os
import json


# -------------------------------
# Extract Text from PDF
# -------------------------------
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# -------------------------------
# Clean Text
# -------------------------------
def clean_text(text):
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


# -------------------------------
# Extract Title
# -------------------------------
def extract_title(text):
    lines = text.split("\n")

    for line in lines[:20]:
        if len(line.split()) > 5:
            return line.strip()

    return "Title Not Found"


# -------------------------------
# Extract Authors
# -------------------------------
def extract_authors(text):
    authors = re.findall(
        r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
        text[:1500]
    )
    return list(set(authors))


# -------------------------------
# Extract Abstract
# -------------------------------
# -------------------------------
# Extract Abstract (Improved)
# -------------------------------
def extract_abstract(text):

    match = re.search(
        r'Abstract[:\s]*(.*?)(?:Keywords|Index Terms|I\.|1\. Introduction)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        abstract = match.group(1)

        # remove extra spaces/newlines
        abstract = re.sub(r'\s+', ' ', abstract)

        return abstract.strip()

    return "Abstract Not Found"



# -------------------------------
# MAIN PROGRAM
# -------------------------------
pdf_folder = "Data"
results = []

# read all pdf files automatically
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

for file in pdf_files:

    pdf_path = os.path.join(pdf_folder, file)

    print(f"Processing: {file}")

    raw_text = extract_pdf_text(pdf_path)
    cleaned_text = clean_text(raw_text)

    paper_data = {
        "file_name": file,
        "title": extract_title(cleaned_text),
        "authors": extract_authors(cleaned_text),
        "abstract": extract_abstract(cleaned_text)
    }

    results.append(paper_data)


# -------------------------------
# SAVE TO JSON
# -------------------------------
with open("output.json", "w", encoding="utf-8") as json_file:
    json.dump(results, json_file, indent=4, ensure_ascii=False)

print("\n✅ Data stored successfully in output.json")

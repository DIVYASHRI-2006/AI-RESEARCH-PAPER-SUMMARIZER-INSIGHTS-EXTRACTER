import fitz
import re
import json
import uuid
import spacy
import os


#pdf text extraction
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# text cleaning
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)   
    return text.strip()


# Title extraction
def extract_title(text):
    lines = text.split("\n")
    for line in lines[:15]:
        if len(line.strip()) > 10:
            return line.strip()
    return "Unknown Title"


# author extraction
def extract_authors(text):

    abstract_match = re.search(r'\nAbstract', text, re.IGNORECASE)
    if not abstract_match:
        return []

    header_text = text[:abstract_match.start()]

    lines = [line.strip() for line in header_text.split("\n") if line.strip()]

    if len(lines) < 2:
        return []

    lines = lines[1:]   # remove title

    cleaned_lines = []
    for line in lines:
        if any(keyword in line.lower() for keyword in
               ["university", "institute", "department", "correspondence", "preprint", "@"]):
            continue
        cleaned_lines.append(line)

    author_block = " ".join(cleaned_lines)

    author_block = re.sub(r'[\*\d]', "", author_block)

    authors = re.findall(
        r'\b[A-Z][a-zA-Z\-\.]+(?:\s[A-Z][a-zA-Z\-\.]+){1,3}\b',
        author_block
    )

    seen = set()
    final_authors = []
    for name in authors:
        if name not in seen:
            seen.add(name)
            final_authors.append(name)

    return final_authors


# abstract extraction
def extract_abstract(text):

    text = text.replace('\r', '\n')

    pattern = re.search(
        r'\bAbstract\b\s*\n(.*?)\n\s*(?:\d+\.\s*Introduction|Introduction)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if pattern:
        abstract = pattern.group(1).strip()
        abstract = re.sub(r'\n+', ' ', abstract)
        abstract = re.sub(r'\s+', ' ', abstract)
        return abstract

    return "Abstract Not Found"


# main function
if __name__ == "__main__":

    pdf_file = r"Data\Machine Learning .pdf"  # check path carefully
    output_dir = "parsed_output"
    os.makedirs(output_dir, exist_ok=True)

    raw_text = extract_pdf_text(pdf_file)
    cleaned_text = clean_text(raw_text)

    print("\n TITLE:")
    print(extract_title(raw_text))

    print("\n AUTHORS: ")
    print(extract_authors(raw_text))

    print("\n ABSTRACT: ")
    print(extract_abstract(raw_text)[:1000])

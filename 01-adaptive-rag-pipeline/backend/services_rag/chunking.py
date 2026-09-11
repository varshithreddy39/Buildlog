import pdfplumber
import io 
import re
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_content: bytes) -> str:

    try:

        text = ""

        with pdfplumber.open(io.BytesIO(file_content)) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:

                    text += page_text + "\n\n"

        return text.strip()

    except Exception as e:

        print(f"Error extracting text: {e}")

        return ""


def clean_text(text: str) -> str:
    text=text.lower()

    # normalize spaces
    text = text.replace("\t", " ")

    # preserve paragraph breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # remove extra spaces
    text = re.sub(r' +', ' ', text)

    # remove weird characters
    text = re.sub(
        r'[^a-zA-Z0-9.,!?;:()\-_\n\s/%=#\[\]{}+]',
        '',
        text
    )

    return text.strip()

def langchain_chunking(text: str) -> list:

    text_lenght = len(text)
    if text_lenght<5000:
        chunk_size=150
        chunk_overlap=30
    elif text_lenght<20000:
        chunk_size=300
        chunk_overlap=50
    else:
        chunk_size=500
        chunk_overlap=100

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_text(text)

    print("\n===== RETRIEVED CHUNKS =====")



    return chunks



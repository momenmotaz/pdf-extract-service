import fitz  # PyMuPDF
import pdfplumber
import io
import re
import unicodedata


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text extracted from PDFs for clean storage and RAG search.
    
    - NFKC normalization converts Arabic Presentation Forms (U+FB50-FDFF, U+FE70-FEFF)
      back to standard Arabic characters (U+0600-U+06FF)
    - Removes tatweel (kashida) elongation characters
    - Strips diacritics (tashkeel) which add noise for search/RAG
    """
    has_arabic = any(
        '\u0600' <= ch <= '\u06FF' or '\uFB50' <= ch <= '\uFDFF' or '\uFE70' <= ch <= '\uFEFF'
        for ch in text
    )
    if not has_arabic:
        return text
    # NFKC decomposes Arabic Presentation Forms → standard Arabic
    text = unicodedata.normalize('NFKC', text)
    # Remove tatweel (kashida) elongation character
    text = text.replace('\u0640', '')
    # Remove Arabic diacritics (tashkeel) — noisy for RAG
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    return text


def extract_with_pymupdf(content: bytes) -> dict:
    full_text = ""
    pages_data = []

    doc = fitz.open(stream=content, filetype="pdf")
    page_count = len(doc)

    for page_num in range(page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks", sort=True)
        page_text = ""
        for b in blocks:
            if b[6] == 0:  # text block
                page_text += b[4] + "\n"

        page_text = normalize_arabic(page_text)
        full_text += page_text + "\n"
        pages_data.append({
            "page_number": page_num + 1,
            "text": page_text.strip(),
            "tables": []
        })

    doc.close()
    return {"text": full_text, "pages": pages_data, "page_count": page_count}


def extract_with_pdfplumber(content: bytes) -> dict:
    full_text = ""
    pages_data = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        page_count = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            page_text = normalize_arabic(page_text)
            full_text += page_text + "\n"
            pages_data.append({
                "page_number": i + 1,
                "text": page_text.strip(),
                "tables": []
            })

    return {"text": full_text, "pages": pages_data, "page_count": page_count}

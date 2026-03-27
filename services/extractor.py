import fitz  # PyMuPDF
import pdfplumber
import io
import unicodedata

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text extracted from PDFs.
    
    PDFs often store Arabic in 'Presentation Forms' (legacy Unicode block U+FE70–U+FEFF)
    which renders incorrectly in browsers. This converts them to proper Arabic Unicode
    (U+0600–U+06FF) using arabic_reshaper, then fixes RTL ordering with python-bidi.
    """
    if not ARABIC_SUPPORT:
        return text
    
    # Check if text contains Arabic Presentation Forms or Arabic characters
    has_arabic = any(
        '\u0600' <= ch <= '\u06FF' or '\uFE70' <= ch <= '\uFEFF'
        for ch in text
    )
    
    if not has_arabic:
        return text
    
    # Normalize unicode (NFC) to convert Presentation Forms to base forms
    text = unicodedata.normalize('NFC', text)
    
    lines = text.split('\n')
    normalized_lines = []
    
    for line in lines:
        line_has_arabic = any(
            '\u0600' <= ch <= '\u06FF' or '\uFE70' <= ch <= '\uFEFF'
            for ch in line
        )
        if line_has_arabic and line.strip():
            reshaped = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped)
            normalized_lines.append(bidi_text)
        else:
            normalized_lines.append(line)
    
    return '\n'.join(normalized_lines)


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


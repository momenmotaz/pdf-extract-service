import fitz # PyMuPDF
import pdfplumber
import io

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
            if b[6] == 0: # text block
                page_text += b[4] + "\n"
        
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
            full_text += page_text + "\n"
            pages_data.append({
                "page_number": i + 1,
                "text": page_text.strip(),
                "tables": []
            })
            
    return {"text": full_text, "pages": pages_data, "page_count": page_count}

import fitz
import time

from services.extractor import extract_with_pymupdf, extract_with_pdfplumber
from services.ocr_service import extract_with_ocr
from services.table_service import extract_tables
from utils.helpers import validate_text, clean_text

def process_document(content: bytes, filename: str) -> dict:
    start_time = time.time()
    
    # 1. Quick check if it's encrypted
    doc = fitz.open(stream=content, filetype="pdf")
    page_count = len(doc)
    is_encrypted = doc.is_encrypted
    doc.close()
    
    if is_encrypted:
        raise ValueError("PDF is password protected. Please unlock the PDF first.")
        
    if page_count == 0:
        raise ValueError("No pages found in PDF.")
        
    method_used = "pymupdf"
    warning = None
    
    # 2. Try fast text-based extraction
    res = extract_with_pymupdf(content)
    validation = validate_text(res["text"])
    
    # If standard text extraction yields minimal data
    if not validation["is_valid"]:
        if len(res["text"].strip()) < 50:
            # Highly likely a scanned image, attempt OCR pipeline
            try:
                ocr_res = extract_with_ocr(content)
                ocr_validation = validate_text(ocr_res["text"])
                if ocr_validation["is_valid"] or len(ocr_res["text"].strip()) > 50:
                    res = ocr_res
                    method_used = "ocr"
                    validation = ocr_validation
            except Exception as e:
                warning = f"OCR failed on fallback: {str(e)}"
        else:
            # Layout might be overlapping, attempt pdfplumber
            res = extract_with_pdfplumber(content)
            method_used = "pdfplumber"
            validation = validate_text(res["text"])
            if not validation["is_valid"]:
                warning = validation["reason"]
                
    # 3. Clean all texts strictly
    clean_full_text = clean_text(res["text"])
    for p in res["pages"]:
        p["text"] = clean_text(p["text"])
        
    # 4. Attempt table extraction overhead isolated
    tables = extract_tables(content)
    
    # Attach matched tables locally to logical pages
    for page in res["pages"]:
        page_num = page["page_number"]
        page["tables"] = [t["data"] for t in tables if int(t["page"]) == page_num]
        
    processing_time = int((time.time() - start_time) * 1000)
    
    response = {
        "success": True,
        "text": clean_full_text,
        "pageCount": page_count,
        "method": method_used,
        "warning": warning,
        "pages": res["pages"],
        "tables": tables,
        "metadata": {
            "file_name": filename,
            "total_pages": page_count,
            "extraction_methods_used": [method_used] if not tables else [method_used, "camelot"],
            "processing_time_ms": processing_time
        }
    }
    
    # Free memory buffer explicitly
    content = None 
    return response

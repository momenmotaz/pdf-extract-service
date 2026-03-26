import fitz
import cv2
import numpy as np
import io
import traceback

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def extract_with_ocr(content: bytes) -> dict:
    
    if not TESSERACT_AVAILABLE:
        raise RuntimeError("Tesseract library is not installed in Python.")
        
    full_text = ""
    pages_data = []
    
    doc = fitz.open(stream=content, filetype="pdf")
    page_count = len(doc)
    
    for page_num in range(page_count):
        page = doc.load_page(page_num)
        # 300 DPI for reliable OCR readability
        pix = page.get_pixmap(dpi=300)
        
        # Determine color space and convert to grayscale directly in numpy limits
        if pix.n == 4:
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 4)
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
        elif pix.n == 3:
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
            gray = img_np
            
        # Optional: Apply thresholding to clean noise from scanned pages
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        try:
            # Attempt to use Arabic and English model combo
            text = pytesseract.image_to_string(thresh, lang='ara+eng')
        except Exception:
            try:
                # Fallback to English if Ara is missing in system data
                text = pytesseract.image_to_string(thresh, lang='eng')
            except Exception as e:
                text = ""
                print(f"OCR Failure on page {page_num}: {e}")
                
        full_text += text + "\n"
        pages_data.append({
            "page_number": page_num + 1,
            "text": text.strip(),
            "tables": []
        })
        
        # Free memory aggressively inside loop
        pix = None
        img_np = None
        gray = None
        thresh = None
        
    doc.close()
    return {"text": full_text, "pages": pages_data, "page_count": page_count}

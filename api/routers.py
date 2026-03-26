from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pipeline import process_document
import gc

router = APIRouter()

@router.post("/extract-pdf")
async def extract_pdf_endpoint(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")
        
    try:
        # Stream file safely
        content = await file.read()
        
        # Verify magic number manually for safety
        if len(content) < 5 or not content.startswith(b'%PDF-'):
            raise HTTPException(status_code=400, detail="Invalid PDF file format. Missing magic number.")
            
        result = process_document(content, filename=file.filename)
        
        # Force garbage collection to keep the low server memory clear
        del content
        gc.collect()
        
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "production-pdf-extractor"}

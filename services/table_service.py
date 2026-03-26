import tempfile
import os

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

def extract_tables(content: bytes) -> list:
    if not CAMELOT_AVAILABLE:
        print("Camelot is not available. Skipping table extraction.")
        return []
        
    tables_data = []
    
    # Camelot requires physical files on the OS, utilizing a secure Temp File
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
            
        # Try finding complex bordered tables (lattice)
        tables = camelot.read_pdf(tmp_path, pages='all', flavor='lattice')
        
        # Fallback to gap-based (stream) if lattice found nothing
        if len(tables) == 0:
            tables = camelot.read_pdf(tmp_path, pages='all', flavor='stream')
            
        for t in tables:
            tables_data.append({
                "page": t.page,
                "data": t.df.values.tolist()
            })
            
    except Exception as e:
        print(f"Table Extraction Engine skipping due to OS error: {e}")
        # Ghostscript likely not found in system variables
        pass
    finally:
        # Guarantee RAM/Disk un-blocking
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
    return tables_data

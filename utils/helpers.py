import re

MIN_READABLE_RATIO = 0.5
READABLE_CHARS_REGEX = re.compile(
    r'[\x20-\x7E\n\r\t\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]'
)

def validate_text(text: str) -> dict:
    if not text or len(text.strip()) == 0:
        return {"is_valid": False, "reason": "No text extracted from PDF"}

    if len(text.strip()) < 20:
        return {"is_valid": False, "reason": "Extracted text is too short (minimum 20 characters)"}

    total_checked = 0
    readable_count = 0
    
    for char in text:
        if not char.isspace():
            total_checked += 1
            if READABLE_CHARS_REGEX.match(char):
                readable_count += 1
                
    readable_ratio = readable_count / total_checked if total_checked > 0 else 0
    
    if readable_ratio < MIN_READABLE_RATIO:
        return {
            "is_valid": False,
            "reason": f"Text appears corrupted (readable: {readable_ratio * 100:.1f}%, minimum: {MIN_READABLE_RATIO * 100}%)",
            "readable_ratio": readable_ratio
        }
        
    return {"is_valid": True, "readable_ratio": readable_ratio}

def clean_text(text: str) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()

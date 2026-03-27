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
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove control characters (keep newlines/tabs)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Collapse multiple spaces/tabs into one
    text = re.sub(r'[ \t]+', ' ', text)

    # Split into lines and strip each
    lines = [line.strip() for line in text.split('\n')]

    # Remove standalone page-number lines (lone integers, e.g. "7", "12", "63")
    lines = [line for line in lines if not re.fullmatch(r'\d{1,3}', line)]

    # Remove consecutive duplicate lines (common artifact in RTL/bidi PDFs extracted by PyMuPDF)
    deduped = []
    prev = None
    for line in lines:
        if line != prev:
            deduped.append(line)
        prev = line

    # Collapse more than 1 consecutive blank line into a single blank line
    cleaned = []
    blank_count = 0
    for line in deduped:
        if line == '':
            blank_count += 1
            if blank_count <= 1:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)

    return '\n'.join(cleaned).strip()

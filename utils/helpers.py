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
    """
    Thoroughly clean extracted PDF text:
    - Normalize line endings and whitespace
    - Remove control characters
    - Remove standalone page numbers
    - Remove consecutive duplicate lines (common in Arabic/RTL PDF extraction)
    - Collapse excessive blank lines
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove control characters (keep newlines/tabs)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Collapse multiple spaces/tabs into one
    text = re.sub(r'[ \t]+', ' ', text)

    # Split into lines and strip each
    lines = [line.strip() for line in text.split('\n')]

    # Remove standalone page-number lines (lone integers, e.g. "7", "12", "63")
    lines = [line for line in lines if not re.fullmatch(r'\d{1,4}', line)]

    # Remove consecutive duplicate lines (normalize for comparison)
    deduped = []
    prev_normalized = None
    for line in lines:
        # Normalize: lowercase, collapse whitespace, strip for comparison
        normalized = re.sub(r'\s+', '', line).lower()
        if normalized == '' or normalized != prev_normalized:
            deduped.append(line)
        prev_normalized = normalized

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

    # Merge consecutive non-empty lines into paragraphs
    # A blank line separates paragraphs
    paragraphs = []
    current_para = []
    for line in cleaned:
        if line == '':
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
            paragraphs.append('')  # keep blank line as paragraph separator
        else:
            current_para.append(line)
    if current_para:
        paragraphs.append(' '.join(current_para))

    # Final collapse: remove consecutive blank lines again after merge
    final = []
    prev_blank = False
    for p in paragraphs:
        if p == '':
            if not prev_blank:
                final.append(p)
            prev_blank = True
        else:
            prev_blank = False
            final.append(p)

    return '\n'.join(final).strip()

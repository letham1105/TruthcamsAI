import re


NOISE_PATTERNS = [
    # Social media timestamps
    r"^\s*\d{1,2}\s+tháng\s+\d{1,2}\s+lúc\s+.*$",

    # Websites
    r"^\s*[\w.-]+\.(vn|com|net|org)\s*$",

    # Social media UI
    r"^\s*(like|comment|share|follow|subscribe)\s*$",
    r"^\s*(see more|read more|view more|đọc thêm|xem thêm)\s*$",

    # Standalone symbols
    r"^\s*[®©™]+\s*$",
    r"^\s*[\W_]{1,5}\s*$",
]


def is_noise_line(line: str) -> bool:
    line = line.strip()

    if not line:
        return True

    # Match known noise patterns
    if any(
        re.match(pattern, line, re.IGNORECASE)
        for pattern in NOISE_PATTERNS
    ):
        return True

    # Remove very short lines
    if len(line) <= 2:
        return True

    # Extract meaningful tokens
    tokens = re.findall(r"\b[\wÀ-ỹ]+\b", line)

    # Remove short OCR fragments with very few meaningful words
    if len(tokens) <= 4 and len(line) < 40:
        meaningful_tokens = [
            token for token in tokens
            if len(token) > 3
        ]

        if len(meaningful_tokens) <= 1:
            return True

    # Remove lines dominated by non-alphanumeric symbols
    alphanumeric_count = sum(
        char.isalnum() for char in line
    )

    if len(line) >= 4:
        ratio = alphanumeric_count / len(line)

        if ratio < 0.35:
            return True

    return False


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""

    # Normalize line breaks and whitespace
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    cleaned_lines = []

    for line in text.split("\n"):
        line = line.strip()

        if is_noise_line(line):
            continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    # Remove repeated blank lines
    cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text)

    return cleaned_text.strip()
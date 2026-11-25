import re

BOILERPLATE_PATTERNS = [
    r"^đọc thêm[:：]?\s*$",
    r"^xem thêm[:：]?\s*$",
    r"^theo dõi chúng tôi[:：]?.*$",
    r"^bài viết liên quan[:：]?.*$",
    r"^quảng cáo[:：]?.*$",
]

def clean_article(article):
    cleaned = dict(article)
    raw = article.get("raw_content") or article.get("content") or ""
    raw_paragraphs = re.split(r"\n\s*\n+", raw.replace("\r", "\n"))
    output, seen = [], set()

    for paragraph in raw_paragraphs:
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()
        paragraph = re.sub(r"\n+", " ", paragraph)
        if not paragraph:
            continue
        normalized = paragraph.casefold()
        if any(re.match(pattern, normalized, flags=re.I) for pattern in BOILERPLATE_PATTERNS):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        output.append(paragraph)

    cleaned["raw_content"] = raw
    cleaned["cleaned_content"] = "\n\n".join(output)
    cleaned["content"] = cleaned["cleaned_content"]
    return cleaned

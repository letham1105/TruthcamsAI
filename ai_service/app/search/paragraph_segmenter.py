import re
from ai_service.app.utils.text_utils import clean_text, stable_article_id

def segment_article(article, min_chars=80, max_chars=1800):
    content = article.get("cleaned_content") or article.get("content") or ""
    if not content.strip():
        return []

    blocks = [b.strip() for b in re.split(r"\n\s*\n+", content) if b.strip()]
    if len(blocks) == 1 and len(blocks[0]) > max_chars:
        sentences = re.split(r"(?<=[.!?。！？])\s+", blocks[0])
        blocks, current = [], ""
        for sentence in sentences:
            if current and len(current) + len(sentence) + 1 > max_chars:
                blocks.append(current.strip())
                current = sentence
            else:
                current = (current + " " + sentence).strip()
        if current:
            blocks.append(current.strip())

    paragraphs, pending = [], ""
    for block in blocks:
        block = clean_text(block)
        if not block:
            continue
        if pending:
            block = pending + " " + block
            pending = ""
        if len(block) < min_chars:
            pending = block
            continue
        paragraphs.append({"paragraph_text": block})

    if pending:
        if paragraphs:
            paragraphs[-1]["paragraph_text"] += " " + pending
        elif len(pending) >= 20:
            paragraphs.append({"paragraph_text": pending})

    article_id = article.get("article_id") or stable_article_id(article.get("url", "unknown"))
    claim_ids = article.get("claim_ids", [])
    output = []
    for index, item in enumerate(paragraphs, start=1):
        output.append({
            "article_id": article_id,
            "paragraph_id": f"{article_id}_P{index:02d}",
            "claim_ids": list(claim_ids),
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "url": article.get("final_url") or article.get("url", ""),
            "published_at": article.get("published_at"),
            "paragraph_text": item["paragraph_text"],
        })
    return output

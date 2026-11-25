import re
import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
except ImportError:
    trafilatura = None

from ai_service.app.config import REQUEST_TIMEOUT, USER_AGENT
from ai_service.app.utils.text_utils import clean_text, safe_error, stable_article_id
from ai_service.app.utils.url_utils import normalize_url, is_http_url

def extract_article(url, search_result=None, timeout=REQUEST_TIMEOUT):
    search_result = search_result or {}
    article = {
        "article_id": stable_article_id(normalize_url(url) or str(url)),
        "url": url,
        "final_url": None,
        "title": clean_text(search_result.get("title")),
        "source": clean_text(search_result.get("source")),
        "published_at": search_result.get("published_at"),
        "author": None,
        "content": "",
        "raw_content": "",
        "claim_ids": list(
            search_result.get("claim_ids", []) or
            ([search_result.get("claim_id")] if search_result.get("claim_id") else [])
        ),
        "query_associations": list(search_result.get("query_associations", [])),
        "extraction_status": "failed",
        "error": None,
    }

    if not is_http_url(url):
        article["error"] = "Invalid HTTP/HTTPS URL."
        return article

    try:
        response = requests.get(
            url, headers={"User-Agent": USER_AGENT},
            timeout=timeout, allow_redirects=True
        )
        response.raise_for_status()
        article["final_url"] = response.url
        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type and "text/" not in content_type:
            article["error"] = f"Unsupported content type: {content_type or 'unknown'}"
            return article

        html = response.text
        soup = BeautifulSoup(html, "lxml")
        if not article["title"]:
            article["title"] = clean_text(
                soup.title.get_text(" ", strip=True) if soup.title else ""
            )
        author_meta = (
            soup.find("meta", attrs={"name": re.compile("author", re.I)})
            or soup.find("meta", attrs={"property": "article:author"})
        )
        if author_meta:
            article["author"] = author_meta.get("content")
        date_meta = (
            soup.find("meta", attrs={"property": "article:published_time"})
            or soup.find("meta", attrs={"name": re.compile("date", re.I)})
        )
        if not article["published_at"] and date_meta:
            article["published_at"] = date_meta.get("content")

        content = ""
        if trafilatura is not None:
            content = trafilatura.extract(
                html, include_comments=False, include_tables=True
            ) or ""
        if not content:
            for tag in soup([
                "script", "style", "nav", "footer", "header",
                "aside", "form", "noscript"
            ]):
                tag.decompose()
            main = soup.find("article") or soup.find("main") or soup.body or soup
            blocks = [
                clean_text(node.get_text(" ", strip=True))
                for node in main.find_all(["h1", "h2", "h3", "p", "li"])
            ]
            content = "\n\n".join(block for block in blocks if block)

        article["raw_content"] = content.strip()
        article["content"] = article["raw_content"]
        article["extraction_status"] = (
            "success" if len(article["content"]) >= 200
            else ("partial" if article["content"] else "failed")
        )
        if not article["content"]:
            article["error"] = "No article body extracted."
    except Exception as exc:
        article["error"] = safe_error(exc)
    return article

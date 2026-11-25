import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from ai_service.app.config import REQUEST_TIMEOUT, GOOGLE_NEWS_MAX_RESULTS, USER_AGENT
from ai_service.app.utils.text_utils import clean_text, safe_error
from ai_service.app.utils.logging_config import get_logger

logger = get_logger(__name__)

def search_google_news(query, max_results=10, timeout=REQUEST_TIMEOUT):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")
    if max_results < 1:
        raise ValueError("max_results must be >= 1")

    rss_url = (
        "https://news.google.com/rss/search?q=" + quote_plus(query.strip())
        + "&hl=vi&gl=VN&ceid=VN:vi"
    )
    response = requests.get(
        rss_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
    )
    response.raise_for_status()

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise ValueError(f"Malformed Google News RSS: {exc}") from exc

    results = []
    for item in root.findall(".//item")[:max_results]:
        title = clean_text(item.findtext("title", default=""))
        link = clean_text(item.findtext("link", default=""))
        published_at = clean_text(item.findtext("pubDate", default=""))
        description = item.findtext("description", default="") or ""
        snippet = clean_text(
            BeautifulSoup(description, "html.parser").get_text(" ", strip=True)
        )
        source_element = item.find("source")
        source = clean_text(source_element.text if source_element is not None else "")
        results.append({
            "title": title, "source": source, "published_at": published_at,
            "snippet": snippet, "url": link,
        })
    return results

def search_all_queries(prepared_queries, max_results=GOOGLE_NEWS_MAX_RESULTS):
    all_results, errors = [], []
    for item in prepared_queries:
        try:
            rows = search_google_news(item["query"], max_results=max_results)
            for row in rows:
                all_results.append({
                    **row,
                    "claim_id": item["claim_id"],
                    "search_query": item["query"],
                })
            logger.info("RSS query %s returned %d results", item["claim_id"], len(rows))
        except Exception as exc:
            errors.append({
                "stage": "google_news_search",
                "claim_id": item["claim_id"],
                "query": item["query"],
                "error": safe_error(exc),
            })
            logger.warning("RSS query failed (%s): %s", item["query"], exc)
    return all_results, errors

from urllib.parse import urlparse
from gnews_decoder import decode_many

from ai_service.app.utils.logging_config import get_logger

logger = get_logger(__name__)

def resolve_google_news_urls(search_results, concurrency=4, timeout=20):
    """Resolve Google News RSS URLs into original publisher URLs."""
    google_urls = list(dict.fromkeys(
        item.get("url")
        for item in search_results
        if item.get("url")
        and urlparse(item["url"]).hostname == "news.google.com"
    ))
    if not google_urls:
        return {}
    try:
        return decode_many(
            google_urls, concurrency=concurrency, timeout=timeout
        )
    except Exception as exc:
        logger.warning("Google News URL resolution failed: %s", exc)
        return {url: None for url in google_urls}

import requests
from bs4 import BeautifulSoup

from ai_service.app.config import REQUEST_TIMEOUT, USER_AGENT
from ai_service.app.utils.text_utils import clean_text, safe_error
from ai_service.app.utils.url_utils import is_http_url
from ai_service.app.utils.logging_config import get_logger

logger = get_logger(__name__)

try:
    import trafilatura
except ImportError:
    trafilatura = None


def extract_text_from_url(url, timeout=REQUEST_TIMEOUT):
    result = {
        "title": "",
        "text": "",
        "final_url": url,
        "status": "failed",
        "error": None,
    }

    if not is_http_url(url):
        result["error"] = "Invalid HTTP/HTTPS URL."
        return result

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            allow_redirects=True,
        )
        response.raise_for_status()

        result["final_url"] = response.url

        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type and "text/" not in content_type:
            result["error"] = (
                f"Unsupported content type: {content_type or 'unknown'}"
            )
            return result

        html = response.text
        soup = BeautifulSoup(html, "lxml")

        # 1. Extract title
        result["title"] = clean_text(
            soup.title.get_text(" ", strip=True) if soup.title else ""
        )

        # 2. Extract main text using Trafilatura
        extracted = ""

        if trafilatura is not None:
            extracted = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
            ) or ""

        # 3. BeautifulSoup fallback
        if not extracted.strip():
            fallback_soup = BeautifulSoup(html, "lxml")

            for tag in fallback_soup(
                ["script", "style", "nav", "footer", "header",
                 "aside", "form"]
            ):
                tag.decompose()

            main = (
                fallback_soup.find("article")
                or fallback_soup.find("main")
                or fallback_soup.body
                or fallback_soup
            )

            extracted = "\n\n".join(
                clean_text(p.get_text(" ", strip=True))
                for p in main.find_all(["p", "h1", "h2", "h3", "li"])
                if clean_text(p.get_text(" ", strip=True))
            )

        extracted = extracted.strip()

        # 4. Metadata fallback
        # Used only when main-text extraction fails.
        if not extracted:
            metadata_description = ""

            for attrs in [
                {"property": "og:description"},
                {"name": "description"},
                {"name": "twitter:description"},
            ]:
                meta = soup.find("meta", attrs=attrs)

                if meta and meta.get("content"):
                    candidate = clean_text(meta["content"])

                    if candidate:
                        metadata_description = candidate
                        break

            if metadata_description:
                extracted = metadata_description
                result["metadata_fallback"] = True
                logger.info("URL extraction used metadata description fallback")

        result["text"] = extracted

        if result["text"]:
            result["status"] = "success"
            result["error"] = None
        else:
            result["status"] = "partial"
            result["error"] = (
                "Page was accessible but no main text or usable "
                "metadata description could be extracted."
            )

    except Exception as exc:
        result["error"] = safe_error(exc)
        logger.warning("URL extraction failed: %s", result["error"])

    return result
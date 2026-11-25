import re
import hashlib
import json

def clean_text(value):
    """Normalize whitespace without changing the meaning of the text."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()

def safe_error(exc):
    return f"{type(exc).__name__}: {exc}"

def stable_article_id(url):
    return "A_" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]

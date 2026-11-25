from ai_service.app.utils.text_utils import clean_text
from ai_service.app.utils.url_utils import normalize_url, is_http_url

def normalize_search_results(results):
    normalized = []
    for row in results or []:
        if not isinstance(row, dict):
            continue
        claim_id = row.get("claim_id")
        search_query = clean_text(row.get("search_query"))
        normalized.append({
            "claim_id": claim_id,
            "search_query": search_query,
            "title": clean_text(row.get("title")),
            "source": clean_text(row.get("source")),
            "published_at": clean_text(row.get("published_at")) or None,
            "snippet": clean_text(row.get("snippet")),
            "url": clean_text(row.get("url")),
            "claim_ids": [claim_id] if claim_id else [],
            "query_associations": (
                [{"claim_id": claim_id, "query": search_query}] if claim_id else []
            ),
        })
    return normalized

def deduplicate_results(results):
    deduplicated = {}
    for row in results or []:
        canonical = normalize_url(row.get("url", ""))
        if not canonical:
            continue
        if canonical not in deduplicated:
            item = dict(row)
            item["url"] = canonical
            item["claim_ids"] = list(dict.fromkeys(
                item.get("claim_ids", []) or
                ([item.get("claim_id")] if item.get("claim_id") else [])
            ))
            item["query_associations"] = list(item.get("query_associations", []))
            deduplicated[canonical] = item
        else:
            current = deduplicated[canonical]
            for claim_id in row.get("claim_ids", []) or (
                [row.get("claim_id")] if row.get("claim_id") else []
            ):
                if claim_id and claim_id not in current["claim_ids"]:
                    current["claim_ids"].append(claim_id)
            association = {
                "claim_id": row.get("claim_id"),
                "query": row.get("search_query", ""),
            }
            if association not in current["query_associations"]:
                current["query_associations"].append(association)
            for field in ("title", "source", "published_at", "snippet"):
                if not current.get(field) and row.get(field):
                    current[field] = row[field]
    return list(deduplicated.values())

def filter_search_results(results):
    """Conservative structural filtering; not semantic truth assessment."""
    kept, rejected = [], []
    for row in results or []:
        reason = None
        if not is_http_url(row.get("url", "")):
            reason = "missing_or_invalid_url"
        elif len(clean_text(row.get("title"))) < 4:
            reason = "missing_meaningful_title"
        if reason:
            rejected.append({"result": row, "reason": reason})
        else:
            kept.append(row)
    return kept, rejected

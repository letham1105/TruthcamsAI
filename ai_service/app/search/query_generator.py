from ai_service.app.utils.text_utils import clean_text

def prepare_search_queries(claims):
    """Flatten per-claim search_queries while preserving claim-query relationships."""
    if isinstance(claims, dict):
        claims = claims.get("claims", [])
    if not isinstance(claims, list):
        raise TypeError("claims must be a list or claim-extraction dictionary.")

    prepared, seen = [], set()
    for index, claim in enumerate(claims, start=1):
        claim_id = claim.get("claim_id") or f"C{index}"
        claim_text = clean_text(claim.get("claim_text"))
        queries = claim.get("search_queries", [])
        if not claim_text or not isinstance(queries, list):
            continue
        local_seen = set()
        query_index = 0
        for query in queries:
            query = clean_text(query)
            normalized = query.casefold()
            if not query or normalized in local_seen:
                continue
            local_seen.add(normalized)
            query_index += 1
            key = (claim_id, normalized)
            if key in seen:
                continue
            seen.add(key)
            prepared.append({
                "claim_id": claim_id,
                "claim_text": claim_text,
                "query": query,
                "query_index": query_index,
            })
    return prepared

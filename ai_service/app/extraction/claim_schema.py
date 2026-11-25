import logging

LOGGER = logging.getLogger(__name__)

def validate_claims_schema(data, original_text=None):
    """Validate required claim fields; reject malformed output instead of inventing data."""
    if not isinstance(data, dict):
        raise TypeError("Claim extraction output must be a dictionary.")
    if not isinstance(data.get("claims"), list):
        raise ValueError("Output must contain a 'claims' list.")
    if original_text is not None and data.get("original_text") != original_text:
        LOGGER.warning("Model original_text differs from input; preserving actual input.")
        data["original_text"] = original_text

    allowed_types = {"factual_event", "approval", "proposal_status", "prediction", "announcement"}
    allowed_entity_types = {"PERSON", "ORGANIZATION", "LOCATION", "OTHER"}
    temporal_fields = [
        "announcement_date", "approval_date", "event_date",
        "expected_completion_date"
    ]

    for index, claim in enumerate(data["claims"], start=1):
        if not isinstance(claim, dict):
            raise ValueError(f"Claim at index {index - 1} is not an object.")
        for field in ("claim_text", "claim_type", "entities", "temporal", "search_queries"):
            if field not in claim:
                raise ValueError(f"Claim {index} is missing field: {field}")
        if not isinstance(claim["claim_text"], str) or not claim["claim_text"].strip():
            raise ValueError(f"Claim {index} has empty claim_text.")
        if claim["claim_type"] not in allowed_types:
            raise ValueError(f"Claim {index} has unsupported claim_type: {claim['claim_type']}")
        if not isinstance(claim["entities"], list) or not isinstance(claim["temporal"], dict):
            raise ValueError(f"Claim {index}: entities/temporal have invalid types.")
        for field in temporal_fields:
            claim["temporal"].setdefault(field, None)
        for entity in claim["entities"]:
            if (
                not isinstance(entity, dict)
                or entity.get("type") not in allowed_entity_types
                or not entity.get("name")
            ):
                raise ValueError(f"Claim {index} contains an invalid entity.")
        if not isinstance(claim["search_queries"], list):
            raise ValueError(f"Claim {index}: search_queries must be a list.")
        claim["search_queries"] = [
            q.strip() for q in claim["search_queries"]
            if isinstance(q, str) and q.strip()
        ][:3]
        claim["claim_id"] = f"C{index}"

    data.setdefault("original_text", original_text or "")
    return data

from ai_service.app.verification.verifier import verify_pair


def verify_retrieved_evidence(bm25_results):
    """
    Verify each retrieved evidence paragraph against its claim.

    Input:
        BM25 results grouped by claim.

    Output:
        BM25 results enriched with verification results.
    """

    verified_results = []

    for item in bm25_results or []:
        claim_id = item.get("claim_id")
        claim_text = item.get("claim_text", "")
        evidences = item.get("evidence", [])

        verified_evidences = []

        for evidence in evidences:
            paragraph_text = evidence.get("paragraph_text", "")

            if not claim_text.strip() or not paragraph_text.strip():
                continue

            verification = verify_pair(
                claim=claim_text,
                evidence=paragraph_text,
            )

            evidence_result = {
                **evidence,
                "verification": verification.model_dump(),
            }

            verified_evidences.append(evidence_result)

        verified_results.append({
            "claim_id": claim_id,
            "claim_text": claim_text,
            "evidence": verified_evidences,
        })

    return verified_results

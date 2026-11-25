from ai_service.app.verification.verifier import verify_pair


def _get_relevant_sentences(evidence):
    """Extract relevant sentences with their relevance metadata."""

    relevant_sentences = evidence.get("relevant_sentences")

    if relevant_sentences is None:
        relevant_sentences = evidence.get("sentence_relevance", [])

    if not isinstance(relevant_sentences, list):
        return []

    sentences = []

    for item in relevant_sentences:
        if isinstance(item, str):
            sentence_text = item
            relevance_score = None

        elif isinstance(item, dict):
            sentence_text = (
                item.get("sentence_text")
                or item.get("text")
                or item.get("sentence")
                or ""
            )

            relevance_score = item.get("relevance_score")

        else:
            continue

        sentence_text = sentence_text.strip()

        if not sentence_text:
            continue

        sentences.append({
            "sentence_text": sentence_text,
            "relevance_score": relevance_score,
        })

    return sentences


def verify_retrieved_evidence(bm25_results):
    """Verify relevant sentences against their corresponding claims."""

    verified_results = []

    for item in bm25_results or []:

        claim_id = item.get("claim_id")
        claim_text = item.get("claim_text", "")
        evidences = item.get("evidence", []) or []

        verified_evidences = []

        for evidence in evidences:

            if not claim_text.strip():
                continue

            relevant_sentences = _get_relevant_sentences(evidence)

            if not relevant_sentences:
                continue

            sentence_verifications = []

            for sentence in relevant_sentences:

                sentence_text = sentence["sentence_text"]

                verification = verify_pair(
                    claim=claim_text,
                    evidence=sentence_text,
                )

                sentence_verifications.append({
                    "sentence_text": sentence_text,
                    "relevance_score": sentence.get(
                        "relevance_score"
                    ),
                    "verification": verification.model_dump(),
                })

            evidence_result = {
                **evidence,
                "sentence_verifications": sentence_verifications,
            }

            verified_evidences.append(evidence_result)

        verified_results.append({
            "claim_id": claim_id,
            "claim_text": claim_text,
            "evidence": verified_evidences,
        })

    return verified_results
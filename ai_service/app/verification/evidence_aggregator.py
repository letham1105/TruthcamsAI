LABELS = {
    "supported",
    "refuted",
    "not_enough_information",
}

RELEVANCE_THRESHOLD = 0.20


def aggregate_claim_evidence(verified_results):
    """
    Aggregate sentence-level verification predictions
    into claim-level verdicts.

    Relevance filtering and verification are performed
    at sentence level.

    Paragraph and source metadata are preserved in the
    aggregated evidence records.
    """

    aggregated_results = []

    for item in verified_results or []:

        claim_id = item.get("claim_id")
        claim_text = item.get("claim_text", "")
        evidences = item.get("evidence", []) or []

        label_counts = {
            "supported": 0,
            "refuted": 0,
            "not_enough_information": 0,
        }

        supporting_evidence = []
        refuting_evidence = []
        inconclusive_evidence = []
        excluded_evidence = []

        total_sentence_verifications = 0

        for evidence in evidences:

            sentence_verifications = (
                evidence.get("sentence_verifications", [])
                or []
            )

            for sentence_result in sentence_verifications:

                verification = (
                    sentence_result.get("verification", {})
                    or {}
                )

                label = verification.get("label")

                if label not in LABELS:
                    continue

                total_sentence_verifications += 1

                relevance_score = sentence_result.get(
                    "relevance_score"
                )

                # Relevance threshold for aggregation.
                if relevance_score is not None:

                    try:
                        relevance_score = float(relevance_score)

                    except (TypeError, ValueError):
                        relevance_score = None

                if (
                    relevance_score is not None
                    and relevance_score < RELEVANCE_THRESHOLD
                ):

                    excluded_evidence.append({
                        **evidence,
                        "sentence_text": sentence_result.get(
                            "sentence_text"
                        ),
                        "relevance_score": relevance_score,
                        "verification": verification,
                        "aggregation_exclusion_reason": (
                            "low_relevance_score"
                        ),
                    })

                    continue

                sentence_evidence = {
                    **evidence,
                    "sentence_text": sentence_result.get(
                        "sentence_text"
                    ),
                    "relevance_score": relevance_score,
                    "verification": verification,
                }

                label_counts[label] += 1

                if label == "supported":

                    supporting_evidence.append(
                        sentence_evidence
                    )

                elif label == "refuted":

                    refuting_evidence.append(
                        sentence_evidence
                    )

                else:

                    inconclusive_evidence.append(
                        sentence_evidence
                    )

        # Claim-level aggregation.
        has_support = label_counts["supported"] > 0
        has_refutation = label_counts["refuted"] > 0

        total_valid = sum(label_counts.values())

        if total_valid == 0:

            verdict = "no_evidence"

        elif has_support and has_refutation:

            verdict = "conflicting_evidence"

        elif has_support:

            verdict = "supported"

        elif has_refutation:

            verdict = "refuted"

        else:

            verdict = "not_enough_information"

        aggregated_results.append({

            "claim_id": claim_id,
            "claim_text": claim_text,
            "verdict": verdict,

            "evidence_counts": label_counts,

            "total_evidence": total_sentence_verifications,

            "valid_verification_count": total_valid,

            "excluded_evidence_count": len(
                excluded_evidence
            ),

            "supporting_evidence": supporting_evidence,

            "refuting_evidence": refuting_evidence,

            "inconclusive_evidence": inconclusive_evidence,

            "excluded_evidence": excluded_evidence,
        })

    return aggregated_results
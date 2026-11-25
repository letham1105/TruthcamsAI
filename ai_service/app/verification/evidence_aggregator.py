LABELS = {
    "supported",
    "refuted",
    "not_enough_information",
}

# Experimental baseline.
# Evidence with relevance score below this threshold
# will not be used to determine the final verdict.
RELEVANCE_THRESHOLD = 0.20

RELEVANCE_SCORE_KEYS = (
    "relevance_score",
    "sentence_relevance_score",
    "similarity_score",
    "tfidf_score",
)


def get_relevance_score(evidence):
    """
    Extract sentence relevance score if available.
    """
    for key in RELEVANCE_SCORE_KEYS:
        score = evidence.get(key)

        if score is not None:
            try:
                return float(score)
            except (TypeError, ValueError):
                continue

    return None


def aggregate_claim_evidence(verified_results):
    """
    Aggregate sentence-level verification predictions
    into claim-level verdicts.

    Rule-based baseline:
    - Filter evidence using sentence relevance score.
    - Exclude low-relevance evidence from verdict calculation.
    - Aggregate remaining sentence-level NLI predictions.

    Sentence counts do not represent independent source counts
    or calibrated truth probabilities.
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

        for evidence in evidences:

            verification = evidence.get(
                "verification",
                {},
            ) or {}

            label = verification.get("label")

            if label not in LABELS:
                continue

            # --------------------------------------------------
            # 1. Relevance filtering
            # --------------------------------------------------

            relevance_score = get_relevance_score(evidence)

            if (
                relevance_score is not None
                and relevance_score < RELEVANCE_THRESHOLD
            ):
                excluded_evidence.append({
                    **evidence,
                    "aggregation_exclusion_reason": (
                        "low_relevance_score"
                    ),
                })
                continue

            # --------------------------------------------------
            # 2. Count valid evidence
            # --------------------------------------------------

            label_counts[label] += 1

            if label == "supported":

                supporting_evidence.append(evidence)

            elif label == "refuted":

                refuting_evidence.append(evidence)

            else:

                inconclusive_evidence.append(evidence)

        # ------------------------------------------------------
        # 3. Claim-level aggregation
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # 4. Output
        # ------------------------------------------------------

        aggregated_results.append({

            "claim_id": claim_id,
            "claim_text": claim_text,
            "verdict": verdict,

            "evidence_counts": label_counts,

            "total_evidence": len(evidences),

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
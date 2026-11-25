from ai_service.app import pipeline


USER_INPUT = """
Ngày 2/9/2026, mỗi người dân Việt Nam được phát 100.000 đồng.
"""


result = pipeline.run_search_pipeline(
    user_input=USER_INPUT,
    input_type="text",
)


def short_text(text, max_length=300):
    text = str(text or "").replace("\n", " ").strip()

    if len(text) > max_length:
        return text[:max_length] + "..."

    return text


# ============================================================
# PIPELINE STATUS
# ============================================================

print("\n" + "=" * 80)
print("PIPELINE STATUS")
print("=" * 80)

print("Status:", result.get("pipeline_status"))

print(
    "Counts:",
    {
        "claims": len(result.get("claims", [])),
        "queries": len(result.get("search_queries", [])),
        "search_results": len(result.get("search_results", [])),
        "articles": len(result.get("articles", [])),
        "paragraphs": len(result.get("paragraphs", [])),
        "retrieved": len(result.get("retrieved_evidence", [])),
        "verified": len(result.get("verified_evidence", [])),
        "aggregated": len(result.get("aggregated_results", [])),
    },
)


# ============================================================
# AGGREGATED RESULTS
# ============================================================

print("\n" + "=" * 80)
print("AGGREGATED RESULTS")
print("=" * 80)

for item in result.get("aggregated_results", []):

    print("\n" + "-" * 80)

    print("Claim ID:", item.get("claim_id"))
    print("Claim:", item.get("claim_text"))
    print("Verdict:", item.get("verdict"))

    print("Evidence counts:", item.get("evidence_counts"))
    print("Valid evidence:", item.get("valid_verification_count"))
    print("Total evidence:", item.get("total_evidence"))
    print("Excluded:", item.get("excluded_evidence_count", 0))

    # --------------------------------------------------------
    # SUPPORTING
    # --------------------------------------------------------

    supporting = item.get("supporting_evidence", [])

    print(f"\n[SUPPORT] {len(supporting)}")

    for evidence in supporting:

        verification = evidence.get("verification", {})

        print(
            f"- [{verification.get('confidence', 0):.4f}] "
            f"{short_text(evidence.get('paragraph_text'))}"
        )

    # --------------------------------------------------------
    # REFUTING
    # --------------------------------------------------------

    refuting = item.get("refuting_evidence", [])

    print(f"\n[REFUTED] {len(refuting)}")

    for evidence in refuting:

        verification = evidence.get("verification", {})

        print(
            f"- [{verification.get('confidence', 0):.4f}] "
            f"{short_text(evidence.get('paragraph_text'))}"
        )

    # --------------------------------------------------------
    # NEI
    # --------------------------------------------------------

    inconclusive = item.get("inconclusive_evidence", [])

    print(f"\n[NEI] {len(inconclusive)}")

    for evidence in inconclusive:

        verification = evidence.get("verification", {})

        print(
            f"- [{verification.get('confidence', 0):.4f}] "
            f"{short_text(evidence.get('paragraph_text'))}"
        )

    # --------------------------------------------------------
    # EXCLUDED
    # --------------------------------------------------------

    excluded = item.get("excluded_evidence", [])

    print(f"\n[EXCLUDED] {len(excluded)}")

    for evidence in excluded:

        verification = evidence.get("verification", {})

        print(
            f"- Label: {verification.get('label')} | "
            f"Score: {evidence.get('relevance_score', evidence.get('similarity_score', evidence.get('tfidf_score')))} | "
            f"{short_text(evidence.get('paragraph_text'))}"
        )


# ============================================================
# ERRORS
# ============================================================

print("\n" + "=" * 80)
print("ERRORS")
print("=" * 80)

errors = result.get("errors", []) or []

if not errors:
    print("No errors.")
else:
    for error in errors:
        print("-", error)
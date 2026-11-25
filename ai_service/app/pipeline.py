
from urllib.parse import urlparse

from ai_service.app.config import GOOGLE_NEWS_MAX_RESULTS, BM25_TOP_K
from ai_service.app.input.input_processor import process_input
from ai_service.app.input.ocr_cleaner import clean_ocr_text
from ai_service.app.extraction.claim_extractor import extract_claims

from ai_service.app.search.query_generator import prepare_search_queries
from ai_service.app.search.google_news import search_all_queries
from ai_service.app.search.result_normalizer import (
    normalize_search_results,
    deduplicate_results,
    filter_search_results,
)
from ai_service.app.search.url_resolver import resolve_google_news_urls
from ai_service.app.search.article_extractor import extract_article
from ai_service.app.search.article_cleaner import clean_article
from ai_service.app.search.paragraph_segmenter import segment_article
from ai_service.app.search.bm25_retriever import retrieve_evidence_bm25

from ai_service.app.verification.evidence_relevance import (
    filter_relevant_sentences,
)
from ai_service.app.verification.evidence_verification import (
    verify_retrieved_evidence,
)
from ai_service.app.verification.evidence_aggregator import (
    aggregate_claim_evidence,
)

from ai_service.app.utils.text_utils import safe_error
from ai_service.app.utils.logging_config import get_logger


logger = get_logger(__name__)


def run_search_pipeline(
    user_input,
    input_type="text",
    max_results=GOOGLE_NEWS_MAX_RESULTS,
    top_k=BM25_TOP_K,
    selected_claims=None,
):
    """
    Full Truthcams AI search and verification pipeline.

    Input
        -> Input Processing
        -> Claim Extraction
        -> Query Generation
        -> Google News Search
        -> Normalize / Deduplicate / Filter
        -> Google News URL Resolution
        -> Article Extraction
        -> Article Cleaning
        -> Paragraph Segmentation
        -> BM25 Evidence Retrieval
        -> Sentence Relevance Filtering
        -> Sentence-level VELECTRA Verification
        -> Evidence Aggregation

    Returns structured pipeline results.
    """

    result = {
        "input": {},
        "claims": [],
        "search_queries": [],
        "search_results": [],
        "rejected_search_results": [],
        "articles": [],
        "paragraphs": [],
        "retrieved_evidence": [],
        "filtered_evidence": [],
        "verified_evidence": [],
        "aggregated_results": [],
        "pipeline_status": "failed",
        "errors": [],
    }

    try:
        # =========================================================
        # 1. INPUT PROCESSING
        # =========================================================
        processed = process_input(user_input, input_type)
        result["input"] = processed

        extracted_text = processed.get("extracted_text") or ""

        if not extracted_text.strip():
            result["errors"].append({
                "stage": "input_processing",
                "error": (
                    processed.get("metadata", {}).get("error")
                    or "No extracted text."
                ),
            })
            return result

        if processed.get("metadata", {}).get("status") == "partial":
            result["errors"].append({
                "stage": "input_processing_partial",
                "error": (
                    processed.get("metadata", {}).get("error")
                    or "Input extraction was partial."
                ),
            })

        # =========================================================
        # 2. OCR TEXT CLEANING
        # =========================================================
        cleaned_text = clean_ocr_text(extracted_text)

        # Preserve raw OCR text and cleaned text for debugging
        result["input"]["raw_text"] = extracted_text
        result["input"]["cleaned_text"] = cleaned_text

        if not cleaned_text:
            result["errors"].append({
                "stage": "ocr_cleaning",
                "error": "No usable text after cleaning.",
            })
            return result

        # =========================================================
        # 3. CLAIM EXTRACTION
        # =========================================================
        try:
            claims_data = extract_claims(cleaned_text)

            if isinstance(claims_data, dict):
                result["claims"] = claims_data.get("claims", [])
            elif isinstance(claims_data, list):
                result["claims"] = claims_data
            else:
                result["claims"] = []

        except Exception as exc:
            result["errors"].append({
                "stage": "claim_extraction",
                "error": safe_error(exc),
            })
            logger.exception("Claim extraction failed")
            return result
        # =========================================================
        # 3. QUERY GENERATION
        # =========================================================
        prepared_queries = prepare_search_queries(result["claims"])
        result["search_queries"] = prepared_queries

        if not prepared_queries:
            result["errors"].append({
                "stage": "query_management",
                "error": "No valid search queries generated.",
            })
            result["pipeline_status"] = "partial"
            return result

        # =========================================================
        # 4. GOOGLE NEWS SEARCH
        # =========================================================
        raw_results, search_errors = search_all_queries(
            prepared_queries,
            max_results=max_results,
        )

        if search_errors:
            result["errors"].extend(search_errors)

        # =========================================================
        # 5. NORMALIZE / DEDUPLICATE / FILTER
        # =========================================================
        normalized_results = normalize_search_results(raw_results)

        unique_results = deduplicate_results(normalized_results)

        filtered_results, rejected_results = filter_search_results(
            unique_results
        )

        result["search_results"] = filtered_results
        result["rejected_search_results"] = rejected_results

        if rejected_results:
            result["errors"].append({
                "stage": "result_filtering",
                "count": len(rejected_results),
            })

        if not filtered_results:
            result["pipeline_status"] = "partial"
            return result

        # =========================================================
        # 6. GOOGLE NEWS URL RESOLUTION
        # =========================================================
        decoded_urls = resolve_google_news_urls(filtered_results)

        # =========================================================
        # 7. ARTICLE EXTRACTION / CLEANING / SEGMENTATION
        # =========================================================
        for search_result in filtered_results:

            original_url = search_result.get("url", "")

            hostname = urlparse(original_url).hostname

            if hostname == "news.google.com":
                publisher_url = decoded_urls.get(original_url)
            else:
                publisher_url = original_url

            # Skip unresolved Google News URLs.
            if not publisher_url:
                result["errors"].append({
                    "stage": "google_news_url_resolution",
                    "url": original_url,
                    "status": "failed",
                    "error": (
                        "Could not resolve Google News URL "
                        "to publisher URL."
                    ),
                })
                continue

            article_input = dict(search_result)
            article_input["google_news_url"] = original_url
            article_input["url"] = publisher_url

            # Extract article.
            try:
                article = extract_article(
                    publisher_url,
                    search_result=article_input,
                )

            except Exception as exc:
                result["errors"].append({
                    "stage": "article_extraction",
                    "url": publisher_url,
                    "google_news_url": original_url,
                    "status": "failed",
                    "error": safe_error(exc),
                })
                logger.exception(
                    "Article extraction failed: %s",
                    publisher_url,
                )
                continue

            article["google_news_url"] = original_url
            article["publisher_url"] = publisher_url

            # Clean article content.
            article = clean_article(article)

            # Store article.
            result["articles"].append(article)

            if article.get("extraction_status") != "success":
                result["errors"].append({
                    "stage": "article_extraction",
                    "article_id": article.get("article_id"),
                    "url": publisher_url,
                    "google_news_url": original_url,
                    "status": article.get("extraction_status"),
                    "error": (
                        article.get("error")
                        or "Article extraction was partial or failed."
                    ),
                })

            # Segment article into paragraphs.
            try:
                article_paragraphs = segment_article(article)

                result["paragraphs"].extend(
                    article_paragraphs
                )

            except Exception as exc:
                result["errors"].append({
                    "stage": "paragraph_segmentation",
                    "article_id": article.get("article_id"),
                    "url": publisher_url,
                    "error": safe_error(exc),
                })
                logger.exception(
                    "Paragraph segmentation failed"
                )

        # =========================================================
        # 8. BM25 EVIDENCE RETRIEVAL
        # =========================================================
        result["retrieved_evidence"] = retrieve_evidence_bm25(
            result["claims"],
            result["paragraphs"],
            top_k=top_k,
        )

        has_retrieval = any(
            item.get("evidence")
            for item in result["retrieved_evidence"]
        )

        if not has_retrieval:
            result["pipeline_status"] = "partial"
            return result

        # =========================================================
        # 9. SENTENCE RELEVANCE FILTERING
        # =========================================================
        try:
            result["filtered_evidence"] = filter_relevant_sentences(
                result["retrieved_evidence"],
                threshold=0.08,
            )

        except Exception as exc:
            result["errors"].append({
                "stage": "evidence_relevance_filtering",
                "error": safe_error(exc),
            })

            logger.exception(
                "Evidence relevance filtering failed"
            )

            result["pipeline_status"] = "partial"
            return result

        has_relevant_evidence = any(
            item.get("evidence")
            for item in result["filtered_evidence"]
        )

        if not has_relevant_evidence:
            result["pipeline_status"] = "partial"
            result["errors"].append({
                "stage": "evidence_relevance_filtering",
                "error": (
                    "No relevant sentences retained "
                    "by the relevance filter."
                ),
            })
            return result

        # =========================================================
        # 10. SENTENCE-LEVEL VELECTRA VERIFICATION
        # =========================================================
        try:
            result["verified_evidence"] = verify_retrieved_evidence(
                result["filtered_evidence"]
            )

        except Exception as exc:
            result["errors"].append({
                "stage": "evidence_verification",
                "error": safe_error(exc),
            })

            logger.exception(
                "Evidence verification failed"
            )

            result["pipeline_status"] = "partial"
            return result

        # =========================================================
        # 11. EVIDENCE AGGREGATION
        # =========================================================
        try:
            result["aggregated_results"] = aggregate_claim_evidence(
                result["verified_evidence"]
            )

        except Exception as exc:
            result["errors"].append({
                "stage": "evidence_aggregation",
                "error": safe_error(exc),
            })

            logger.exception(
                "Evidence aggregation failed"
            )

            result["pipeline_status"] = "partial"
            return result

        # =========================================================
        # 12. PIPELINE STATUS
        # =========================================================
        if result["errors"]:
            result["pipeline_status"] = "partial"
        else:
            result["pipeline_status"] = "success"

    except Exception as exc:
        result["errors"].append({
            "stage": "pipeline_orchestration",
            "error": safe_error(exc),
        })

        result["pipeline_status"] = "failed"

        logger.exception(
            "Search and verification pipeline failed"
        )

    return result


import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_RELEVANCE_THRESHOLD = 0.08


def clean_text(text):
    """Basic text cleaning before sentence segmentation."""
    text = str(text or "")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text):
    """
    Experimental Vietnamese sentence segmentation.

    Handle:
    - Newlines
    - Sentence-ending punctuation
    - Selected fused headline/body boundaries
    """

    text = str(text or "").strip()

    if not text:
        return []

    text = re.sub(r"\r\n?", "\n", text)

    chunks = [
        chunk.strip()
        for chunk in text.split("\n")
        if chunk.strip()
    ]

    sentences = []

    fused_patterns = [
        r"(?<=[đĐ]ồng)\s+(?=Ngoài hành vi\b)",
        r"(?<=[đĐ]ồng)\s+(?=Ngoài dự án\b)",
        r"(?<=[đĐ]ồng)\s+(?=Theo cơ quan điều tra\b)",
        r"(?<=[đĐ]ồng)\s+(?=Theo kết quả điều tra\b)",
        r"(?<=[đĐ]ồng)\s+(?=Tuy nhiên\b)",
        r"(?<=[đĐ]ồng)\s+(?=Đáng chú ý\b)",
    ]

    for chunk in chunks:

        for pattern in fused_patterns:
            chunk = re.sub(pattern, ". ", chunk)

        parts = re.split(
            r'(?<=[.!?])\s+',
            chunk,
        )

        for part in parts:
            sentence = clean_text(part)

            if sentence:
                sentences.append(sentence)

    return sentences


def calculate_relevance(claim, sentences):
    """
    Character n-gram TF-IDF cosine similarity.

    Measures lexical similarity, not factual correctness.
    """

    if not sentences:
        return []

    claim = clean_text(claim)

    if not claim:
        return [0.0] * len(sentences)

    texts = [claim] + sentences

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
    )

    vectors = vectorizer.fit_transform(texts)

    scores = cosine_similarity(
        vectors[0],
        vectors[1:],
    ).flatten()

    return scores.tolist()


def filter_relevant_sentences(
    bm25_results,
    threshold=DEFAULT_RELEVANCE_THRESHOLD,
):
    """
    Split retrieved paragraphs into sentences and filter
    sentences using lexical relevance to the claim.

    Original paragraph metadata is preserved.
    """

    filtered_results = []

    for item in bm25_results or []:

        claim_id = item.get("claim_id")
        claim_text = clean_text(
            item.get("claim_text", "")
        )

        evidences = item.get("evidence", []) or []

        filtered_evidences = []

        for evidence in evidences:

            paragraph_text = str(
                evidence.get("paragraph_text", "") or ""
            )

            sentences = split_sentences(
                paragraph_text
            )

            if not claim_text or not sentences:
                continue

            scores = calculate_relevance(
                claim_text,
                sentences,
            )

            sentence_results = []

            for sentence, score in zip(
                sentences,
                scores,
            ):

                sentence_results.append({
                    "sentence": sentence,
                    "relevance_score": float(score),
                    "is_relevant": (
                        float(score) >= threshold
                    ),
                })

            relevant_sentences = [
                result
                for result in sentence_results
                if result["is_relevant"]
            ]

            filtered_evidences.append({
                **evidence,
                "original_paragraph_text": paragraph_text,
                "sentence_relevance": sentence_results,
                "relevant_sentences": relevant_sentences,
                "relevant_sentence_count": len(
                    relevant_sentences
                ),
                "relevance_threshold": threshold,
            })

        filtered_results.append({
            "claim_id": claim_id,
            "claim_text": claim_text,
            "evidence": filtered_evidences,
        })

    return filtered_results

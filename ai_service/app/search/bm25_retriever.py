import math
import re
import unicodedata

try:
    from underthesea import word_tokenize as vi_word_tokenize
except ImportError:
    vi_word_tokenize = None

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

from ai_service.app.utils.text_utils import clean_text

VI_STOPWORDS = {
    "và", "là", "của", "có", "được", "cho", "trong", "với", "một", "các",
    "những", "này", "đó", "tại", "theo", "về", "đã", "đang", "sẽ", "bị",
    "từ", "khi", "do", "để", "trên", "sau", "trước", "năm", "ngày",
}

def tokenize_vietnamese(text):
    text = unicodedata.normalize("NFC", str(text or "")).lower()
    if vi_word_tokenize is not None:
        try:
            token_text = vi_word_tokenize(text, format="text")
            tokens = re.findall(r"[\w]+", token_text, flags=re.UNICODE)
        except Exception:
            tokens = re.findall(r"[\w]+", text, flags=re.UNICODE)
    else:
        tokens = re.findall(r"[\w]+", text, flags=re.UNICODE)
    return [
        t for t in tokens
        if t not in VI_STOPWORDS and (len(t) > 1 or t.isdigit())
    ]

class SimpleBM25:
    """BM25 fallback for environments without rank_bm25."""
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.corpus = corpus
        self.k1, self.b = k1, b
        self.doc_len = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_len) / max(len(self.doc_len), 1)
        self.df = {}
        for doc in corpus:
            for term in set(doc):
                self.df[term] = self.df.get(term, 0) + 1
        self.idf = {
            term: math.log(1 + (len(corpus) - freq + 0.5) / (freq + 0.5))
            for term, freq in self.df.items()
        }

    def get_scores(self, query_tokens):
        scores = []
        for doc, length in zip(self.corpus, self.doc_len):
            frequencies = {}
            for token in doc:
                frequencies[token] = frequencies.get(token, 0) + 1
            score = 0.0
            for term in query_tokens:
                if term not in frequencies:
                    continue
                freq = frequencies[term]
                denom = freq + self.k1 * (
                    1 - self.b + self.b * length / max(self.avgdl, 1)
                )
                score += self.idf.get(term, 0.0) * (
                    freq * (self.k1 + 1) / denom
                )
            scores.append(score)
        return scores

def retrieve_evidence_bm25(claims, paragraphs, top_k=5):
    """BM25 scores textual relevance, not truth probability."""
    if isinstance(claims, dict):
        claims = claims.get("claims", [])
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    output = []
    paragraphs = paragraphs or []

    for claim in claims or []:
        claim_id = claim.get("claim_id")
        claim_text = clean_text(claim.get("claim_text"))
        candidates = [
            p for p in paragraphs
            if claim_id in (p.get("claim_ids") or [])
        ]
        query_tokens = tokenize_vietnamese(claim_text)
        evidence = []

        if not candidates or not query_tokens:
            output.append({
                "claim_id": claim_id, "claim_text": claim_text, "evidence": []
            })
            continue

        tokenized_pairs = [
            (p, tokenize_vietnamese(p.get("paragraph_text", "")))
            for p in candidates
        ]
        tokenized_pairs = [(p, tokens) for p, tokens in tokenized_pairs if tokens]

        if not tokenized_pairs:
            output.append({
                "claim_id": claim_id, "claim_text": claim_text, "evidence": []
            })
            continue

        searchable_paragraphs = [p for p, _ in tokenized_pairs]
        corpus_tokens = [tokens for _, tokens in tokenized_pairs]

        if BM25Okapi is not None:
            index = BM25Okapi(corpus_tokens)
            scores = list(index.get_scores(query_tokens))
            if not any(math.isfinite(float(s)) and s > 0 for s in scores):
                scores = SimpleBM25(corpus_tokens).get_scores(query_tokens)
        else:
            scores = SimpleBM25(corpus_tokens).get_scores(query_tokens)

        query_token_set = set(query_tokens)
        matched_indices = [
            idx for idx, tokens in enumerate(corpus_tokens)
            if query_token_set.intersection(tokens)
        ]
        ranked = sorted(
            matched_indices, key=lambda idx: scores[idx], reverse=True
        )[:top_k]

        for rank, idx in enumerate(ranked, start=1):
            paragraph = searchable_paragraphs[idx]
            evidence.append({
                "rank": rank,
                "score": float(scores[idx]),
                "article_id": paragraph.get("article_id"),
                "paragraph_id": paragraph.get("paragraph_id"),
                "title": paragraph.get("title", ""),
                "source": paragraph.get("source", ""),
                "url": paragraph.get("url", ""),
                "published_at": paragraph.get("published_at"),
                "paragraph_text": paragraph.get("paragraph_text", ""),
            })

        output.append({
            "claim_id": claim_id,
            "claim_text": claim_text,
            "evidence": evidence,
        })
    return output

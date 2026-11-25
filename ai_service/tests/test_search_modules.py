from ai_service.app.search.query_generator import prepare_search_queries
from ai_service.app.search.result_normalizer import (
    normalize_search_results, deduplicate_results, filter_search_results
)
from ai_service.app.search.bm25_retriever import retrieve_evidence_bm25

def test_query_generation():
    claims = [{
        "claim_id": "C1",
        "claim_text": "Đà Nẵng xây cầu",
        "search_queries": ["Đà Nẵng xây cầu", " ", "Đà Nẵng xây cầu"],
    }]
    rows = prepare_search_queries(claims)
    assert len(rows) == 1
    assert rows[0]["claim_id"] == "C1"

def test_result_deduplication():
    rows = normalize_search_results([
        {"claim_id": "C1", "search_query": "q1", "title": "Title", "url": "https://www.example.com/a?utm_source=x"},
        {"claim_id": "C2", "search_query": "q2", "title": "Title", "url": "https://example.com/a"},
    ])
    unique = deduplicate_results(rows)
    assert len(unique) == 1
    assert set(unique[0]["claim_ids"]) == {"C1", "C2"}
    assert len(filter_search_results(unique)[0]) == 1

def test_bm25_synthetic():
    claims = [{"claim_id": "C1", "claim_text": "Đà Nẵng xây dựng cầu mới với vốn đầu tư 500 tỷ đồng"}]
    paragraphs = [
        {"claim_ids": ["C1"], "article_id": "A1", "paragraph_id": "A1_P01",
         "title": "Dự án cầu", "source": "Demo", "url": "https://example.com/a",
         "paragraph_text": "Đà Nẵng triển khai dự án xây dựng cầu mới với tổng vốn đầu tư 500 tỷ đồng."},
        {"claim_ids": ["C1"], "article_id": "A2", "paragraph_id": "A2_P01",
         "title": "Tin thể thao", "source": "Demo", "url": "https://example.com/b",
         "paragraph_text": "Đội bóng địa phương giành chiến thắng trong trận đấu cuối tuần."},
    ]
    result = retrieve_evidence_bm25(claims, paragraphs, top_k=5)
    assert result[0]["evidence"]
    assert result[0]["evidence"][0]["paragraph_id"] == "A1_P01"

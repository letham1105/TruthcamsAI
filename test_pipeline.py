
from pprint import pprint

from ai_service.app.pipeline import run_search_pipeline


TEST_INPUT = (
    "Dự án Antex bị cáo buộc trốn thuế "
    "với số tiền hơn 38,7 tỷ đồng."
)


def main():
    result = run_search_pipeline(
        user_input=TEST_INPUT,
        input_type="text",
    )

    print("\n" + "=" * 100)
    print("PIPELINE STATUS")
    print("=" * 100)
    print(result.get("pipeline_status"))

    print("\n" + "=" * 100)
    print("EXTRACTED CLAIMS")
    print("=" * 100)
    pprint(result.get("claims"))

    print("\n" + "=" * 100)
    print("SEARCH RESULTS")
    print("=" * 100)
    pprint(result.get("search_results"))

    print("\n" + "=" * 100)
    print("RETRIEVED EVIDENCE (BM25)")
    print("=" * 100)
    pprint(result.get("retrieved_evidence"))

    print("\n" + "=" * 100)
    print("FILTERED EVIDENCE (TF-IDF)")
    print("=" * 100)
    pprint(result.get("filtered_evidence"))

    print("\n" + "=" * 100)
    print("VERIFIED EVIDENCE (VELECTRA)")
    print("=" * 100)
    pprint(result.get("verified_evidence"))

    print("\n" + "=" * 100)
    print("AGGREGATED RESULTS")
    print("=" * 100)
    pprint(result.get("aggregated_results"))

    print("\n" + "=" * 100)
    print("ERRORS")
    print("=" * 100)
    pprint(result.get("errors"))


if __name__ == "__main__":
    main()

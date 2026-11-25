from collections import Counter
from pathlib import Path

from ai_service.app.verification.evidence_relevance import (
    split_sentences,
    calculate_relevance,
)
from ai_service.app.verification.verifier import verify_pair


CLAIM = "Dự án Antex bị cáo buộc trốn thuế với số tiền hơn 38,7 tỷ đồng."

THRESHOLD = 0.10

TEST_CASES = [
    {
        "name": "CafeF Rank 1",
        "evidence": """Ngoài dự án tiền số, cơ quan điều tra còn làm rõ hoạt động kinh doanh bất động sản tại Nextland, nơi bị can Nguyễn Hòa Bình bị cáo buộc chỉ đạo nhân viên sử dụng 2 hệ thống sổ sách kế toán để che giấu doanh thu, lợi nhuận. Theo kết quả điều tra, từ năm 2022 đến tháng 5/2025, Nextland bán 7 bất động sản, thu về hơn 117,17 tỷ đồng. Tuy nhiên, trong số tiền này, gần 45 tỷ đồng bị để ngoài sổ sách kế toán. Cơ quan điều tra xác định, việc sử dụng 2 hệ thống sổ sách kế toán tại Nextland gây thiệt hại cho ngân sách nhà nước hơn 4,36 tỷ đồng, từ đó đề nghị truy tố Nguyễn Hòa Bình về tội vi phạm quy định về kế toán gây hậu quả nghiêm trọng. Một hành vi khác được làm rõ trong kết luận điều tra liên quan đến hoạt động của Công ty cổ phần công nghệ Vi Mô. Theo cơ quan điều tra, Nguyễn Hòa Bình đã chỉ đạo nhân viên cung cấp dịch vụ nhưng không xuất hóa đơn, không đưa doanh thu vào sổ sách kế toán. Không dừng ở việc để doanh thu ngoài sổ sách, cơ quan điều tra còn xác định Bình chỉ đạo hợp thức hóa các giao dịch chuyển nhượng cổ phần nhằm che giấu thông tin cá nhân sở hữu cổ phần. Đáng chú ý, Nguyễn Hòa Bình bị cáo buộc nhờ nhân viên đứng tên chủ sở hữu các công ty trách nhiệm hữu hạn một thành viên để nhận tiền cổ tức được chi trả. Bằng những hành vi này, tổng số tiền Nguyễn Hòa Bình bị cáo buộc trốn thuế là hơn 38,7 tỷ đồng. Trong vụ án này, bị can Nguyễn Hữu Tuất được xác định là người giúp sức cho Nguyễn Hòa Bình ở cả 2 nhóm hành vi liên quan dự án AntEx và hoạt động trốn thuế tại Công ty Vi Mô. Theo kết luận điều tra, Tuất tham gia phát triển dự án AntEx, giúp sức cho việc chiếm đoạt tiền của các nhà đầu tư. Bị can còn đồng phạm trong việc bán hàng không xuất hóa đơn, để doanh thu ngoài sổ sách tại Công ty Vi Mô, dẫn đến hành vi trốn thuế số tiền đặc biệt lớn.""",
    },
    {
        "name": "Kenh14 Rank 3",
        "evidence": """Từ những tài liệu thu thập được, cơ quan điều tra đề nghị truy tố Nguyễn Hòa Bình về tội lừa đảo chiếm đoạt tài sản theo khoản 4 Điều 174 Bộ luật Hình sự. Ngoài dự án tiền số, cơ quan công an còn làm rõ hoạt động kinh doanh bất động sản tại Nextland, nơi Shark Bình bị cáo buộc chỉ đạo nhân viên sử dụng hai hệ thống sổ sách kế toán để che giấu doanh thu, lợi nhuận. Theo kết quả điều tra, từ năm 2022 đến tháng 5/2025, Nextland bán bảy bất động sản, thu về hơn 117,17 tỷ đồng. Tuy nhiên, trong số tiền này, gần 45 tỉ đồng bị để ngoài sổ sách kế toán. Kết luận điều tra ghi nhận Nextland đã kê khai, quyết toán thuế đối với khoản doanh thu bị để ngoài sổ sách nói trên. Tuy nhiên, cơ quan điều tra vẫn xác định việc sử dụng hai hệ thống sổ sách kế toán tại Nextland gây thiệt hại cho ngân sách nhà nước hơn 4,36 tỷ đồng, từ đó đề nghị truy tố Shark Bình về tội vi phạm quy định về kế toán gây hậu quả nghiêm trọng. Cũng theo cơ quan công an, Shark Bình đã chỉ đạo nhân viên cung cấp dịch vụ nhưng không xuất hóa đơn, không đưa doanh thu vào sổ sách kế toán. Không dừng ở việc để doanh thu ngoài sổ sách, không dừng ở việc để doanh thu ngoài sổ sách, cơ quan điều tra còn xác định Bình chỉ đạo hợp thức hóa các giao dịch chuyển nhượng cổ phần nhằm che giấu thông tin cá nhân sở hữu cổ phần. Đáng chú ý, Shark Bình bị cáo buộc nhờ nhân viên đứng tên chủ sở hữu các công ty trách nhiệm hữu hạn một thành viên để nhận tiền cổ tức được chi trả. Bằng những hành vi này, tổng số tiền Shark Bình bị cáo buộc trốn thuế là hơn 38,7 tỷ đồng. Nguyễn Hữu Tuất được xác định là người giúp sức cho Shark Bình ở cả 2 nhóm hành vi liên quan dự án AntEx và hoạt động trốn thuế tại Vimo. Theo kết luận điều tra, Tuất tham gia phát triển dự án AntEx, giúp sức cho việc chiếm đoạt tiền của các nhà đầu tư.""",
    },
    {
        "name": "Dan Tri Rank 5",
        "evidence": """Một phần tiền còn được chuyển vào các doanh nghiệp trong hệ sinh thái NextTech để sử dụng không đúng mục đích. Cơ quan điều tra xác định hành vi của Bình và đồng phạm đã chiếm đoạt của nhiều bị hại số tiền đặc biệt lớn. Từ đó, đề nghị truy tố Bình về tội Lừa đảo chiếm đoạt tài sản theo khoản 4 Điều 174 Bộ luật Hình sự. Để ngoài sổ sách gần 45 tỷ đồng, trốn thuế hơn 38,7 tỷ đồng Ngoài hành vi liên quan dự án tiền số, Shark Bình còn bị cáo buộc chỉ đạo cấp dưới thực hiện những sai phạm trong hoạt động kinh doanh bất động sản tại Công ty cổ phần Đầu tư và Kinh doanh bất động sản Nextland. Theo cơ quan điều tra, từ năm 2022 đến tháng 5/2025, Nextland bán 7 bất động sản, thu về hơn 117,17 tỷ đồng. Tuy nhiên, gần 45 tỷ đồng trong số này không được đưa vào sổ sách kế toán. Để che giấu doanh thu và lợi nhuận thực tế, Bình bị cáo buộc chỉ đạo nhân viên sử dụng hai hệ thống sổ sách kế toán. Mặc dù Nextland sau đó đã kê khai, quyết toán thuế đối với khoản doanh thu nói trên, cơ quan điều tra vẫn xác định hành vi vi phạm quy định về kế toán gây thiệt hại hơn 4,36 tỷ đồng cho ngân sách Nhà nước. Đối với hoạt động của Công ty cổ phần Công nghệ Vimo, cơ quan điều tra xác định Shark Bình chỉ đạo nhân viên cung cấp dịch vụ nhưng không xuất hóa đơn, đồng thời không hạch toán đầy đủ doanh thu vào sổ sách. Đáng chú ý, bị can còn bị cáo buộc chỉ đạo hợp thức hóa các giao dịch chuyển nhượng cổ phần để che giấu việc cá nhân sở hữu cổ phần. Bình cũng nhờ nhân viên đứng tên chủ sở hữu những công ty trách nhiệm hữu hạn một thành viên để nhận tiền cổ tức thay mình. Bằng các thủ đoạn trên, tổng số tiền thuế mà Shark Bình bị cáo buộc trốn là hơn 38,7 tỷ đồng.""",
    },
]


LABELS = [
    "supported",
    "refuted",
    "not_enough_information",
]


def get_label_counts(results):
    counts = Counter(
        result["label"]
        for result in results
    )

    return {
        label: counts.get(label, 0)
        for label in LABELS
    }


def format_counts(results):
    counts = get_label_counts(results)

    return (
        f"supported={counts['supported']} | "
        f"refuted={counts['refuted']} | "
        f"NEI={counts['not_enough_information']}"
    )


def run_experiment():

    output_lines = []

    def log(text=""):
        print(text)
        output_lines.append(str(text))

    log("=" * 100)
    log("FILTERED SENTENCE VERIFICATION EXPERIMENT")
    log(f"Claim: {CLAIM}")
    log(f"Threshold: {THRESHOLD}")
    log("=" * 100)

    global_results = {
        "all": [],
        "kept": [],
        "rejected": [],
    }

    for case in TEST_CASES:

        sentences = split_sentences(
            case["evidence"]
        )

        scores = calculate_relevance(
            CLAIM,
            sentences,
        )

        case_results = []

        log("\n" + "=" * 100)
        log(case["name"])
        log("=" * 100)

        for index, (sentence, score) in enumerate(
            zip(sentences, scores),
            start=1,
        ):

            is_relevant = score >= THRESHOLD

            # Run VELECTRA on every sentence exactly once.
            verification = verify_pair(
                claim=CLAIM,
                evidence=sentence,
            )

            result = {
                "sentence_id": index,
                "sentence": sentence,
                "relevance_score": float(score),
                "is_relevant": is_relevant,
                "label": verification.label,
                "confidence": verification.confidence,
                "scores": verification.scores,
            }

            case_results.append(result)

            global_results["all"].append(result)

            group = (
                "kept"
                if is_relevant
                else "rejected"
            )

            global_results[group].append(result)

            log(
                f"\nS{index} | "
                f"relevance={score:.4f} | "
                f"group={group.upper()} | "
                f"label={verification.label} | "
                f"confidence={verification.confidence:.4f}"
            )

            log(sentence)

        kept = [
            result
            for result in case_results
            if result["is_relevant"]
        ]

        rejected = [
            result
            for result in case_results
            if not result["is_relevant"]
        ]

        log("\n" + "-" * 100)
        log("ARTICLE SUMMARY")
        log("-" * 100)

        log(
            f"Total sentences: {len(case_results)}"
        )

        log(
            f"Kept: {len(kept)} | "
            f"Rejected: {len(rejected)}"
        )

        log(
            "\nALL: "
            + format_counts(case_results)
        )

        log(
            "KEPT: "
            + format_counts(kept)
        )

        log(
            "REJECTED: "
            + format_counts(rejected)
        )

    log("\n" + "=" * 100)
    log("OVERALL SUMMARY")
    log("=" * 100)

    for group in ["all", "kept", "rejected"]:

        results = global_results[group]

        log(f"\n[{group.upper()}]")

        log(
            f"Total: {len(results)}"
        )

        log(
            format_counts(results)
        )

    log("\n" + "=" * 100)
    log("END OF EXPERIMENT")
    log("=" * 100)

    output_path = Path(
        "filtered_verification_results.txt"
    )

    output_path.write_text(
        "\n".join(output_lines),
        encoding="utf-8",
    )

    print(
        f"\nResults saved to: {output_path.resolve()}"
    )


if __name__ == "__main__":
    run_experiment()


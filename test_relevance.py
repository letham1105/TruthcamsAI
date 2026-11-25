from ai_service.app.verification.evidence_relevance import (
    split_sentences,
    calculate_relevance,
)

CLAIM = "Dự án Antex bị cáo buộc trốn thuế với số tiền hơn 38,7 tỷ đồng."

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


THRESHOLDS = [0.10, 0.15, 0.20, 0.25]


for case in TEST_CASES:
    sentences = split_sentences(case["evidence"])

    scores = calculate_relevance(CLAIM, sentences)

    print("\n" + "=" * 100)
    print(case["name"])
    print("=" * 100)

    for i, (sentence, score) in enumerate(
        zip(sentences, scores), start=1
    ):
        print(f"\nS{i} | score={score:.4f}")
        print(sentence)

    print("\n" + "-" * 100)

    for threshold in THRESHOLDS:
        selected = [
            sentence
            for sentence, score in zip(sentences, scores)
            if score >= threshold
        ]

        rejected = [
            sentence
            for sentence, score in zip(sentences, scores)
            if score < threshold
        ]

        print(f"\nTHRESHOLD = {threshold}")
        print(
            f"Kept: {len(selected)}/{len(sentences)} | "
            f"Rejected: {len(rejected)}/{len(sentences)}"
        )

        print("\n[KEPT]")
        for sentence in selected:
            print("-", sentence)

        print("\n[REJECTED]")
        for sentence in rejected:
            print("-", sentence)

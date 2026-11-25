from ai_service.app.verification.verifier import verify_pair

claim = "Mặt Trăng quay quanh Trái Đất."

evidences = [
    {
        "rank": 1,
        "text": (
            "Tuy nhiên, do hai chuyển động diễn ra với cùng chu kỳ, "
            "chúng ta luôn chỉ nhìn thấy một mặt. Hiện tượng này được gọi "
            "là synchronous rotation (quay đồng bộ)."
        ),
    },
    {
        "rank": 2,
        "text": (
            "Bài viết nói về các hình ảnh Artemis II và khái niệm "
            "mặt tối của Mặt Trăng, liệu mặt tối có thực sự luôn tối hay không."
        ),
    },
    {
        "rank": 3,
        "text": (
            "Mặt Trăng đóng vai trò đối với sự sống trên Trái Đất, "
            "quỹ đạo cổ đại và các tác động thủy triều."
        ),
    },
    {
        "rank": 4,
        "text": (
            "Mặt Trăng quay quanh trục của nó với chu kỳ 27,3 ngày, "
            "bằng chu kỳ quay quanh Trái Đất. Hiện tượng này được gọi là "
            "khóa thủy triều."
        ),
    },
    {
        "rank": 5,
        "text": (
            "Mặt Trăng là vệ tinh tự nhiên của Trái Đất, có quỹ đạo ổn định, "
            "chu kỳ khoảng 27,32 ngày và khoảng cách trung bình hơn 384.000 km."
        ),
    },
]

for item in evidences:
    print("=" * 80)
    print(f"Evidence rank: {item['rank']}")

    result = verify_pair(claim, item["text"])

    print(result)
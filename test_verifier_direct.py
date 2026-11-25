import torch
from ai_service.app.verification.verifier import load_verifier, verify_pair

model, tokenizer = load_verifier()

print("=" * 60)
print("MODEL CONFIG")
print("=" * 60)
print("num_labels:", model.config.num_labels)
print("id2label:", model.config.id2label)
print("label2id:", model.config.label2id)
print("classifier:", model.classifier)
claim = (
    "Dự án Antex bị cáo buộc trốn thuế "
    "với số tiền hơn 38,7 tỷ đồng."
)

cases = [
    {
        "name": "CafeF Rank 1",
        "evidence": (
            "Bằng những hành vi này, tổng số tiền "
            "Nguyễn Hòa Bình bị cáo buộc trốn thuế "
            "là hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "Kenh14 Rank 2",
        "evidence": (
            "Bằng những thủ đoạn trên, tổng số tiền "
            "Nguyễn Hòa Bình bị cáo buộc trốn thuế "
            "là hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "Dan Tri Rank 4",
        "evidence": (
            "Để ngoài sổ sách gần 45 tỷ đồng, trốn thuế "
            "hơn 38,7 tỷ đồng. Bằng các thủ đoạn trên, "
            "tổng số tiền thuế mà Shark Bình bị cáo buộc "
            "trốn là hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "Dan Tri Rank 5",
        "evidence": (
            "Cơ quan điều tra đề nghị truy tố Nguyễn Hòa Bình "
            "về 3 tội danh, trong đó có tội trốn thuế "
            "liên quan đến số tiền hơn 38,7 tỷ đồng."
        ),
    },
]

for case in cases:
    result = verify_pair(claim, case["evidence"])

    print("\n" + "=" * 60)
    print(case["name"])
    print("=" * 60)
    print("Claim:", claim)
    print("Evidence:", case["evidence"])
    print("Label:", result.label)
    print("Confidence:", result.confidence)
    print("Scores:", result.scores)

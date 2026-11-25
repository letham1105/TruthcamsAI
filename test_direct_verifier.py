import torch
from ai_service.app.verification.verifier import load_verifier, LABELS

CLAIM = (
    "Dự án Antex bị cáo buộc trốn thuế "
    "với số tiền hơn 38,7 tỷ đồng."
)

TEST_CASES = [
    {
        "name": "T1 - CafeF",
        "evidence": (
            "Bằng những hành vi này, tổng số tiền Nguyễn Hòa Bình "
            "bị cáo buộc trốn thuế là hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "T2 - Dan Tri P01",
        "evidence": (
            "Cơ quan điều tra đề nghị truy tố Nguyễn Hòa Bình "
            "về 3 tội danh, trong đó có tội Trốn thuế, "
            "với số tiền hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "T3 - Kenh14",
        "evidence": (
            "Bằng những hành vi này, tổng số tiền Shark Bình "
            "bị cáo buộc trốn thuế là hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "T4 - aFamily",
        "evidence": (
            "Bằng những hành vi này, tổng số tiền Shark Bình "
            "bị cáo buộc trốn thuế là hơn 38,7 tỷ đồng."
        ),
    },
    {
        "name": "T5 - Dan Tri P02",
        "evidence": (
            "Bằng các thủ đoạn trên, tổng số tiền thuế mà "
            "Shark Bình bị cáo buộc trốn là hơn 38,7 tỷ đồng."
        ),
    },
]

model, tokenizer = load_verifier()

print("=" * 80)
print("MODEL CONFIG")
print("=" * 80)

print("config.id2label:", model.config.id2label)
print("config.label2id:", model.config.label2id)
print("Hardcoded LABELS:", LABELS)

print("\n" + "=" * 80)
print("DIRECT VERIFICATION")
print("=" * 80)

for case in TEST_CASES:
    inputs = tokenizer(
        CLAIM,
        case["evidence"],
        return_tensors="pt",
        truncation="only_second",
        max_length=256,
    )

    with torch.inference_mode():
        outputs = model(**inputs)
        logits = outputs.logits[0]
        probs = torch.softmax(logits, dim=-1)

    predicted_id = int(torch.argmax(probs).item())

    print(f"\n--- {case['name']} ---")
    print("Evidence:", case["evidence"])
    print("Raw logits:", logits.tolist())
    print("Probabilities:", probs.tolist())
    print("Predicted ID:", predicted_id)
    print("Predicted label:", LABELS[predicted_id])

    print("Scores:")
    for i, score in enumerate(probs):
        print(f"  ID {i} - {LABELS[i]}: {float(score):.6f}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)

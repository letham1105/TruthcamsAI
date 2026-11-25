
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from ai_service.app.verification.verification_schema import VerificationResult


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "velectra-vifactcheck"
)

LABELS = {
    0: "supported",
    1: "refuted",
    2: "not_enough_information",
}

_model = None
_tokenizer = None


def load_verifier():
    global _model, _tokenizer

    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model directory not found: {MODEL_PATH}"
        )

    _tokenizer = AutoTokenizer.from_pretrained(
        str(MODEL_PATH),
        local_files_only=True,
        use_fast=False,
    )

    _model = AutoModelForSequenceClassification.from_pretrained(
        str(MODEL_PATH),
        local_files_only=True,
    )

    _model.to("cpu")
    _model.eval()

    return _model, _tokenizer


def verify_pair(claim: str, evidence: str) -> VerificationResult:

    if not claim.strip():
        raise ValueError("Claim must not be empty.")

    if not evidence.strip():
        raise ValueError("Evidence must not be empty.")

    model, tokenizer = load_verifier()

    inputs = tokenizer(
        claim,
        evidence,
        return_tensors="pt",
        truncation="only_second",
        max_length=512,
    )

    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1)[0]

    scores = {
        LABELS[i]: float(probabilities[i])
        for i in range(len(LABELS))
    }

    predicted_id = int(torch.argmax(probabilities).item())
    predicted_label = LABELS[predicted_id]

    return VerificationResult(
        label=predicted_label,
        confidence=scores[predicted_label],
        scores=scores,
    )

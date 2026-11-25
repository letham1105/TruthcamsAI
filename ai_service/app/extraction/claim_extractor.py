from pathlib import Path

from ai_service.app.llm.gemini_provider import get_gemini
from ai_service.app.extraction.json_parser import safe_json_from_model
from ai_service.app.extraction.claim_schema import validate_claims_schema
from ai_service.app.utils.text_utils import safe_error
from ai_service.app.utils.logging_config import get_logger


logger = get_logger(__name__)

PROMPT_PATH = (
    Path(__file__).parent
    / "prompts"
    / "claim_extraction.txt"
)

SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


def extract_claims(input_text, max_new_tokens=2048):
    """
    Extract verifiable claims from input text using Gemini API.

    Args:
        input_text: Original text to analyze.
        max_new_tokens: Maximum number of output tokens.

    Returns:
        Validated claims dictionary.
    """

    if not isinstance(input_text, str) or not input_text.strip():
        raise ValueError("input_text cannot be empty.")

    try:
        # 1. Get Gemini provider
        provider = get_gemini()

        response_text = provider.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=input_text.strip(),
            max_output_tokens=max_new_tokens,
        )

        logger.warning("Gemini raw response: %s", response_text[:3000])

        parsed = safe_json_from_model(response_text)

        # 3. Parse JSON response
        parsed = safe_json_from_model(response_text)

        # 4. Validate output schema
        result = validate_claims_schema(
            parsed,
            original_text=input_text.strip()
        )

        logger.info(
            "Extracted %d claims using Gemini",
            len(result["claims"])
        )

        return result

    except Exception as exc:
        logger.exception("Claim extraction failed")

        raise RuntimeError(
            f"Claim extraction failed: {safe_error(exc)}"
        ) from exc
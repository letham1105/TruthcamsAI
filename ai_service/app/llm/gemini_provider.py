import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from ai_service.app.utils.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)


class GeminiProvider:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please check your .env file."
            )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite"
        )

        self.client = genai.Client(api_key=api_key)

        logger.info("Initialized Gemini provider: %s", self.model)

    def generate(
        self,
        system_prompt,
        user_prompt,
        max_output_tokens=2048
    ):
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=max_output_tokens,
            ),
        )

        response_text = response.text

        if not response_text:
            raise ValueError("Gemini returned an empty response.")

        return response_text


_provider = None


def get_gemini():
    global _provider

    if _provider is None:
        _provider = GeminiProvider()

    return _provider
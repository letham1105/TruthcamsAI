import json
import re

def safe_json_from_model(text):
    """Parse one JSON object from a model response; tolerate fences and Qwen think tags."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Model response is empty.")
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.S).strip()
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char == "{":
            try:
                parsed, _ = decoder.raw_decode(text[index:])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
    raise ValueError("No valid JSON object found in model response.")

from datetime import datetime, timezone

from ai_service.app.input.ocr import extract_text_from_image
from ai_service.app.input.url_extractor import extract_text_from_url
from ai_service.app.utils.text_utils import safe_error

def process_input(user_input, input_type="text"):
    """Return original input and extracted text separately."""
    input_type = str(input_type).lower().strip()
    output = {
        "input_type": input_type,
        "original_input": user_input if input_type != "image" or isinstance(user_input, str) else "<PIL.Image.Image>",
        "extracted_text": "",
        "metadata": {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "error": None,
        },
    }
    try:
        if input_type == "text":
            if not isinstance(user_input, str) or not user_input.strip():
                raise ValueError("Text input cannot be empty.")
            output["extracted_text"] = user_input.strip()
            output["metadata"]["status"] = "success"

        elif input_type == "image":
            text, image_ref = extract_text_from_image(user_input)
            output["extracted_text"] = text
            output["metadata"].update({
                "image_ref": image_ref,
                "status": "success" if text else "partial",
            })
            if not text:
                output["metadata"]["error"] = "OCR returned empty text."

        elif input_type == "url":
            page = extract_text_from_url(user_input)
            output["extracted_text"] = page["text"]
            output["metadata"].update({
                "title": page["title"],
                "final_url": page["final_url"],
                "status": page["status"],
                "error": page["error"],
            })
        else:
            raise ValueError("input_type must be one of: text, image, url")

    except Exception as exc:
        output["metadata"]["error"] = safe_error(exc)

    return output

from pathlib import Path
from PIL import Image
import pytesseract

from ai_service.app.config import OCR_LANGUAGE, OCR_CONFIG
from ai_service.app.utils.logging_config import get_logger

logger = get_logger(__name__)

def extract_text_from_image(image_input, lang=OCR_LANGUAGE, config=OCR_CONFIG):
    if isinstance(image_input, Image.Image):
        image = image_input.convert("RGB")
        image_ref = "<PIL.Image.Image>"
    else:
        image_ref = str(image_input)
        image_path = Path(image_ref)
        if not image_path.is_file():
            raise FileNotFoundError(f"Image not found: {image_ref}")
        with Image.open(image_path) as source:
            image = source.convert("RGB")

    text = pytesseract.image_to_string(image, lang=lang, config=config).strip()
    logger.info("OCR completed; extracted %d characters", len(text))
    return text, image_ref

from io import BytesIO
from pathlib import Path
import requests
from PIL import Image

from ai_service.app.config import SERPAPI_API_KEY

def prepare_jpeg(image, max_bytes=450 * 1024):
    quality = 90
    while quality >= 30:
        buffer = BytesIO()
        image.convert("RGB").save(
            buffer, format="JPEG", quality=quality, optimize=True
        )
        image_bytes = buffer.getvalue()
        if len(image_bytes) <= max_bytes:
            return image_bytes
        quality -= 10
    raise ValueError("Unable to compress image below size limit.")

def search_google_lens(image_path, serpapi_key=None, timeout=60):
    serpapi_key = serpapi_key or SERPAPI_API_KEY
    if not serpapi_key:
        raise ValueError("SERPAPI_API_KEY is required.")
    image_path = Path(image_path)
    if not image_path.is_file():
        raise FileNotFoundError(str(image_path))

    with Image.open(image_path) as image:
        image_bytes = prepare_jpeg(image)

    upload = requests.post(
        "https://serpapi.com/image",
        data={"api_key": serpapi_key},
        files={"image": ("screenshot.jpg", image_bytes, "image/jpeg")},
        timeout=timeout,
    )
    upload.raise_for_status()
    image_id = upload.json().get("image_id")
    if not image_id:
        raise RuntimeError("SerpApi did not return image_id.")

    response = requests.get(
        "https://serpapi.com/search.json",
        params={
            "engine": "google_lens", "image_id": image_id,
            "api_key": serpapi_key, "hl": "vi", "country": "vn",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("visual_matches", [])

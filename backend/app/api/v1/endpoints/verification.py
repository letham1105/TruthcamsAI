from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError

from backend.app.db.database import get_db
from backend.app.schemas.verification import (
    VerificationRequest,
    VerificationSessionResponse,
    VerificationHistoryResponse,
    DeleteVerificationResponse,
)
from backend.app.services.verification_service import analyze_text
from backend.app.repositories.verification_repository import (
    get_session,
    get_history,
    count_history,
    delete_session,
)

from ai_service.app.input.ocr import extract_text_from_image
from ai_service.app.input.ocr_cleaner import clean_ocr_text

router = APIRouter(
    prefix="/verification",
    tags=["Verification"],
)


MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/ocr")
async def extract_image_text(
    file: UploadFile = File(...),
):
    """
    Extract and clean Vietnamese and English text from an uploaded image.
    """

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image.",
        )

    image_bytes = await file.read(MAX_IMAGE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB.",
        )

    try:
        image = Image.open(BytesIO(image_bytes))
        image.verify()

        image = Image.open(BytesIO(image_bytes))
        image = image.convert("RGB")

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image file.",
        )

    try:
        # 1. Extract raw OCR text
        raw_text, _ = extract_text_from_image(image)

        # 2. Clean OCR noise
        cleaned_text = clean_ocr_text(raw_text)

        # 3. Return cleaned text for UI
        return {
            "filename": file.filename,
            "text": cleaned_text,
            "raw_text": raw_text,
            "character_count": len(cleaned_text),
            "raw_character_count": len(raw_text),
            "status": "success" if cleaned_text.strip() else "empty",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Text extraction failed.",
        ) from exc

@router.post(
    "/analyze",
    response_model=VerificationSessionResponse,
)
def analyze(
    request: VerificationRequest,
    db: Session = Depends(get_db),
):
    return analyze_text(
        db=db,
        text=request.text,
    )


@router.get(
    "/history",
    response_model=VerificationHistoryResponse,
)
def history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    items = get_history(
        db=db,
        limit=limit,
        offset=offset,
    )

    total = count_history(db=db)

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/{session_id}",
    response_model=VerificationSessionResponse,
)
def get_verification(
    session_id: int,
    db: Session = Depends(get_db),
):
    verification_session = get_session(
        db=db,
        session_id=session_id,
    )

    if verification_session is None:
        raise HTTPException(
            status_code=404,
            detail="Verification session not found.",
        )

    return verification_session


@router.delete(
    "/{session_id}",
    response_model=DeleteVerificationResponse,
)
def delete_verification(
    session_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_session(
        db=db,
        session_id=session_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Verification session not found.",
        )

    return {
        "message": "Verification session deleted successfully."
    }
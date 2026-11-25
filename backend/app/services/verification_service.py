
from sqlalchemy.orm import Session

from ai_service.app.pipeline import run_search_pipeline
from ai_service.app.utils.url_utils import is_http_url

from backend.app.repositories.verification_repository import (
    create_session,
    update_session,
)


def detect_input_type(text: str) -> str:
    text = text.strip()

    if is_http_url(text):
        return "url"

    return "text"


def analyze_text(
    db: Session,
    text: str,
    user_id: int | None = None,
):
    text = text.strip()
    input_type = detect_input_type(text)

    # 1. Create session
    verification_session = create_session(
        db=db,
        original_input=text,
        input_type=input_type,
        user_id=user_id,
    )

    session_id = verification_session.id

    # 2. Run AI pipeline
    try:
        result = run_search_pipeline(
            user_input=text,
            input_type=input_type,
        )

        pipeline_status = result.get("pipeline_status", "failed")

        if pipeline_status not in ("success", "partial", "failed"):
            pipeline_status = "failed"

        errors = result.get("errors", [])
        error_message = None

        if pipeline_status == "failed":
            error_message = str(errors) if errors else "Pipeline failed."

        # 3. Save result
        verification_session = update_session(
            db=db,
            session_id=session_id,
            status=pipeline_status,
            result=result,
            error=error_message,
        )

        return verification_session

    except Exception as exc:
        error_message = str(exc)

        failure_result = {
            "pipeline_status": "failed",
            "errors": [
                {
                    "stage": "pipeline",
                    "error": error_message,
                }
            ],
        }

        verification_session = update_session(
            db=db,
            session_id=session_id,
            status="failed",
            result=failure_result,
            error=error_message,
        )

        return verification_session

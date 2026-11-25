from sqlalchemy.orm import Session

from backend.app.models.verification_session import VerificationSession


def create_session(
    db: Session,
    original_input: str,
    input_type: str = "text",
    user_id: int | None = None,
):
    verification_session = VerificationSession(
        original_input=original_input,
        input_type=input_type,
        user_id=user_id,
        status="processing",
    )

    db.add(verification_session)
    db.commit()
    db.refresh(verification_session)

    return verification_session


def update_session(
    db: Session,
    session_id: int,
    status: str,
    result: dict | None = None,
    error: str | None = None,
):
    verification_session = get_session(db, session_id)

    if verification_session is None:
        return None

    verification_session.status = status
    verification_session.result = result
    verification_session.error = error

    db.commit()
    db.refresh(verification_session)

    return verification_session


def get_session(db: Session, session_id: int):
    return (
        db.query(VerificationSession)
        .filter(VerificationSession.id == session_id)
        .first()
    )


def get_history(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    user_id: int | None = None,
):
    query = db.query(VerificationSession)

    if user_id is not None:
        query = query.filter(
            VerificationSession.user_id == user_id
        )

    return (
        query.order_by(VerificationSession.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def count_history(
    db: Session,
    user_id: int | None = None,
):
    query = db.query(VerificationSession)

    if user_id is not None:
        query = query.filter(
            VerificationSession.user_id == user_id
        )

    return query.count()


def delete_session(db: Session, session_id: int):
    verification_session = get_session(db, session_id)

    if verification_session is None:
        return False

    db.delete(verification_session)
    db.commit()

    return True

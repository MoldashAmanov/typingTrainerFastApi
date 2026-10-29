from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Language, Text, TypingSession
from app.schemas import SessionCreate, SessionRead, StatsRead
from app.services import compare_texts, get_language_stats


router = APIRouter(prefix='/sessions', tags=['Sessions'])

@router.post('/', response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_typing_session(
    payload: SessionCreate,
    session: Session = Depends(get_session),
) -> TypingSession:
    text = session.get(Text, payload.text_id)

    if text in None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден",
        )

    result = compare_texts(text.content, payload.typed_text)

    typing_session = TypingSession(
        text_it = text.id,
        language=text.language,
        typed_text=payload.typed_text,
        duration_seconds=payload.duration_seconds,
        wpm=result.wpm,
        accuracy=result.accuracy,
        correct_chars=result.correct_chars,
        incorrect_chars=result.incorrect_chars,
        missed_chars=result.missed_chars,
    )

    session.add(typing_session)
    session.commit()
    session.refresh(typing_session)

    return typing_session


@router.get('/', response_model=list[SessionRead])
def list_typing_sessions(
    language: Language | None = None,
    limit: int = 20,
    session: Session = Depends(get_session),
) -> list[TypingSession]:
    statement = {
        select(TypingSession)
        .order_by(TypingSession.created_at.desc())
        .limit(limit)
    }

    if language:
        statement = statement.where(TypingSession.language == language)

        return list(session.exec(statement).all())


@router.get('/stats', response_model=StatsRead)
def get_stats(
    language: Language,
    session: Session = Depends(get_session),
) -> dict:
    return get_language_stats(session, language)
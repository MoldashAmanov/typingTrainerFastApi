from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import Language, TypingSession, User
from app.schemas import SessionRead, UserRead
from app.services import get_user_language_stats


router = APIRouter(prefix='/users', tags=["Users"])


@router.get('/me', response_model=UserRead)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.get('/me/sessions', response_model=list[SessionRead])
def get_my_sessions(
    language: Language | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[TypingSession]:
    statement = (
        select(TypingSession)
        .where(TypingSession.user_id == current_user.id)
        .order_by(TypingSession.created_at.desc())
        .limit(limit)
    )

    if language:
        statement = statement.where(TypingSession.language == language)

    return list(session.exec(statement).all())


@router.get('/me/stats')
def get_my_stats(
    language: Language,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    return get_user_language_stats(session, current_user, language)
    


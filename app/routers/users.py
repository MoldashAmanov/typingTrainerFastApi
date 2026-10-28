from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import Language, TypingSession, User
from app.schemas import SessionRead, UserRead
from app.services import get_user_language_stats


router = APIRouter(prefix='/users', tags=["Users"])


@router.get('/me', response_model=UserRead)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.get('/me/sessions', response_model=list[SessionRead])
async def get_my_sessions(
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


@router.get('/me/stats')
async def get_my_stats(
    language: Language,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    sessions = session.exec(
        select(TypingSession).where(
            TypingSession.user_id == user.id,
            TypingSession.language == language,
        )
    ).all()

    if not sessions:
        return {
            'language': language,
            'total_sessions': 0,
            'average_wpm': 0.0,
            'best_wpm': 0.0,
            'average_accuracy': 0.0,
            'total_practice_seconds': 0.0,
        }

    return {
        'language': language,
        'total_sessions': len(sessions),
        'average_wpm': round(sum(s.wpm for s in sessions) / len(sessions), 2),
        'best_wpm': round(max(s.wpm for s in sessions), 2),
        'average_accuracy': round(
            sum(s.accuracy for s in sessions) / len(sessions), 2
        ),
        'total_practice_seconds': round(
            sum(s.duration_seconds for s in sessions), 2
        ),
    }

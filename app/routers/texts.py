from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Language, Text
from app.schemas import TextCreate, TextRead
from app.services import get_random_text

router = APIRouter(prefix='/texts', tags=['Texts'])

@router.post('/', response_model=TextRead, status_code=status.HTTP_201_CREATED)
async def create_text(
    payload: TextCreate,
    session: Session = Depends(get_session),
) -> Text:
    text = Text.model_validate(payload)
    session.add(text)
    session.commit()
    session.refresh(text)
    return text


@router.get('/', response_model=list[TextRead])
async def list_texts(
    language: Language | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[Text]:
    statement = select(Text).order_by(Text.created_at.desc()).limit(limit)

    if language:
        statement = statement.where(Text.language == language)

    return list(session.exec(statement).all())


@router.get('/random', response_model=TextRead)
async def get_random_practice_text(
    language: Language,
    difficulty: int | None = Query(default=None, ge=1, le=5),
    session: Session = Depends(get_session),
) -> Text:
    text = get_random_text(session, language, difficulty)

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдено ни одного текста для этого языка и сложности")

    return text


@router.delete('/{text_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_text(
    text_id: int, 
    session: Session = Depends(get_session)
) -> None:
    text = session.get(Text, text_id)

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден",
        )

    session.delete(text)
    session.commit()
from fastapi import (
    APIRouter, Depends, 
    HTTPException, Query, status,
    File, UploadFile,
)
from sqlmodel import Session, select
from app.database import get_session
from app.models import Language, Text, User
from app.schemas import TextCreate, TextRead, TextImportResult
from app.services import get_random_text
from app.text_import import parse_text_file
from app.dependencies import get_current_user
from pathlib import Path
from app.config import (
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES,
    UPLOAD_DIR,
)


router = APIRouter(prefix='/texts', tags=['Texts'])

@router.post('/', response_model=TextRead, status_code=status.HTTP_201_CREATED)
def create_text(
    payload: TextCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Text:
    text = Text(
        owner_id=current_user.id,
        language=payload.language,
        content=payload.content,
        difficulty=payload.difficulty,
        source='manual',
    )

    session.add(text)
    session.commit()
    session.refresh(text)
    return text


@router.post(
        '/import',
        response_model=TextImportResult,
        status_code=status.HTTP_201_CREATED,)
async def import_texts_from_file(
    language: Language,
    difficulty: int = Query(default=1, ge=1, le=5),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TextImportResult:
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Только формата .txt или .md",
        )

    raw_bytes = await file.read()

    if len(raw_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл слишком большой. Максимальный размер не больше 2 MB"
        )

    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть UTF-8"
        ) from exc

    parsed = parse_text_file(content)

    if not parsed.texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В загруженном файле не найдено ни одной валидной строки"
        )

    created = 0

    for line in parsed.texts:
        text = Text(
            owner_id=current_user.id,
            language=language,
            content=line,
            difficulty=difficulty,
            source=f"file:{file.filename}",
        )
        session.add(text)
        created += 1

    session.commit()

    return TextImportResult(
        created_text=created,
        skipped_lines=parsed.skipped_lines,
        language=language,
        source_filename=file.filename or "uploaded_file",
    )


@router.get('/random', response_model=TextRead)
def get_random_pracice_text(
    language: Language,
    difficulty: int | None = Query(default=None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session,)
) -> Text:
    statement = select(Text).where(Text.language == language)

    if difficulty is not None:
        statement = statement.where(Text.difficulty == difficulty)

    statement = statement.where(
        (Text.owner_id == current_user.id) | (Text.owner_id.is_(None))
    )

    texts = session.exec(statement).all()

    if not texts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет доступных текстов",
        )

    import secrets
    
    return secrets.choice(texts)  


@router.get('/', response_model=list[TextRead])
def list_texts(
    language: Language | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[Text]:
    statement = select(Text).order_by(Text.created_at.desc()).limit(limit)

    if language:
        statement = statement.where(Text.language == language)

    return list(session.exec(statement).all())


@router.get('/random', response_model=TextRead)
def get_random_practice_text(
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
def delete_text(
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
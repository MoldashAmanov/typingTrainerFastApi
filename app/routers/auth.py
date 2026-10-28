from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED,)
async def register(
    payload: UserCreate,
    session: Session = Depends(get_session),
) -> User:
    existing_email = session.exec(
        select(User).where(User.email == payload.email)
    ).first()

    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такой email уже есть")

    existing_username = session.exec(
        select(User).where(User.username == payload.username)
    ).first()

    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже зарегестрирован")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post('/token', response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный пароль или имя пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_minutes=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).seconds // 60,
    )

    return Token(access_token=access_token)


@router.get('/me', response_model=UserRead)
async def read_current_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

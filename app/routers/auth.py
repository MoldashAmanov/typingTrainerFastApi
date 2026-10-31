from datetime import timedelta
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/register',
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
) -> User:
    # Валидируем через Pydantic-схему — сохраняем единый источник правды
    payload = UserCreate(email=email, username=username, password=password)

    # Одна проверка на оба конфликта (email или username)
    conflict = session.exec(
        select(User).where(
            (User.email == payload.email)
            | (User.username == payload.username)
        )
    ).first()

    if conflict:
        # Даём точное сообщение в зависимости от того, что совпало
        if conflict.email == payload.email:
            detail = "Такой email уже есть"
        else:
            detail = "Пользователь с таким именем уже зарегистрирован"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Автологин: выдаём токен и кладём в cookie
    access_token = create_access_token(
        subject=str(user.id),
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        samesite='lax',
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.post('/token', status_code=status.HTTP_303_SEE_OTHER)
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if user is None or not verify_password(password, user.hashed_password):
        # Ошибка → обратно на страницу логина с флагом
        return RedirectResponse(
            url='/login?error=1',
            status_code=status.HTTP_303_SEE_OTHER,
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    response = RedirectResponse(
        url='/',
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        samesite='lax',
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get('/me', response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

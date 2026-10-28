from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from app.database import get_session
from app.models import User
from app.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
) -> User:
    creadentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)

    if user_id is None:
        raise creadentials_error

    user = session.get(User, int(user_id))

    if user is None or not user.is_active:
        raise creadentials_error

    return user

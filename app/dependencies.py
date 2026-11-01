from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.database import get_session
from app.models import User
from app.security import decode_access_token


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    token = request.cookies.get("access_token")

    credentials_error = HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"Location": "/auth/login"},
    )

    if not token:
        raise credentials_error

    user_id = decode_access_token(token)

    if user_id is None:
        raise credentials_error

    user = session.get(User, int(user_id))

    if user is None or not user.is_active:
        raise credentials_error

    return user
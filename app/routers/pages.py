from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import Language, TypingSession, User
from app.services import get_user_language_stats

router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory="app/templates")

def render(
        request: Request,
        template_name: str,
        context: dict | None=None,
        status_code: int = 200,
):
    base_context = {
        'request': request, 
        'current_user': getattr(request.state, 'current_user', None),
        'messages': getattr(request.state, 'messages', []),
    }

    if context:
        base_context.update(context)

    return templates.TemplateResponse(
        name=template_name,
        context=base_context,
        status_code=status_code,
    )


@router.get('/')
def index_page(request: Request):
    return render(request, 'index.html')


@router.get('/register')
def register_page(request: Request):
    return render(request, 'register.html')


@router.get('/login')
def login_page(request: Request):
    return render(request, 'login.html')


@router.get('/practice')
def practice_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return render(request, 'practice.html')


@router.get('/texts/import')
def import_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return render(request, 'texts/import.html')


@router.get('/profile')
def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    stats = get_user_language_stats(session, current_user, Language.english)

    sessions = session.exec(
        select(TypingSession)
        .where(TypingSession.user_id == current_user.id)
        .order_by(TypingSession.created_at.desc())
        .limit(10)
    ).all()

    return render(
        request,
        'profile.html',
        context= {
            'stats': stats,
            'sessions': sessions,
        },
    )
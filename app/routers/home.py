from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ..database import check_email, get_counts


router = APIRouter()
router = APIRouter(prefix='/home', tags=['home'])

templates = Jinja2Templates(directory='templates')


@router.get('/')
def welcome(request: Request):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
    
    counts = get_counts()
    
    return templates.TemplateResponse(
        request=request,
        name='Home.html',
        context={'user': user, 'counts':counts}
    )

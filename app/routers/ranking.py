from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ..database import get_visible_rank

router = APIRouter()
router = APIRouter(prefix='/ranking', tags=['ranking'])

templates = Jinja2Templates(directory='templates')


@router.get('/')
def rank(request: Request):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
      
    rank = get_visible_rank()
    
    return templates.TemplateResponse(
        request=request,
        name='Ranking.html',
        context={'rank': rank}
    )

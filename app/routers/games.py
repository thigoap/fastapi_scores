from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse


router = APIRouter()
router = APIRouter(prefix='/games', tags=['games'])

templates = Jinja2Templates(directory='templates')


@router.get('/')
def games(request: Request):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
    
    return templates.TemplateResponse(
        name='Games.html',
            request=request,
            context={'request': request}
    )


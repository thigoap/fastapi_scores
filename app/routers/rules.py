from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse


router = APIRouter()
router = APIRouter(prefix='/rules', tags=['rules'])

templates = Jinja2Templates(directory='templates')


@router.get('/')
def rules(request: Request):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
    
    #return templates.TemplateResponse(
    #    name='Rules.html',
    #    context={'request': request}
    #)
    return templates.TemplateResponse(
        request=request,
        name='Rules.html',
        context={'request': request}
    )

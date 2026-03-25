from fastapi import APIRouter, Form
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ..database import get_profile_info, get_guesses, record_guesses, update_user_guesses, get_match_status


router = APIRouter()
router = APIRouter(prefix='/guesses', tags=['guesses'])

templates = Jinja2Templates(directory='templates')


@router.get('/')
def games(request: Request):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
     
    return templates.TemplateResponse(
        request=request,
        name='Guesses.html',
        context={'request': request}
    )

@router.get('/{page_id}')
def games(request: Request, page_id: str):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
    
    user_email = user['email']

    profile_info = get_profile_info(user_email)
    if profile_info is None:
        message = 'Acesse seu perfil para criar seu nome de usuário antes de palpitar.'
    else:
        message = ''

    guesses = get_guesses(user_email)
    match_status = get_match_status()
    
    return templates.TemplateResponse(
        request=request,
        name='/guesses/' + page_id + '.html',
        context={'guesses': guesses, 'message': message, 'match_status': match_status}
    )

@router.post('/{page_id}')
async def update(request: Request, page_id: str):
    user = request.session.get('user')
    
    if not user:
        return RedirectResponse('/')
    
    user_email = user['email']

    profile_info = get_profile_info(user_email)
    if profile_info is None:
        message = 'Acesse seu perfil para criar seu nome de usuário antes de palpitar.'
        error_message = 'Palpite não registrado. Acesse seu perfil para criar seu nome de usuário antes de palpitar.'
    else:
        message = ''
        error_message = ''

        form_data = await request.form()
        guesses = dict(form_data)
        record_guesses(user_email, guesses)
        update_user_guesses(user_email)

    # get updated data from the database for the new page
    db_guesses = get_guesses(user_email)
    match_status = get_match_status()

    return templates.TemplateResponse(
        request=request,
        name='/guesses/' + page_id + '.html',
        context={'guesses': db_guesses, 'message': message, 'error_message': error_message, 'match_status': match_status}
    )

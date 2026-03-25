from fastapi import APIRouter, Form
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ..database import get_profile_info, check_email, check_username, signup_user, update_user, delete_email

router = APIRouter()
router = APIRouter(prefix='', tags=['profile'])

templates = Jinja2Templates(directory='templates')


@router.get('/profile')
def profile(request: Request):
    user = request.session.get('user')

    if not user:
        return RedirectResponse('/')
    
    user_email = user['email'] 
    profile_info = get_profile_info(user_email)
    if profile_info is None:
        profile_data = { 'username': '', 'invisible': False }
    else:
        profile_data = profile_info.data

    return templates.TemplateResponse(
        request=request,
        name='Profile.html',
        context={'profile_data': profile_data, 'email': user_email}
    )


@router.post('/profile')
async def update(request: Request, username: str = Form(...), invisible: bool = Form(False)):
    user = request.session.get('user')
    
    user_email = user['email']

    email_in_db = check_email(user_email)
    user_in_db = check_username(username)

    profile_info = get_profile_info(user_email)
    if profile_info is None:
        profile_data = { 'username': '', 'invisible': False }
    else:
        profile_data = profile_info.data

    if not email_in_db and not user_in_db:
        signup_user(user['email'], username, invisible)
        return RedirectResponse('profile', status_code=303)
    
    if not email_in_db and user_in_db:
        message = 'Nome de usuário já existe.'
        return templates.TemplateResponse(
            request=request,
            name='Profile.html', 
            context={'profile_data': profile_data, 'email': user_email, 'message': message}
        )   
    
   
    if profile_data['username'] == username and profile_data['invisible'] == invisible:
        message = 'Nenhuma alteração foi feita.'
        return templates.TemplateResponse(
            request=request,
            name='Profile.html', 
            context={'profile_data': profile_data, 'email': user_email, 'message': message}
        )
    
    
    if profile_data['username'] == username and profile_data['invisible'] != invisible:
        update_user(user['email'], username, invisible)
        return RedirectResponse('profile', status_code=303)
    
    if profile_data['username'] != username:
        user_in_db = check_username(username)
        print('user no db')
        if user_in_db:
            message = 'Nome de usuário já existe.'
            return templates.TemplateResponse(
                request=request,
                name='Profile.html', 
                context={'profile_data': profile_data, 'email': user_email, 'message': message}
            )  
                  
        else:
            print('user novo')
            update_user(user['email'], username, invisible)
            return RedirectResponse('profile', status_code=303)
    

@router.post('/delete')
async def delete(request: Request, deleteemail: str = Form(...),):
    user = request.session.get('user')

    user_email = user['email'] 
    profile_info = get_profile_info(user_email)
    if profile_info is None:
        profile_data = { 'username': '', 'invisible': False }
    else:
        profile_data = profile_info.data

    if user['email'] != deleteemail:
        delete_message = 'Email incorreto.'
        return templates.TemplateResponse(
            request=request,
            name='Profile.html', 
            context={'profile_data': profile_data, 'email': user_email, 'delete_message': delete_message}
        ) 
    else:
        delete_email(user['email'])
        return RedirectResponse('logout', status_code=303)


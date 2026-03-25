from fastapi import APIRouter, HTTPException, status, Form
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI_ENDPOINT

from ..database import check_email, check_username, signup_user

router = APIRouter()
router = APIRouter(prefix='', tags=['access'])

templates = Jinja2Templates(directory='templates')

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_uri': GOOGLE_REDIRECT_URI_ENDPOINT
    }
)

#############################################
# GOOGLE
#############################################
@router.get('/login')
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            request=request,
            name='Error.html',
            context={'error': e.error}
        )
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        return RedirectResponse('home')


@router.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')


""" @router.get('/username')
async def username(request: Request):
    email_in_db = check_email
    if email_in_db:
        print('email exists, redirect to home')
        return RedirectResponse('home', status_code=303)
    else:
        return templates.TemplateResponse(
            name='Username.html',
            context={'request': request}
    )


@router.post('/username')
async def username(request: Request, username: str = Form(...), invisible: bool = Form(False)):
    user = request.session.get('user')

    user_in_db = check_username(username)
    if user_in_db:
        message = 'Nome de usuário já existe.'
        return templates.TemplateResponse(
            name='Username.html', 
            context={'request': request, 'message': message}
        ) 
    else:
        signup_user(user['email'], username, invisible)
        return RedirectResponse('home', status_code=303) """


#############################################
# SUPABASE OAUTH
#############################################
from supabase.client import create_client, Client
from app.database import SUPABASE_URL, SUPABASE_KEY, SUPA_GOOGLE_REDIRECT_URI_ENDPOINT

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get('/supalogin')
async def supalogin():
    """
    Redirects the user to the Google OAuth sign-in page via Supabase.
    """
    # Supabase handles the generation of the Google OAuth URL and redirect
    auth_response = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            # Specify where you want the user to be redirected AFTER Google auth
            "redirect_to": SUPA_GOOGLE_REDIRECT_URI_ENDPOINT
        }
    })
    # The response contains the URL to redirect the user to Google's OAuth screen
    print('url', auth_response.url)
    return RedirectResponse(url=auth_response.url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/auth/v1/callback")
async def callback(request: Request):
    """
    Handles the callback from Supabase after successful Google authentication.
    """
    # Extract the 'code' from the query parameters, which is provided by Supabase
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code not found")

    # Exchange the authorization code for a user session (PKCE flow)
    # This must match the redirect_to URL used in the initial sign_in_with_oauth call
    session_response = supabase.auth.exchange_code_for_session({'auth_code': code})
    user = session_response.user

    if user:
        #print(user)
        return {"message": f"Welcome, {user.email}! Authentication successful."}
        #return RedirectResponse('home')
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
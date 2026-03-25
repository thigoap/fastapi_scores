from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

from .config import SESSION_SECRET_KEY

from app.routers import access, home, rules, games, guesses, ranking, profile

from .database import get_counts

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    https_only=False, # Set to True in production to ensure cookies are only sent over HTTPS
    max_age=600) 

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(access.router)
app.include_router(home.router)
app.include_router(rules.router)
app.include_router(games.router)
app.include_router(guesses.router)
app.include_router(ranking.router)
app.include_router(profile.router)


templates = Jinja2Templates(directory="templates")


@app.get('/')
def index(request: Request):
    user = request.session.get('user')
    # if user:
    #     return RedirectResponse('Home')
    counts = get_counts()

    return templates.TemplateResponse(
        request=request,
        name='OauthLogin.html',
        context={'counts':counts}
    )

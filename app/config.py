import os
from dotenv import load_dotenv


load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_REDIRECT_URI_ENDPOINT = os.environ.get('GOOGLE_REDIRECT_URI_ENDPOINT', None)

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY', None)
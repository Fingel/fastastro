from fastapi import FastAPI, Depends
from logging.config import dictConfig

from .config import settings, log_config
from .sources.views import router as sources_router
from .auth.views import router as auth_router
from .auth.security import get_current_active_user
from .auth.models import User
from .util.mail import send_mail


dictConfig(log_config)

app = FastAPI()
app.include_router(sources_router)
app.include_router(auth_router)


@app.get('/')
async def root():
    return {'message': 'hello', 'db_string': settings.db_string, 'admin_email': settings.admin_email}


@app.get('/secure/')
async def secure(user: User = Depends(get_current_active_user)):
    return {'user': user.email}


@app.get('/testmail/')
async def test_mail():
    await send_mail('Test Subject From View', 'Hi From View Should go to console', 'austin@m51.io',)
    return {'message': 'hope it sends'}

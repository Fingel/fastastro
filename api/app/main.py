from fastapi import FastAPI, Depends


from .config import settings
from .sources.views import router as sources_router
from .auth.views import router as auth_router
from .auth.security import oauth2_scheme


app = FastAPI()
app.include_router(sources_router)
app.include_router(auth_router)


@app.get('/')
async def root():
    return {'message': 'hello', 'db_string': settings.db_string, 'admin_email': settings.admin_email}


@app.get('/secure/')
async def secure(token: str = Depends(oauth2_scheme)):
    return {'token': token}

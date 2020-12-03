from fastapi import FastAPI

from .config import settings
from .sources.views import router as sources_router


app = FastAPI()
app.include_router(sources_router)


@app.get('/')
async def root():
    return {'message': 'hello', 'db_string': settings.db_string, 'admin_email': settings.admin_email}

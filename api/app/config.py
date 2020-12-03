from pydantic import BaseSettings


class Settings(BaseSettings):
    db_string: str = 'postgresql://postgres:postgres@127.0.0.1:5432/fastastro'
    admin_email: str = 'austin@m51.io'
    srid: int = 4035


settings = Settings()

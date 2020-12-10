from pydantic import BaseSettings


class Settings(BaseSettings):
    db_string: str = 'postgresql://postgres:postgres@127.0.0.1:5432/fastastro'
    admin_email: str = 'austin@m51.io'
    srid: int = 4035
    secret_key: str
    access_token_expire_minutes: int = 30

    # Mail Settings
    email_backend: str = 'ConsoleEmailBackend'
    smtp_host: str = '127.0.0.1'
    smtp_port: int = 8025
    from_address: str = 'root@localhost'


settings = Settings()

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "app": {"handlers": ["default"], "level": "DEBUG"},
    },
}

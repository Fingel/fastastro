import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app
from app.auth.models import User
from app.database import Base, get_db
from app.auth.security import get_current_active_user


@pytest.fixture(scope="session")
def engine():
    DATABASE_URL = 'postgresql://postgres:postgres@127.0.0.1:5432/fastastro_test'
    engine = create_engine(DATABASE_URL)
    engine.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    return engine


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    app.dependency_overrides[get_db] = lambda: session

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def current_user(db):
    """
    A basic user which will be injected as the currently logged in user
    """
    test_user = {
        'email': 'test@example.com',
        'first_name': 'Joe',
        'last_name': 'Test',
        'hashed_password': '',
        'is_active': True,
        'is_superuser': False,
        'email_verified': True
    }

    db_user = User(**test_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    app.dependency_overrides[get_current_active_user] = lambda: db_user
    yield db_user
    app.dependency_overrides = {}

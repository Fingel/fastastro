from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import exists

from app.main import app
from app.auth.models import User
from app.auth.security import hash_password

client = TestClient(app)


class TestAuth:
    def test_register(self, db):
        data = {
            'email': 'register@example.com',
            'first_name': 'Bilbo',
            'last_name': 'Taggins',
            'password': 'testing123'
        }

        response = client.post(app.url_path_for('register'), json=data)
        assert response.json()['email'] == data['email']
        assert response.status_code == status.HTTP_201_CREATED
        assert db.query(exists().where(User.email == data['email'])).scalar()

    def test_login(self, db):
        password = 'secretsaregood'
        hashed_password = hash_password(password)
        new_user = User(
            email='hi@example.com', first_name='hi', last_name='there', hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()

        data = {
            'username': 'hi@example.com',
            'password': password
        }
        response = client.post(app.url_path_for('login'), data=data)
        assert response.status_code == 200
        assert 'access_token' in response.json()

    def test_get_me(self, current_user):
        response = client.get(app.url_path_for('read_users_me'))
        assert response.json()['email'] == current_user.email

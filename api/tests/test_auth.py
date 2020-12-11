from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import exists

from app.main import app
from app.auth.models import User
from app.auth.security import hash_password, get_email_confirmation_link, password_reset_token, verify_password
from app.util.mail import record_messages

client = TestClient(app)


class TestAuth:
    def test_register(self, db):
        data = {
            'email': 'register@example.com',
            'first_name': 'Bilbo',
            'last_name': 'Taggins',
            'password': 'testing123'
        }

        with record_messages() as outbox:
            response = client.post(app.url_path_for('register'), json=data)
            assert len(outbox) == 1
            assert 'verify' in outbox[0].get('subject').lower()

        assert response.json()['email'] == data['email']
        assert response.status_code == status.HTTP_201_CREATED
        assert db.query(exists().where(User.email == data['email'])).scalar()

    def test_register_email_taken(self, db, current_user):
        data = {
            'email': current_user.email,
            'first_name': 'Bilbo',
            'last_name': 'Taggins',
            'password': 'testing123'
        }
        with record_messages() as outbox:
            response = client.post(app.url_path_for('register'), json=data)
            assert len(outbox) == 0

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'email already exists' in response.json()['detail'].lower()

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

    def test_update_me(self, db, current_user):
        data = {
            'first_name': 'NewName'
        }
        response = client.patch(app.url_path_for('update_user_me'), json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['first_name'] == data['first_name']
        db.refresh(current_user)
        assert current_user.first_name == data['first_name']

    def test_update_password(self, db, current_user):
        current_user.hashed_password = hash_password('oldpassword')
        db.commit()
        data = {
            'current_password': 'oldpassword',
            'password': 'makeitnew'
        }
        response = client.post(app.url_path_for('update_password_me'), json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'ok'
        db.refresh(current_user)
        assert verify_password(data['password'], current_user.hashed_password)

    def test_confirm_email(self, db):
        unverified_user = User(
            email='hi@example.com', first_name='hi', last_name='there', hashed_password='nothashed'
        )
        db.add(unverified_user)
        db.commit()

        assert not unverified_user.email_verified

        confirm_link = get_email_confirmation_link(app.url_path_for('confirm_email'), unverified_user.email)

        response = client.get(confirm_link)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'ok'
        db.refresh(unverified_user)
        assert unverified_user.email_verified

    def test_request_reset_password(self, db):
        user = User(
            email='hi@example.com', first_name='forgot', last_name='password', hashed_password='anything',
            email_verified=True
        )
        db.add(user)
        db.commit()

        data = {
            'email': user.email
        }
        with record_messages() as outbox:
            response = client.post(app.url_path_for('request_password_reset'), json=data)
            assert len(outbox) == 1
            assert 'password reset' in outbox[0].get('Subject').lower()

        assert response.status_code == status.HTTP_200_OK

    def test_request_reset_password_bad_email(self, db):
        user = User(
            email='hi@example.com', first_name='forgot', last_name='password', hashed_password='anything',
            email_verified=True
        )
        db.add(user)
        db.commit()

        data = {
            'email': 'iamfishing@example.com'
        }
        with record_messages() as outbox:
            response = client.post(app.url_path_for('request_password_reset'), json=data)
            assert len(outbox) == 0

        assert response.status_code == status.HTTP_200_OK

    def test_request_reset_password_not_verified(self, db):
        user = User(
            email='hi@example.com', first_name='forgot', last_name='password', hashed_password='anything'
        )
        db.add(user)
        db.commit()

        data = {
            'email': user.email
        }
        with record_messages() as outbox:
            response = client.post(app.url_path_for('request_password_reset'), json=data)
            assert len(outbox) == 0

        assert response.status_code == status.HTTP_200_OK

    def test_reset_password(self, db):
        pass_before_reset = hash_password('beforereset')
        user = User(
            email='hi@example.com', first_name='forgot', last_name='password', hashed_password=pass_before_reset,
            email_verified=True
        )
        db.add(user)
        db.commit()

        reset_token = password_reset_token(user.email)
        data = {
            'token': reset_token,
            'password': 'afterreset'
        }
        response = client.post(app.url_path_for('password_reset_confirm'), json=data)
        assert response.status_code == status.HTTP_200_OK

        # log in with new password
        data = {
            'username': user.email,
            'password': 'afterreset'
        }
        response = client.post(app.url_path_for('login'), data=data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.json()

        # confirm cannot login with old password:
        data = {
            'username': user.email,
            'password': 'beforereset'
        }
        response = client.post(app.url_path_for('login'), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access_token' not in response.json()

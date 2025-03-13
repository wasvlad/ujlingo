import os
from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient

from main import app
from endpoints.user.register import generate_token
from unit_tests.tools import clear_database
from .register_helpers import register_user

client = TestClient(app)

class TestRegisterUser:
    def test_register_user_success(self):
        clear_database()

        response = register_user(client)

        assert response.status_code == 200
        assert response.json() == {"message": "User registered successfully"}

    def test_register_user_weak_password(self):
        clear_database()

        response = client.post("/user/register", json={
            "email": "test2@example.com",
            "password": "password123",
            "name": "Test",
            "surname": "User"
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "Password is not strong enough"}

    def test_register_user_email_already_registered(self):
        clear_database()
        response = register_user(client)
        assert response.status_code == 200

        response = register_user(client)

        assert response.status_code == 400
        assert response.json() == {"detail": "Email already registered"}


class TestConfirmEmail:
    def test_confirm_email_success(self):
        clear_database()

        register_user(client)

        token = generate_token("test@example.com", os.getenv("SECRET_KEY"))

        response = client.get(f"/user/confirm_email?token={token}")

        assert response.status_code == 200
        assert response.json() == {"message": "Email confirmed successfully"}

    def test_confirm_email_invalid_token(self):
        clear_database()

        register_user(client)

        response = client.get("/user/confirm_email?token=invalid")

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid token"}

    def test_confirm_email_expired_token(self):
        clear_database()

        register_user(client)

        token = generate_token("test@example.com", secret_key=os.getenv("SECRET_KEY"),
                               expiration_date=datetime.now(timezone.utc) - timedelta(minutes=5))

        response = client.get(f"/user/confirm_email?token={token}")

        assert response.status_code == 400
        assert response.json() == {"detail": "Token expired"}

    def test_confirm_email_invalid_email(self):
        clear_database()

        register_user(client)

        token = generate_token("invalid@example.com", secret_key=os.getenv("SECRET_KEY"))

        response = client.get(f"/user/confirm_email?token={token}")

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
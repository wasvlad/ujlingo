import os
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from endpoints.user.hashing import hash_password, verify_password
from endpoints.user.tools import generate_token
from main import app
from database.models import User, Base
from database import get_db, engine, DatabaseSession
from unit_tests.tools import clear_database


class TestRequestPasswordReset:

    @staticmethod
    def setup_method():
        clear_database()
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password"))

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_register_user_success(self, client):
        with patch("endpoints.user.register.generate_token", return_value="token"):
            response = client.post("/user/request-password-reset", json={
                "email": "test@example.com"
            })
            assert response.status_code == 200
            assert response.json() == {"message": "A password reset link has been sent."}

    def test_not_existing_user(self, client):
        with patch("endpoints.user.register.generate_token", return_value="token"):
            response = client.post("/user/request-password-reset", json={
                "email": "wrong@example.com"
            })
            assert response.status_code == 200
            assert response.json() == {"message": "A password reset link has been sent."}


class TestPasswordReset:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @staticmethod
    def setup_method():
        clear_database()
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash=hash_password("old-password1A!")))
        db.commit()

    def test_ok(self, client):

        token = generate_token("test@example.com", os.getenv("PASSWORD_RESET_KEY"))

        response = client.post(f"/user/reset-password?token={token}", json={
            "password": "new-passwordA1!"
        })

        assert response.status_code == 200
        assert response.json() == {"message": "Password reset successfully"}
        db = next(get_db())
        user = db.query(User).filter(User.email == "test@example.com").first()
        assert verify_password("new-passwordA1!", user.password_hash)
        assert not verify_password("old-password1A!", user.password_hash)

    def test_same_password(self, client):

        token = generate_token("test@example.com", os.getenv("PASSWORD_RESET_KEY"))

        response = client.post(f"/user/reset-password?token={token}", json={
            "password": "old-password1A!"
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "New password cannot be the same as the old password"}

    def test_invalid_token(self, client):

        response = client.post("/user/reset-password?token=invalid", json={
            "password": "new-passwordA1!"
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid token"}

    def test_expired_token(self, client):

        token = generate_token("test@example.com", secret_key=os.getenv("PASSWORD_RESET_KEY"),
                               expiration_date=datetime.now(timezone.utc) - timedelta(minutes=5))

        response = client.post(f"/user/reset-password?token={token}", json={
            "password": "new-passwordA1!"
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "Token expired"}

    def test_invalid_email(self, client):
        token = generate_token("invalid@example.com", secret_key=os.getenv("PASSWORD_RESET_KEY"))

        response = client.post(f"/user/reset-password?token={token}", json={
            "password": "new-passwordA1!"
        })

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    def test_weak_password(self, client):
        token = generate_token("test@example.com", secret_key=os.getenv("PASSWORD_RESET_KEY"))

        response = client.post(f"/user/reset-password?token={token}", json={
            "password": "weakpassword"
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "Password is weak"}
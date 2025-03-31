import os
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from endpoints.user.tools import generate_token
from main import app
from database.models import User, Base
from database import get_db, engine, DatabaseSession


class TestRegisterUser:

    @staticmethod
    def setup_method():
        DatabaseSession.close_all()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_register_user_success(self, client):
        with patch("endpoints.user.register.is_strong_password", return_value=True), \
             patch("endpoints.user.register.hash_password", return_value="hashed_password"), \
             patch("endpoints.user.register.generate_token", return_value="token"):
            response = client.post("/user/register", json={
                "email": "test@example.com",
                "password": "StrongPassword123!",
                "name": "Test",
                "surname": "User"
            })
            assert response.status_code == 200
            assert response.json() == {"message": "User registered successfully"}

            # Verify that the user has been added to the database
            db = next(get_db())
            added_user = db.query(User).filter(User.email == "test@example.com").first()
            assert added_user is not None
            assert added_user.email == "test@example.com"
            assert added_user.name == "Test"
            assert added_user.surname == "User"
            assert added_user.is_confirmed is False
            assert added_user.password_hash == "hashed_password"

    def test_register_user_email_uppercase_success(self, client):
        with patch("endpoints.user.register.is_strong_password", return_value=True), \
             patch("endpoints.user.register.hash_password", return_value="hashed_password"), \
             patch("endpoints.user.register.generate_token", return_value="token"):
            response = client.post("/user/register", json={
                "email": "Test@example.com",
                "password": "StrongPassword123!",
                "name": "Test",
                "surname": "User"
            })
            assert response.status_code == 200

            # Verify that the user has been added to the database
            db = next(get_db())
            added_user = db.query(User).filter(User.email == "test@example.com").first()
            assert added_user is not None
            assert added_user.email == "test@example.com"

    def test_register_user_weak_password(self, client):
        with patch("endpoints.user.register.hash_password", return_value="hashed_password"), \
             patch("endpoints.user.register.generate_token", return_value="token"):
            response = client.post("/user/register", json={
                "email": "test@example.com",
                "password": "weak_password",
                "name": "Test",
                "surname": "User"
            })
            assert response.status_code == 400
            assert response.json() == {"detail": "Password is not strong enough"}

            # Verify that the user has been added to the database
            db = next(get_db())
            added_user = db.query(User).filter(User.email == "test@example.com").first()
            assert added_user is None

    def test_register_user_email_already_registered(self, client):
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password"))
        db.commit()
        with patch("endpoints.user.register.generate_token", return_value="token"):
            response = client.post("/user/register", json={
                "email": "test@example.com",
                "password": "StrongPassword123!",
                "name": "Test",
                "surname": "User"
            })
            assert response.status_code == 400
            assert response.json() == {"detail": "Email already registered"}

            # Verify that the user has been added to the database
            db = next(get_db())
            added_user = db.query(User).filter(User.email == "test@example.com").first()
            assert added_user is not None
            assert added_user.email == "test@example.com"


class TestConfirmEmail:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @staticmethod
    def setup_method():
        DatabaseSession.close_all()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password"))
        db.commit()

    def test_confirm_email_success(self, client):

        token = generate_token("test@example.com", os.getenv("SECRET_KEY"))

        response = client.get(f"/user/confirm_email?token={token}")

        print(response.json())
        assert response.status_code == 200
        assert response.json() == {"message": "Email confirmed successfully"}
        db = next(get_db())
        user = db.query(User).filter(User.email == "test@example.com").first()
        assert user.is_confirmed is True

    def test_confirm_email_invalid_token(self, client):

        response = client.get("/user/confirm_email?token=invalid")

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid token"}

    def test_confirm_email_expired_token(self, client):

        token = generate_token("test@example.com", secret_key=os.getenv("SECRET_KEY"),
                               expiration_date=datetime.now(timezone.utc) - timedelta(minutes=5))

        response = client.get(f"/user/confirm_email?token={token}")

        assert response.status_code == 400
        assert response.json() == {"detail": "Token expired"}

    def test_confirm_email_invalid_email(self, client):
        token = generate_token("invalid@example.com", secret_key=os.getenv("SECRET_KEY"))

        response = client.get(f"/user/confirm_email?token={token}")

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
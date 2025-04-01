import os
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient

from database import get_db, engine, DatabaseSession
from database.models import Base, User, Session
from endpoints.user.tools import generate_token
from main import app
from endpoints.user.hashing import hash_password, verify_password
from unit_tests.tools import clear_database

client = TestClient(app)

class TestChangePassword:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def setup_method(self, client):
        clear_database()
        db = next(get_db())
        self.user = User(email="test@example.com", name="Test", surname="User",
                    password_hash=hash_password("Strongpassword1!"),
                    is_confirmed=True)
        db.add(self.user)
        db.commit()
        token = generate_token("test@example.com", os.getenv("SECRET_KEY"),
                               expiration_date=datetime.now(timezone.utc) + timedelta(days=30))
        self.session = Session(user_id=self.user.id, token=token)
        db.add(self.session)
        db.commit()
        db.refresh(self.session)
        db.refresh(self.user)
        db.expunge(self.session)
        db.expunge(self.user)


    def test_ok(self, client):

        response = client.post("/user/change-password", json={
            "old_password": "Strongpassword1!",
            "new_password": "new-passwordA1!",
        },
                               cookies={"session-token": self.session.token})
        assert response.status_code == 200
        db = next(get_db())
        user = db.query(User).filter(User.id == self.user.id).first()
        assert not verify_password("Strongpassword1!", user.password_hash)
        assert verify_password("new-passwordA1!", user.password_hash)

    def test_wrong_old_password(self, client):
        response = client.post("/user/change-password", json={
            "old_password": "wrong-password",
            "new_password": "new-passwordA1!",
        }, cookies={"session-token": self.session.token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid old password"}

    def test_wrong_new_password(self, client):
        response = client.post("/user/change-password", json={
            "old_password": "Strongpassword1!",
            "new_password": "weak",
        }, cookies={"session-token": self.session.token})
        assert response.status_code == 400
        assert response.json() == {"detail": "New password is not strong enough"}
    
    def test_same_password(self, client):
        response = client.post("/user/change-password", json={
            "old_password": "Strongpassword1!",
            "new_password": "Strongpassword1!",
        }, cookies={"session-token": self.session.token})
        assert response.status_code == 400
        assert response.json() == {"detail": "New password cannot be the same as the old password"}

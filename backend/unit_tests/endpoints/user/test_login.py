import pytest
from fastapi.testclient import TestClient

from database import get_db, engine, DatabaseSession
from database.models import Base, User, Session
from main import app
from endpoints.user.hashing import hash_password

client = TestClient(app)

class TestLoginUser:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @staticmethod
    def setup_method():
        DatabaseSession.close_all()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User",
                    password_hash=hash_password("password"),
                    is_confirmed=True))
        db.commit()

    def test_login_user_success(self, client):

        response = client.post("/user/login", json={
            "email": "test@example.com",
            "password": "password",
        })

        assert response.status_code == 200
        assert response.json().get("access_token", None) is not None
        db = next(get_db())
        user = db.query(User).filter(User.email == "test@example.com").first()
        session = db.query(Session).filter(Session.user_id == user.id).first()
        assert session is not None
        assert session.is_active is True

    def test_login_wrong_email(self):
        response = client.post("/user/login", json={
            "email": "wrong@email.com",
            "password": "password",
        })
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid email or password"}
        db = next(get_db())
        user = db.query(User).filter(User.email == "test@example.com").first()
        session = db.query(Session).filter(Session.user_id == user.id).first()
        assert session is None

    def test_login_wrong_password(self):
        response = client.post("/user/login", json={
            "email": "test@example.com",
            "password": "wrong_password",
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid email or password"}

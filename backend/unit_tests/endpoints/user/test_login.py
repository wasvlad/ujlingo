import pytest
from fastapi.testclient import TestClient

from database import get_db, engine, DatabaseSession
from database.models import Base, User, Session
from main import app
from endpoints.user.hashing import hash_password
from unit_tests.tools import clear_database

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
        assert response.json().get("message", None) == "Login successful"
        assert "set-cookie" in response.headers
        assert "session-token=" in response.headers["set-cookie"]
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "Secure" in response.headers["set-cookie"]
        assert "SameSite=lax" in response.headers["set-cookie"]
        cookies = response.headers.get("set-cookie")
        assert cookies is not None
        token = None
        for cookie in cookies.split(';'):
            if cookie.strip().startswith("session-token="):
                token = cookie.split('=')[1]
                break
        assert token is not None
        db = next(get_db())
        user = db.query(User).filter(User.email == "test@example.com").first()
        session = db.query(Session).filter(Session.user_id == user.id).first()
        assert session is not None
        assert session.is_active is True
        assert session.token == token

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


class TestValidateSession:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def setup_class(self):
        clear_database()
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User",
                    password_hash=hash_password("password"),
                    is_confirmed=True))
        db.commit()
        response = client.post("/user/login", json={
            "email": "test@example.com",
            "password": "password",
        })
        cookies = response.headers.get("set-cookie")
        token = None
        for cookie in cookies.split(';'):
            if cookie.strip().startswith("session-token="):
                token = cookie.split('=')[1]
                break
        assert token is not None
        self.valid_token = token


    def test_validate_user_success(self):
        response = client.get("/user/validate-session", cookies={
            "session-token": self.valid_token
        })

        assert response.status_code == 200
        assert response.json().get("message", None) == "Hello Test!"

    def test_validate_user_fail(self):
        response = client.get("/user/validate-session", cookies={
            "session-token": "invalid token"
        })

        assert response.status_code == 401

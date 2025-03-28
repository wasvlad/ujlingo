import pytest
from fastapi.testclient import TestClient

from database import get_db
from database.models import User
from main import app
from endpoints.user.hashing import hash_password
from unit_tests.tools import clear_database


class TestValidateSession:

    @pytest.fixture
    def client(self):
        app.dependency_overrides.clear()
        return TestClient(app)

    def setup_class(self):
        client = TestClient(app)
        clear_database()
        db = next(get_db())
        db.add(User(email="admin@example.com", name="Test", surname="User",
                    password_hash=hash_password("password"),
                    is_confirmed=True, is_admin=True))
        db.commit()
        response = client.post("/user/login", json={
            "email": "admin@example.com",
            "password": "password",
        })
        cookies = response.headers.get("set-cookie")
        assert "session-token=" in cookies
        token = cookies.split("session-token=")[1].split(';')[0]
        self.valid_token = token


    def test_validate_admin_success(self, client):
        response = client.get("/admin/validate-session", cookies={
            "session-token": self.valid_token
        })

        assert response.status_code == 200
        assert response.json().get("message", None) == "Hello Test!"

    def test_validate_admin_fail(self, client):
        response = client.get("/admin/validate-session", cookies={
            "session-token": "invalid token"
        })

        assert response.status_code == 401

    def test_not_admin(self, client):
        db = next(get_db())
        user = db.query(User).filter(User.email == "admin@example.com").first()
        user.is_admin = False
        db.commit()
        response = client.get("/admin/validate-session", cookies={
            "session-token": self.valid_token
        })
        user.is_admin = True
        db.commit()

        assert response.status_code == 403
        assert response.json().get("detail", None) == "Access denied"


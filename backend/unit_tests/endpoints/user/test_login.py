from fastapi.testclient import TestClient

from main import app
from unit_tests.tools import clear_database
from .login_helpers import login_user
from .register_helpers import confirm_email
from unit_tests.test_data import TestData

client = TestClient(app)

class TestLoginUser:
    def test_login_user_success(self):
        clear_database()

        response = login_user(client)

        assert response.status_code == 200
        assert response.json().get("access_token", None) is not None

    def test_login_wrong_email(self):
        clear_database()

        confirm_email(client)
        response = client.post("/user/login", json={
            "email": "wrong@email.com",
            "password": TestData.User.password,
        })
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid email or password"}

    def test_login_wrong_password(self):
        clear_database()

        confirm_email(client)
        response = client.post("/user/login", json={
            "email": TestData.User.email,
            "password": "wrong_password",
        })

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid email or password"}

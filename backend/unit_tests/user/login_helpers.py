from fastapi.testclient import TestClient

from ..test_data import TestData
from .register_helpers import register_user

def login_user(client: TestClient, email: str=TestData.User.email, password: str=TestData.User.password):
    register_user(client, email, password)
    return client.post("/user/login", json={
        "email": email,
        "password": password
    })
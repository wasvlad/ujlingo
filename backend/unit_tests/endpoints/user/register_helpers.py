from fastapi.testclient import TestClient

from database.models import User
from unit_tests.test_data import TestData
from database import get_db

def register_user(client: TestClient, email: str=TestData.User.email,
                  password: str=TestData.User.password,
                  name: str=TestData.User.name,
                  surname: str=TestData.User.surname,):

    return client.post("/user/register", json={
        "email": email,
        "password": password,
        "name": name,
        "surname": surname
    })

def confirm_email(client: TestClient, email: str=TestData.User.email):
    register_user(client, email=email)
    gen = get_db()
    db = next(gen)
    existing_user: User | None = db.query(User).filter(User.email == email).first()
    existing_user.is_confirmed = True
    db.commit()
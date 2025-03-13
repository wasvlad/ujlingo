import os

from fastapi import FastAPI
import uvicorn
import httpx

import endpoints
from database import get_db
from database.models import User
from endpoints.user.hashing import hash_password

TRANSLATOR_URL = os.getenv("TRANSLATOR_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

db = next(get_db())
root_user = db.query(User).filter(User.email == "root@company.com").first()
if not root_user:
    db.add(User(email="root@company.com",
                name="root",
                surname="root",
                password_hash=hash_password("mustbechanged"),
                is_admin=True,
                is_confirmed=True))
    db.commit()

app = FastAPI(docs_url=None if ENVIRONMENT != "local" else "/docs",
              redoc_url=None if ENVIRONMENT != "local" else "/redoc")
app.include_router(endpoints.router)
@app.get("/")
async def read_root():
    with httpx.Client() as client:
        response = client.get(TRANSLATOR_URL)
        response.raise_for_status()
        data = response.json()
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
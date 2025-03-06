import os

from fastapi import FastAPI
import uvicorn
import httpx

import user

TRANSLATOR_URL = os.getenv("TRANSLATOR_URL")

app = FastAPI()
app.include_router(user.router, prefix="/user")
@app.get("/")
async def read_root():
    with httpx.Client() as client:
        response = client.get(TRANSLATOR_URL)
        response.raise_for_status()
        data = response.json()
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
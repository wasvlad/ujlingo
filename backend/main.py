import os

from fastapi import FastAPI
import uvicorn
import httpx

import endpoints

TRANSLATOR_URL = os.getenv("TRANSLATOR_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

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
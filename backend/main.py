import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

import endpoints

TRANSLATOR_URL = os.getenv("TRANSLATOR_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

app = FastAPI(docs_url=None if ENVIRONMENT != "local" else "/docs",
              redoc_url=None if ENVIRONMENT != "local" else "/redoc")
# Musialem to dodac, poniewaz backend odrzucal zapytania z frontendu przez CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
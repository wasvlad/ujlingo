import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import httpx

BACKEND_URL = os.getenv("BACKEND_URL")

app = FastAPI()
@app.get("/")
async def read_root():
    async with httpx.AsyncClient() as client:
        response = await client.get(BACKEND_URL)
        response.raise_for_status()
        data = response.json()
    return data

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
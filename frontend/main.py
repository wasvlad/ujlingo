import os

from fastapi import FastAPI
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
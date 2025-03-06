import json

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/en-to-ua-words")
async def to_ua_words():
    return json.loads(open("data/production/en_to_ua_words.json").read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3002)
import json
import csv

from fastapi import FastAPI
import uvicorn
import pandas as pd

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/sync-en-ua-words")
async def sync_en_ua_words():
    csv_file_path = "data/production/uatoeng.csv"
    res = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ua_word = row[0]
            en_words = row[1]
            for en_word in en_words.split(' / '):
                if res.get(en_word, None) is None:
                    res[en_word] = []
                res[en_word].append(ua_word)

    return res

@app.get("/sync-sentences")
async def sync_en_ua_words():
    csv_file_path = "data/production/ua_to_en_sentence.csv"
    df = pd.read_csv(csv_file_path, delimiter=',', quotechar='"')

    res = {}
    for index, row in df.iterrows():
        res[row[0]] = [row[1]]

    return res

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3002)
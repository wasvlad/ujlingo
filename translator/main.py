import os
import csv
import torch
import pandas as pd
from pathlib import Path
from functools import lru_cache
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI(title="UA→EN Translator API", version="1.0")

default_dir = Path(__file__).parent / "data" / "marian_finetuned_uk_en_v1"
MODEL_PATH = os.getenv("MODEL_PATH", str(default_dir))

if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(
        f"MODEL_PATH '{MODEL_PATH}' does not exist.\n"
        "• локально:   export MODEL_PATH=data/marian_finetuned_uk_en_v1\n"
        "• у Docker:   ENV MODEL_PATH=/app/data/marian_finetuned_uk_en_v1"
    )

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, local_files_only=True).to(device)

class TranslationRequest(BaseModel):
    text: str

@app.get("/translate", response_class=HTMLResponse)
async def get_translate():
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Ukrainian→English Translator</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            flex-direction: column;
            min-height: 100vh;
          }
          header {
            background-color: #3e4c59;
            width: 100%;
            padding: 20px 0;
            text-align: center;
            color: #ffffff;
          }
          .container {
            max-width: 700px;
            width: 100%;
            padding: 20px;
            margin-top: 40px;
            background-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
          }
          h1 {
            margin-bottom: 20px;
            font-size: 24px;
            color: #333333;
          }
          textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ccd0d5;
            border-radius: 4px;
            resize: vertical;
          }
          button {
            margin-top: 15px;
            padding: 10px 20px;
            font-size: 16px;
            background-color: #3e4c59;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
          }
          button:hover {
            background-color: #2c3742;
          }
          .message {
            margin-top: 20px;
            font-size: 16px;
            color: #d9534f;
          }
          .result {
            margin-top: 20px;
          }
          .result p {
            font-size: 16px;
            color: #222222;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
          }
        </style>
      </head>
      <body>
        <header>
          <h1>Ukrainian→English Translator</h1>
        </header>
        <div class="container">
          <h1>Enter your Ukrainian sentence below</h1>
          <form action="/translate" method="post">
            <textarea name="text" placeholder="Enter a Ukrainian sentence…"></textarea><br>
            <button type="submit">Translate</button>
          </form>
        </div>
      </body>
    </html>
    """

@app.post("/translate", response_class=HTMLResponse)
async def post_translate(text: str = Form(...)):
    if not text.strip():
        return """
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>Ukrainian→English Translator</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 0;
                display: flex;
                align-items: center;
                flex-direction: column;
                min-height: 100vh;
              }
              header {
                background-color: #3e4c59;
                width: 100%;
                padding: 20px 0;
                text-align: center;
                color: #ffffff;
              }
              .container {
                max-width: 700px;
                width: 100%;
                padding: 20px;
                margin-top: 40px;
                background-color: #ffffff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-radius: 8px;
              }
              h1 {
                margin-bottom: 20px;
                font-size: 24px;
                color: #333333;
              }
              textarea {
                width: 100%;
                height: 120px;
                padding: 10px;
                font-size: 16px;
                border: 1px solid #ccd0d5;
                border-radius: 4px;
                resize: vertical;
              }
              button {
                margin-top: 15px;
                padding: 10px 20px;
                font-size: 16px;
                background-color: #3e4c59;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                cursor: pointer;
              }
              button:hover {
                background-color: #2c3742;
              }
              .message {
                margin-top: 20px;
                font-size: 16px;
                color: #d9534f;
              }
            </style>
          </head>
          <body>
            <header>
              <h1>Ukrainian→English Translator</h1>
            </header>
            <div class="container">
              <h1>Enter your Ukrainian sentence below</h1>
              <form action="/translate" method="post">
                <textarea name="text" placeholder="Enter a Ukrainian sentence…"></textarea><br>
                <button type="submit">Translate</button>
              </form>
              <div class="message">Error: Empty input. Please enter a sentence.</div>
            </div>
          </body>
        </html>
        """
    inputs = tokenizer(text, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_length=128)
    translation = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Ukrainian→English Translator</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            flex-direction: column;
            min-height: 100vh;
          }}
          header {{
            background-color: #3e4c59;
            width: 100%;
            padding: 20px 0;
            text-align: center;
            color: #ffffff;
          }}
          .container {{
            max-width: 700px;
            width: 100%;
            padding: 20px;
            margin-top: 40px;
            background-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
          }}
          h1 {{
            margin-bottom: 20px;
            font-size: 24px;
            color: #333333;
          }}
          textarea {{
            width: 100%;
            height: 120px;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ccd0d5;
            border-radius: 4px;
            resize: vertical;
          }}
          button {{
            margin-top: 15px;
            padding: 10px 20px;
            font-size: 16px;
            background-color: #3e4c59;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
          }}
          button:hover {{
            background-color: #2c3742;
          }}
          .result {{
            margin-top: 20px;
          }}
          .result p {{
            font-size: 16px;
            color: #222222;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
          }}
        </style>
      </head>
      <body>
        <header>
          <h1>Ukrainian→English Translator</h1>
        </header>
        <div class="container">
          <h1>Enter your Ukrainian sentence below</h1>
          <form action="/translate" method="post">
            <textarea name="text" placeholder="Enter a Ukrainian sentence…">{text}</textarea><br>
            <button type="submit">Translate</button>
          </form>
          <div class="result">
            <h2>Translation:</h2>
            <p>{translation}</p>
          </div>
        </div>
      </body>
    </html>
    """

@lru_cache(maxsize=1)
def load_word_dict() -> dict[str, list[str]]:
    csv_file = Path("data/production/uatoeng.csv")
    if not csv_file.is_file():
        raise FileNotFoundError(csv_file)
    res: dict[str, list[str]] = {}
    with csv_file.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            ua_word, en_words = row[0].strip(), row[1].strip()
            for en in en_words.split(" / "):
                res.setdefault(en, []).append(ua_word)
    return res

@app.get("/sync-en-ua-words")
async def sync_en_ua_words():
    return load_word_dict()

@lru_cache(maxsize=1)
def load_sentence_dict() -> dict[str, list[str]]:
    csv_file = Path("data/production/ua_to_en_sentence.csv")
    if not csv_file.is_file():
        raise FileNotFoundError(csv_file)
    df = pd.read_csv(csv_file)
    return {row[0]: [row[1]] for _, row in df.iterrows()}

@app.get("/sync-sentences")
async def sync_sentences():
    return load_sentence_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)

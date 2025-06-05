#!/usr/bin/env python3
import os
import csv
import torch
import pandas as pd

from pathlib import Path
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI(title="Translator + Sync API", version="1.0")

# ─── 1. Шлях до моделі ──────────────────────────────────────────────────────────
default_dir = Path(__file__).parent / "data" / "uk_en_translation_model"
MODEL_PATH = os.getenv("MODEL_PATH", str(default_dir))

if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(
        f"MODEL_PATH '{MODEL_PATH}' does not exist.\n"
        "• локально:   export MODEL_PATH=data/uk_en_translation_model\n"
        "• у Docker:   ENV MODEL_PATH=/app/data/uk_en_translation_model"
    )

# ─── 2. Завантаження моделі (тільки локально, без звернень до HuggingFace Hub) ────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, local_files_only=True).to(device)


# ─── 3. Pydantic-схема для JSON-запиту /translate ───────────────────────────────
class TranslationRequest(BaseModel):
    text: str


# ─── 4. GET / → редірект на /translate ────────────────────────────────────────
@app.get("/", response_class=RedirectResponse)
async def read_root():
    return RedirectResponse(url="/translate")


# ─── 5. GET /translate: повертає HTML-форму для введення речення ───────────────
@app.get("/translate", response_class=HTMLResponse)
async def translate_form_page():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>UA→EN Translator</title>
      </head>
      <body>
        <h1>Українсько-Англійський Переклад</h1>
        <form action="/translate-form" method="post">
          <textarea 
            name="text"
            rows="4" 
            cols="60" 
            placeholder="Введіть українське речення…"
          ></textarea><br><br>
          <button type="submit">Перекласти</button>
        </form>
      </body>
    </html>
    """


# ─── 6. POST /translate-form: обробка форми та повернення HTML ────────────────
@app.post("/translate-form", response_class=HTMLResponse)
async def translate_form(text: str = Form(...)):
    if not text.strip():
        return HTMLResponse(
            content="<h3 style='color:red;'>Помилка: порожній рядок.</h3>"
                    "<a href='/translate'>← Назад</a>",
            status_code=400
        )
    inputs = tokenizer(text, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_length=128)
    translation = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Переклад готовий</title>
      </head>
      <body>
        <h1>Оригінал:</h1>
        <p>{text}</p>
        <h1>Переклад:</h1>
        <p><strong>{translation}</strong></p>
        <a href="/translate">← Назад</a>
      </body>
    </html>
    """


# ─── 7. POST /translate: JSON-ендпоінт для клієнтів ────────────────────────────
@app.post("/translate")
async def translate_json(req: TranslationRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    inputs = tokenizer(req.text, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_length=128)
    translation = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return {"translation": translation}


# ─── 8. Синхронізація: EN⇆UA слова ─────────────────────────────────────────────
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


# ─── 9. Синхронізація речень ─────────────────────────────────────────────────
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


# ─── 10. Локальний запуск через Uvicorn ───────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)

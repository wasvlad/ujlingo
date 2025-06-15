# -*- coding: utf-8 -*-
"""
translate_ukr_to_eng_resumeable.py

→ Резюмуємий переклад: ukr_sentences_reformed.tsv  (дві колонки: ukr | eng)
→ Переклад через googletrans (безкоштовно)
→ Після кожного рядка оновлює ukr_sentences_translated.tsv
→ При перезапуску продовжує з першого незаповненого рядка
"""

import time
import pandas as pd
from pathlib import Path
from googletrans import Translator
from tqdm import tqdm

BASE  = Path(__file__).resolve().parents[2] / "data" / "production"
IN_F  = BASE / "ukr_sentences_reformed.tsv"
OUT_F = BASE / "ukr_sentences_translated.tsv"

df_src = pd.read_csv(IN_F, sep="\t", dtype=str)

if OUT_F.exists():
    df_out = pd.read_csv(
        OUT_F,
        sep="\t",
        dtype=str,
        keep_default_na=False,
    )
    if len(df_out) != len(df_src):
        raise ValueError(
            f"Розмір existing {OUT_F} ({len(df_out)}) "
            f"не співпадає з оригіналом ({len(df_src)})"
        )
else:
    df_out = df_src.copy()
    df_out["eng"] = ""

translator = Translator()

def translate_with_retry(text, retries=3, delay=1.0):
    for i in range(1, retries+1):
        try:
            return translator.translate(text, src="uk", dest="en").text
        except Exception as e:
            print(f"   ⚠️  Помилка (спроба {i}/{retries}): {e}")
            time.sleep(delay * i)
    return ""

mask = df_out["eng"].isna() | (df_out["eng"].str.strip() == "")
if not mask.any():
    print("🎉 Всі рядки вже перекладено.")
    exit()

start_idx = mask.idxmax()
n = len(df_out)
print(f"🔄 Починаємо з рядка #{start_idx} із {n}")

try:
    for idx in tqdm(range(start_idx, n), desc="Translating"):
        ukr_text = df_out.at[idx, "ukr"] or ""
        if not ukr_text:
            df_out.at[idx, "eng"] = ""
        else:
            if len(ukr_text) > 5000:
                parts = [ukr_text[i:i+5000] for i in range(0, len(ukr_text), 5000)]
                tr = "".join(translate_with_retry(p) for p in parts)
            else:
                tr = translate_with_retry(ukr_text)
            df_out.at[idx, "eng"] = tr

        df_out.to_csv(
            OUT_F,
            sep="\t",
            index=False,
            encoding="utf-8",
            na_rep="",
        )
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n⏸️  Перервано користувачем — прогрес збережено.")

print(f"✅ Завершено до рядка #{idx}. Файл: {OUT_F}")

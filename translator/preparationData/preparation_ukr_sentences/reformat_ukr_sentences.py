# -*- coding: utf-8 -*-
"""
reformat_ukr_sentences.py

Читає TSV з:
  …/translator/data/production/ukr_sentences.tsv
та виводить:
  …/translator/data/production/ukr_sentences_reformed.tsv

Вихідний файл містить дві колонки:
  ukr – оригінал
  eng – порожня (для майбутнього перекладу)
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "production"
IN_PATH  = BASE_DIR / "ukr_sentences.tsv"
OUT_PATH = BASE_DIR / "ukr_sentences_reformed.tsv"

if not IN_PATH.exists():
    raise FileNotFoundError(f"Не знайдено файл: {IN_PATH}")

df = pd.read_csv(
    IN_PATH,
    sep="\t",
    header=None,
    names=["id", "lang", "ukr"],
    quoting=3,
    engine="python",
)

if not (df["lang"] == "ukr").all():
    bad = df[df["lang"] != "ukr"].head()
    raise ValueError(f"Знайдено рядки з unexpected lang-маркерами:\n{bad}")

out = pd.DataFrame({
    "ukr": df["ukr"],
    "eng": "",
})

out.to_csv(OUT_PATH, sep="\t", index=False, encoding="utf-8")

print(f"✓ Готово! Новий файл: {OUT_PATH}")

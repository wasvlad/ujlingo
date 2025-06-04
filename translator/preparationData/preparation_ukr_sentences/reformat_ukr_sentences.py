#!/usr/bin/env python3
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

# 1) Знаходимо директорію "translator/data/production" відносно цього скрипта
BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "production"
IN_PATH  = BASE_DIR / "ukr_sentences.tsv"
OUT_PATH = BASE_DIR / "ukr_sentences_reformed.tsv"

# 2) Перевіряємо, що вхідний файл існує
if not IN_PATH.exists():
    raise FileNotFoundError(f"Не знайдено файл: {IN_PATH}")

# 3) Читаємо TSV без заголовків, розділювач — табуляція
df = pd.read_csv(
    IN_PATH,
    sep="\t",
    header=None,               # у файлі нема row із заголовками
    names=["id", "lang", "ukr"],
    quoting=3,                 # QUOTE_NONE, щоб не ламало лапки всередині тексту
    engine="python",
)

# 4) Перевірка: у другому стовпці мають бути тільки 'ukr'
if not (df["lang"] == "ukr").all():
    bad = df[df["lang"] != "ukr"].head()
    raise ValueError(f"Знайдено рядки з unexpected lang-маркерами:\n{bad}")

# 5) Формуємо новий DataFrame з двома колонками
out = pd.DataFrame({
    "ukr": df["ukr"],
    "eng": "",    # заповнюємо порожніми рядками
})

# 6) Пишемо назад у TSV (tab-separated), без індексу
out.to_csv(OUT_PATH, sep="\t", index=False, encoding="utf-8")

print(f"✓ Готово! Новий файл: {OUT_PATH}")

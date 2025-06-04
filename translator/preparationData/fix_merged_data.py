#!/usr/bin/env python3
import csv, re
from pathlib import Path
import pandas as pd

root     = Path.cwd()
src_tsv  = root / "data" / "production" / "merged_ukr_dataset_old.tsv"
fixed_tsv = root / "data" / "production" / "merged_ukr_dataset.tsv"

def lang(text: str) -> str:
    cyr = len(re.findall(r'[\u0400-\u04FF]', text))
    lat = len(re.findall(r'[A-Za-z]', text))
    return "uk" if cyr > lat else "en" if lat > cyr else "und"

df = (
    pd.read_csv(
        src_tsv,
        sep="\t",
        header=0,                # зніміть, якщо немає заголовка
        quoting=csv.QUOTE_NONE,
        on_bad_lines="skip",
        engine="python",
    )[["English", "Ukrainian"]]
    .fillna("")
)

mask = (df["English"].map(lang) == "uk") & (df["Ukrainian"].map(lang) == "en")
swapped = mask.sum()
df.loc[mask, ["English", "Ukrainian"]] = df.loc[mask, ["Ukrainian", "English"]].values

df.to_csv(fixed_tsv, sep="\t", index=False)
print(f"✅ saved → {fixed_tsv.relative_to(root)} | rows swapped: {swapped}")

import csv
import os
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path.cwd()
INPUT_FILE   = PROJECT_ROOT / "data" / "production" / "merged_ukr_dataset.tsv"

OUTPUT_DIR   = PROJECT_ROOT / "data" / "splits_merged_ukr_dataset"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_RATIO = 0.10          # 10 % test
VAL_RATIO  = 0.10          # 10 % validation


def load_parallel_tsv(tsv_path: Path) -> pd.DataFrame:

    if not tsv_path.is_file():
        sys.exit(f"Input file not found: {tsv_path}")

    print(f"📥 Reading {tsv_path.relative_to(PROJECT_ROOT)} …")
    raw_df = pd.read_csv(
        tsv_path,
        sep="\t",
        header=None,
        dtype=str,
        quoting=csv.QUOTE_NONE,
        on_bad_lines="skip",
        engine="python"
    )

    if raw_df.shape[1] < 2:
        sys.exit("Помилка: у файлі менше двох колонок, які можна було б обробити.")

    df = raw_df.iloc[:, :2].copy()
    df.columns = ["en", "uk"]

    df = df.dropna(subset=["en", "uk"])
    print(f"🔎 Loaded {len(df):,} sentence pairs.")
    return df


def split_dataset(df: pd.DataFrame):
    """Повертає три датафрейми: train, validation, test."""
    df_rest, df_test = train_test_split(
        df,
        test_size=TEST_RATIO,
        random_state=42,
        shuffle=True,
    )
    rel_val_ratio = VAL_RATIO / (1 - TEST_RATIO)
    df_train, df_val = train_test_split(
        df_rest,
        test_size=rel_val_ratio,
        random_state=42,
        shuffle=True,
    )
    return df_train, df_val, df_test


def save_split(df: pd.DataFrame, path: Path):
    """Записує датафрейм у TSV з UTF-8 та правильним розділювачем."""
    df.to_csv(path, sep="\t", index=False)
    print(f"💾 Saved {len(df):,} lines → {path.relative_to(PROJECT_ROOT)}")


def main():
    df = load_parallel_tsv(INPUT_FILE)

    print("✂️  Splitting into train / validation / test …")
    df_train, df_val, df_test = split_dataset(df)

    save_split(df_train, OUTPUT_DIR / "train.tsv")
    save_split(df_val,   OUTPUT_DIR / "validation.tsv")
    save_split(df_test,  OUTPUT_DIR / "test.tsv")

    print("\n✅ Data split completed successfully!")


if __name__ == "__main__":
    main()

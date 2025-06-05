import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.normpath(os.path.join(script_dir, "..", "data", "production"))

file1 = os.path.join(data_folder, "ukr-2.tsh")
file2 = os.path.join(data_folder, "ukr_sentences_translated.tsv")
file3 = os.path.join(data_folder, "ua_to_en_sentence.csv")

def load_and_normalize(path):
    """
    Завантажує TSV/TSH/CSV, бере перші дві колонки (англійська та українська),
    перейменовує їх у "English" та "Ukrainian".
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".tsv", ".tsh"):
        df = pd.read_csv(path, sep="\t", header=0, dtype=str)
    elif ext == ".csv":
        df = pd.read_csv(path, sep=",", header=0, dtype=str)
    else:
        raise ValueError(f"Невідомий формат файлу: {path}")

    if df.shape[1] < 2:
        raise RuntimeError(f"Файл {os.path.basename(path)} містить менше ніж 2 колонки.")

    col0, col1 = df.columns[0], df.columns[1]
    df = df.rename(columns={col0: "English", col1: "Ukrainian"})
    return df[["English", "Ukrainian"]].copy()

df1 = load_and_normalize(file1)
df2 = load_and_normalize(file2)
df3 = load_and_normalize(file3)

merged = pd.concat([df1, df2, df3], ignore_index=True)

before = len(merged)
merged = merged.drop_duplicates(subset=["English", "Ukrainian"])
after = len(merged)

print(f"Загалом рядків до drop_duplicates(): {before}")
print(f"Після видалення дублікатів:             {after}")
print()

pd.set_option("display.max_rows", 20)
pd.set_option("display.max_columns", 2)
print(merged.head(20))

output_path = os.path.join(data_folder, "merged_ukr_dataset_no_duplicates.tsv")
merged.to_csv(output_path, sep="\t", index=False, encoding="utf-8")
print()
print(f"Файл без дублікатів збережено за адресою:\n{output_path}")

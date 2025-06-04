import pandas as pd
import os
import sys

def check_duplicates(file_path):
    """
    Читає TSV/TSH/CSV, бере перші дві колонки як "English" та "Ukrainian",
    рахує загальну кількість рядків, унікальних пар та дублікатів,
    і виводить інформацію та самі дублікати.
    """
    if not os.path.isfile(file_path):
        print(f"Файл не знайдено: {file_path}")
        return

    # Визначаємо розширення, щоб обрати роздільник
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".tsv", ".tsh"):
        df = pd.read_csv(file_path, sep="\t", header=0, dtype=str)
    elif ext == ".csv":
        df = pd.read_csv(file_path, sep=",", header=0, dtype=str)
    else:
        print(f"Невідомий формат файлу: {ext}. Підтримуються .tsv, .tsh, .csv")
        return

    # Переконаємося, що є принаймні дві колонки
    if df.shape[1] < 2:
        print(f"У файлі {os.path.basename(file_path)} менше ніж 2 колонки.")
        return

    # Беремо перші дві колонки та перейменовуємо
    col0, col1 = df.columns[0], df.columns[1]
    df = df.rename(columns={col0: "English", col1: "Ukrainian"})
    df = df[["English", "Ukrainian"]].copy()

    total_rows = len(df)
    unique_pairs = df.drop_duplicates(subset=["English", "Ukrainian"])
    num_unique = len(unique_pairs)
    num_duplicates = total_rows - num_unique

    print(f"Файл: {file_path}")
    print(f"Загальна кількість рядків:                   {total_rows}")
    print(f"Кількість унікальних пар (English+Ukrainian): {num_unique}")
    print(f"Кількість рядків, що є дублікатами:           {num_duplicates}")
    print()

    if num_duplicates == 0:
        print("Дублікатів не знайдено.")
        return

    # Знаходимо всі рядки, що мають хоча б одну копію:
    dup_mask = df.duplicated(subset=["English", "Ukrainian"], keep=False)
    duplicates_df = df[dup_mask].copy()

    # Для зручності групуємо дублікати
    grouped = duplicates_df.groupby(["English", "Ukrainian"])
    print("Список дублікатів (пара → кількість):")
    for (eng, ukr), group in grouped:
        count = len(group)
        print(f'"{eng}" ↔ "{ukr}" — {count} раз(и)')
    print()

    # Додатково: можна зберегти всі дублікати у окремий файл
    duplicates_output = os.path.splitext(file_path)[0] + "_duplicates.tsv"
    duplicates_df.to_csv(duplicates_output, sep="\t", index=False, encoding="utf-8")
    print(f"Усі рядки-дублікти збережено у файлі:\n{duplicates_output}")

if __name__ == "__main__":
    # Якщо шлях до файлу передається як аргумент командного рядка, використовуємо його.
    # Інакше – вкажіть шлях нижче у змінній `file_to_check`.
    if len(sys.argv) > 1:
        file_to_check = sys.argv[1]
    else:
        # Приклад: відносний шлях від місця запуску. Замініть на свій файл.
        file_to_check = os.path.join("/translator/data/production/merged_ukr_dataset_old.tsv")

    check_duplicates(file_to_check)

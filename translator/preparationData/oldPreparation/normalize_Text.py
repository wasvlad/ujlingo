# не використовується в теперішній моделі
import unicodedata
import re
import pandas as pd
import spacy

#  Завантажуємо spaCy-моделі, лишаємо тільки токенізатор
nlp_uk = spacy.load("uk_core_news_sm", disable=["parser","tagger","attribute_ruler","lemmatizer","ner"])
nlp_en = spacy.load("en_core_web_sm",   disable=["parser","tagger","attribute_ruler","lemmatizer","ner"])


def clean_text(text: str) -> str:
    # Unicode NFC
    text = unicodedata.normalize("NFC", text)
    # ASCII-аналоги для лапок і тире
    text = text.replace("«", '"').replace("»", '"').replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    # Видалення HTML-тегів
    text = re.sub(r"<[^>]+>", " ", text)
    # Видалення URL
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    # Колапс пробілів
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_and_lower(text: str, nlp) -> str:
    doc = nlp(text)
    tokens = [tok.text.lower() for tok in doc if not tok.is_space]
    return " ".join(tokens)


if __name__ == "__main__":

    df = pd.read_csv("/ujlingo/translator/data/production/ua_to_en_sentence.csv")
    # Перейменовуємо колонки, якщо потрібно
    df = df.rename(columns={"Ukrainian": "uk", "English": "en"})
    #  Нормалізуємо
    df["uk_norm"] = df["uk"].apply(lambda s: tokenize_and_lower(clean_text(s), nlp_uk))
    df["en_norm"] = df["en"].apply(lambda s: tokenize_and_lower(clean_text(s), nlp_en))
    #  Зберігаємо тільки нові, відформатовані колонки
    df[["uk_norm", "en_norm"]].to_csv("ua_to_en_sentence_normalized.csv", index=False)

print("Done: ua_to_en_sentence_normalized.csv created.")

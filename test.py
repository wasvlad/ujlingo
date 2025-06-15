import spacy

# Загружаем предобученную модель для английского языка
nlp = spacy.load("en_core_web_sm")

# Текст для анализа
text = "Apple is looking at buying U.K. startup for $1 billion."

# Обработка текста
doc = nlp(text)

# Вывод информации по каждому токену
print("Токены:")
for token in doc:
    # token.text - оригинальный текст токена
    # token.lemma_ - лемма токена
    # token.pos_ - часть речи
    # token.dep_ - зависимость от других слов в предложении
    print(f"{token.text:<12} {token.lemma_:<12} {token.pos_:<8} {token.dep_}")

print("\nИменованные сущности:")
for ent in doc.ents:
    # ent.text - текст сущности
    # ent.label_ - категория сущности (например, PERSON, ORG, GPE, MONEY)
    print(f"{ent.text:<12} {ent.label_}")

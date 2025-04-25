from random import randint
from typing import List, Type

from sqlalchemy import func

from database import get_db
from database.models import (WordTranslation, WordTranslationKnowledge, Word, Sentence, SentenceTranslation,
                             SentenceTranslationKnowledge)
from ..words import MSQQuestion


def build_msq_question(translation: WordTranslation) -> MSQQuestion:
    db = next(get_db())
    wrong_word: Word = db.query(Word).filter((Word.language == translation.word_translated.language) &
                                             (Word.word != translation.word_translated.word)) \
        .order_by(func.random()).first()
    options = []

    def change_word(word: str) -> str:
        word_new = list(word)
        if len(word) <= 1:
            return word
        while ''.join(word_new) == word:
            i = randint(0, len(word) - 1)
            j = randint(0, len(word) - 2)
            if i == j:
                j += 1
            word_new[i], word_new[j] = word_new[j], word_new[i]
        return ''.join(word_new)

    if wrong_word:
        options.append(wrong_word.word)
        word = str(wrong_word.word)
        word = change_word(word)
        if word != wrong_word.word:
            options.append(word)

    right_word: str = translation.word_translated.word
    options.append(right_word)
    word = str(right_word)
    word = change_word(word)
    if word != right_word:
        options.append(right_word)

    question = MSQQuestion(translation, options)
    return question

def get_new_word_translations(number: int = 10, max_knowledge: int = 10) -> List[WordTranslation]:
    db = next(get_db())
    translations = []

    translations_db = db.query(WordTranslation, WordTranslationKnowledge) \
        .join(WordTranslationKnowledge, WordTranslationKnowledge.word_translation_id == WordTranslation.id, isouter=True) \
        .filter((WordTranslationKnowledge.knowledge <= max_knowledge) | (WordTranslationKnowledge.id == None)) \
        .order_by(func.random()) \
        .limit(number).all()

    for translation, knowledge in translations_db:
        db.refresh(translation)
        db.refresh(translation.word_original)
        db.refresh(translation.word_translated)
        db.expunge(translation)
        translations.append(translation)

    return translations

def get_word_translations_weak_knowledge(number: int = 10, min_knowledge: int = 10, max_knowledge: int = 70) -> List[WordTranslation]:
    db = next(get_db())
    translations = []

    translations_db = db.query(WordTranslation, WordTranslationKnowledge) \
        .join(WordTranslationKnowledge, WordTranslationKnowledge.word_translation_id == WordTranslation.id, isouter=True) \
        .filter((WordTranslationKnowledge.knowledge <= max_knowledge) & (WordTranslationKnowledge.knowledge >= min_knowledge)) \
        .order_by(func.random()) \
        .limit(number).all()

    for translation, knowledge in translations_db:
        db.refresh(translation)
        db.refresh(translation.word_original)
        db.refresh(translation.word_translated)
        db.expunge(translation)
        translations.append(translation)

    return translations


def get_word_translations_strong_knowledge(number: int = 10, min_knowledge: int = 70) -> List[WordTranslation]:
    db = next(get_db())
    translations = []

    translations_db = db.query(WordTranslation, WordTranslationKnowledge) \
        .join(WordTranslationKnowledge, WordTranslationKnowledge.word_translation_id == WordTranslation.id, isouter=True) \
        .filter(WordTranslationKnowledge.knowledge >= min_knowledge) \
        .order_by(func.random()) \
        .limit(number).all()

    for translation, knowledge in translations_db:
        db.refresh(translation)
        db.refresh(translation.word_original)
        db.refresh(translation.word_translated)
        db.expunge(translation)
        translations.append(translation)

    return translations

def get_new_sentence_translations(number: int = 10, max_knowledge: int = 10) -> List[SentenceTranslation]:
    db = next(get_db())
    translations = []

    translations_db = db.query(SentenceTranslation, SentenceTranslationKnowledge) \
        .join(SentenceTranslationKnowledge, SentenceTranslationKnowledge.sentence_translation_id == SentenceTranslation.id, isouter=True) \
        .filter((SentenceTranslationKnowledge.knowledge <= max_knowledge) | (SentenceTranslationKnowledge.id == None)) \
        .order_by(func.random()) \
        .limit(number).all()

    for translation, knowledge in translations_db:
        db.refresh(translation)
        db.refresh(translation.sentence_original)
        db.refresh(translation.sentence_translated)
        db.expunge(translation)
        translations.append(translation)

    return translations
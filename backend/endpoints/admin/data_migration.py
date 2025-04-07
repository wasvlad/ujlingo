import os

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from database import get_db
from .tools import validate_admin_session
from database.models import User, Word, WordTranslation, Sentence, SentenceTranslation

router = APIRouter()

class MessageResponse(BaseModel):
    message: str


def words_translations_to_pairs(data: dict) -> list:
    data_converted = []
    for orig, translations in data.items():
        for translated in translations:
            data_converted.append((orig, translated))
    return data_converted

@router.post("/sync-words", response_model=MessageResponse)
async def migrate_words(user: User = Depends(validate_admin_session),
                              db: Session = Depends(get_db)):
    url = os.getenv("TRANSLATOR_URL") + "/sync-en-ua-words"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    data_converted = words_translations_to_pairs(data)
    en_words = set(data.keys())
    en_words_db = db.query(Word).filter(Word.language == "en").all()
    for en_word_db in en_words_db:
        if en_word_db.word not in en_words:
            db.delete(en_word_db)
        else:
            en_words.remove(en_word_db.word)
    for en_word in en_words:
        word = Word(word=en_word, language="en")
        db.add(word)

    ua_words_db = db.query(Word).filter(Word.language == "ua").all()
    ua_words = set()
    for en_word, ua_word in data_converted:
        ua_words.add(ua_word)
    for ua_word in ua_words_db:
        if ua_word.word not in ua_words:
            db.delete(ua_word)
        else:
            ua_words.remove(ua_word.word)
    for ua_word in ua_words:
        word = Word(word=ua_word, language="ua")
        db.add(word)

    db.commit()

    word_translations = db.query(WordTranslation).options(
        joinedload(WordTranslation.word_original),
        joinedload(WordTranslation.word_translated)
    ).all()
    for word_translation in word_translations:
        word_original = word_translation.word_original
        word_translated = word_translation.word_translated

        if word_original.language == "en" and word_translated.language == "ua":
            db.delete(word_translation)
        elif word_original.language == "ua" and word_translated.language == "en":
            db.delete(word_translation)
        else:
            continue

    for word_en, word_ua in data_converted:
        word_en_db = db.query(Word).filter(Word.word == word_en, Word.language == "en").first()
        word_ua_db = db.query(Word).filter(Word.word == word_ua, Word.language == "ua").first()
        word_translation = WordTranslation()
        word_translation.word_original_id = word_en_db.id
        word_translation.word_translated_id = word_ua_db.id
        db.add(word_translation)
        word_translation = WordTranslation()
        word_translation.word_original_id = word_ua_db.id
        word_translation.word_translated_id = word_en_db.id
        db.add(word_translation)
    db.commit()

    return {"message": "Words migrated successfully"}


@router.post("/sync-sentences", response_model=MessageResponse)
async def migrate_words(user: User = Depends(validate_admin_session),
                              db: Session = Depends(get_db)):
    url = os.getenv("TRANSLATOR_URL") + "/sync-sentences"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    data_converted = words_translations_to_pairs(data)
    ua_sentences = set(data.keys())
    ua_sentences_db = db.query(Sentence).filter(Sentence.language == "ua").all()
    for ua_sentence_db in ua_sentences_db:
        if ua_sentence_db.sentence not in ua_sentences:
            db.delete(ua_sentence_db)
        else:
            ua_sentences.remove(ua_sentence_db.sentence)
    for ua_sentence in ua_sentences:
        sentence = Sentence(sentence=ua_sentence, language="ua")
        db.add(sentence)

    en_sentences_db = db.query(Sentence).filter(Sentence.language == "en").all()
    en_sentences = set()
    for ua_sentence, en_sentence in data_converted:
        en_sentences.add(en_sentence)
    for en_sentence_db in en_sentences_db:
        if en_sentence_db.sentence not in en_sentences:
            db.delete(en_sentence_db)
        else:
            en_sentences.remove(en_sentence_db.sentence)
    for en_sentence in en_sentences:
        sentence = Sentence(sentence=en_sentence, language="en")
        db.add(sentence)

    db.commit()

    sentence_translations = db.query(SentenceTranslation).options(
        joinedload(SentenceTranslation.sentence_original),
        joinedload(SentenceTranslation.sentence_translated)
    ).all()
    for sentence_translation in sentence_translations:
        original = sentence_translation.sentence_original
        translated = sentence_translation.sentence_translated

        if original.language == "en" and translated.language == "ua":
            db.delete(sentence_translation)
        elif original.language == "ua" and translated.language == "en":
            db.delete(sentence_translation)
        else:
            continue

    for sentence_ua, sentence_en in data_converted:
        sentence_en_db = db.query(Sentence).filter(Sentence.sentence == sentence_en, Sentence.language == "en").first()
        sentence_ua_db = db.query(Sentence).filter(Sentence.sentence == sentence_ua, Sentence.language == "ua").first()
        sentence_translation = SentenceTranslation()
        sentence_translation.sentence_original_id = sentence_en_db.id
        sentence_translation.sentence_translated_id = sentence_ua_db.id
        db.add(sentence_translation)
        sentence_translation = SentenceTranslation()
        sentence_translation.sentence_original_id = sentence_ua_db.id
        sentence_translation.sentence_translated_id = sentence_en_db.id
        db.add(sentence_translation)
    db.commit()

    return {"message": "Sentences migrated successfully"}

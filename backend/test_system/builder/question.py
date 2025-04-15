from random import randint

from sqlalchemy import func

from database import get_db
from database.models import User, WordTranslation, WordTranslationKnowledge, Word
from ..words import TranslationQuestion, MSQQuestion

def build_msq_question(translation: WordTranslation) -> MSQQuestion:
    db = next(get_db())
    wrong_word: Word = db.query(Word).filter((Word.language == translation.word_translated.language) &
                                    (Word.word != translation.word_translated.word))\
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


# def get_new_words_questions(user: User, number: int = 10, max_knowledge: int = 10) -> list:
#     db = next(get_db())
#     questions = []
#
#     translations = db.query(WordTranslation) \
#         .join(WordTranslationKnowledge, WordTranslationKnowledge.word_translation_id == WordTranslation.id) \
#         .filter(WordTranslationKnowledge.knowledge <= max_knowledge or WordTranslationKnowledge.knowledge is None) \
#         .order_by(func.random()) \
#         .limit(number).all()
#
#     for translation in translations:
#
#
#     return questions

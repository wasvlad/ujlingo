from test_system.builder.question import *
from database import get_db
from database.models import Word
from test_system.main import QuestionTypeEnum
from unit_tests.tools import clear_database

class TestBuildMsqQuestionTest:
    def setup_class(self):
        clear_database()

    def test_ok(self):
        clear_database()
        db = next(get_db())
        word_en = "hello"
        word_ua = "привіт"
        word_en2 = "world"
        word_en = Word(word=word_en, language="en")
        word_ua = Word(word=word_ua, language="ua")
        word_en2 = Word(word=word_en2, language="en")
        db.add_all([word_en, word_ua, word_en2])
        db.commit()
        word_translation = WordTranslation(word_translated_id=word_en.id, word_original_id=word_ua.id)
        word_translation.word_translated = word_en
        word_translation.word_original = word_ua
        translation = word_translation
        question = build_msq_question(translation)
        question_json = question.get()
        assert question_json.question == f"Translate the word: {translation.word_original.word}"
        assert word_en.word in question_json.options
        assert word_en2.word in question_json.options

    def test_one_letter_word(self):
        clear_database()
        db = next(get_db())
        word_en = "hello"
        word_ua = "привіт"
        word_en2 = "i"
        word_en = Word(word=word_en, language="en")
        word_ua = Word(word=word_ua, language="ua")
        word_en2 = Word(word=word_en2, language="en")
        db.add_all([word_en, word_ua, word_en2])
        db.commit()
        word_translation = WordTranslation(word_translated_id=word_en.id, word_original_id=word_ua.id)
        word_translation.word_translated = word_en
        word_translation.word_original = word_ua
        translation = word_translation
        question = build_msq_question(translation)
        question_json = question.get()
        assert question_json.question == f"Translate the word: {translation.word_original.word}"
        assert word_en.word in question_json.options
        assert word_en2.word in question_json.options

import pytest

from database import get_db
from database.models import User, Word, WordTranslation
from test_system.main import NoQuestionsException
from test_system.random.words import WordTranslationsTestBuilder
from unit_tests.tools import clear_database


class TestWordTranslationsTestBuilder:

    def setup_method(self):
        clear_database()
        self.generator = WordTranslationsTestBuilder()
        self.db = next(get_db())
        self.word_translation = WordTranslation()
        self.word_original = Word(word="привіт", language="ua")
        self.word_translated = Word(word="hi", language="en")
        self.db.add(self.word_original)
        self.db.add(self.word_translated)
        self.db.commit()
        self.word_translation.word_original_id = self.word_original.id
        self.word_translation.word_translated_id = self.word_translated.id
        self.db.add(self.word_translation)
        self.user = User(email="email@email.com", name="Test", surname="User", password_hash="hashed_password")
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)
        self.db.expunge(self.user)

    def test_ok(self):
        test = self.generator.build(self.user, number=3)
        for i in range(3):
            question = test.get_question()
            assert question.question == f"Translate the word: {self.word_original.word}"
            result = test.give_answer(self.word_translated.word)
            assert result.is_correct is True
            assert result.correct_answer == self.word_translated.word
        assert test.get_question() is None
        with pytest.raises(NoQuestionsException):
            test.give_answer("answer")

    def test_ok2(self):
        test = self.generator.build(self.user)
        for i in range(10):
            question = test.get_question()
            assert question.question == f"Translate the word: {self.word_original.word}"
            result = test.give_answer(self.word_translated.word)
            assert result.is_correct is True
            assert result.correct_answer == self.word_translated.word
        assert test.get_question() is None
        with pytest.raises(NoQuestionsException):
            test.give_answer("answer")

    def test_wrong(self):
        test = self.generator.build(self.user)
        for i in range(10):
            question = test.get_question()
            assert question.question == f"Translate the word: {self.word_original.word}"
            result = test.give_answer("wrong answer")
            assert result.is_correct is False
            assert result.correct_answer == self.word_translated.word
        assert test.get_question() is None
        with pytest.raises(NoQuestionsException):
            test.give_answer("answer")

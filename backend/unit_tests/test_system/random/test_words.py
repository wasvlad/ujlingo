import pytest
from unittest.mock import patch, AsyncMock, Mock

from database import get_db
from database.models import User, Base, Word, WordTranslation
from test_system.main import NoQuestionsException
from test_system.random.words import WordsTranslationQuestion as Question, WordTranslationsTestBuilder
from unit_tests.tools import clear_database


class TestWordsTranslationQuestion:
    def setup_class(self):
        self.word_translation = WordTranslation()
        self.word_original = Word(word="hello")
        self.word_translated = Word(word="привіт")
        self.word_translation.word_original = self.word_original
        self.word_translation.word_translated = self.word_translated
        self.question = Question(self.word_translation)

    def test_give_answer_correct(self):
        result = self.question.give_answer(self.word_translated.word)
        assert result.correct_answer == self.word_translated.word
        assert result.is_correct is True

    def test_give_answer_wrong(self):
        result = self.question.give_answer("wrong answer")
        assert result.correct_answer == self.word_translated.word
        assert result.is_correct is False

    def test_get_question(self):
        result = self.question.get()
        assert result.question == f"Translate the word: {self.word_original.word}"


class TestWordTranslationsTestBuilder:

    def setup_class(self):
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
        self.db.commit()

    def test_ok(self):
        test = self.generator.build(User(), number=3)
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
        test = self.generator.build(User())
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
        test = self.generator.build(User())
        for i in range(10):
            question = test.get_question()
            assert question.question == f"Translate the word: {self.word_original.word}"
            result = test.give_answer("wrong answer")
            assert result.is_correct is False
            assert result.correct_answer == self.word_translated.word
        assert test.get_question() is None
        with pytest.raises(NoQuestionsException):
            test.give_answer("answer")

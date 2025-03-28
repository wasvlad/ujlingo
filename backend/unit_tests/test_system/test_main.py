from database import get_db
from database.models import WordTranslation, Word
from test_system.words import WordsTranslationQuestion as Question
from unit_tests.tools import clear_database


class TestWordsTranslationQuestion:
    def setup_class(self):
        clear_database()
        db = next(get_db())
        self.word_translation = WordTranslation()
        self.word_translation2 = WordTranslation()
        self.word_original = Word(word="hello", language="en")
        self.word_translated = Word(word="привіт", language="ua")
        self.word_translated2 = Word(word="алло", language="ua")
        db.add_all([self.word_original, self.word_translated, self.word_translated2])
        db.commit()
        self.word_translation.word_original_id = self.word_original.id
        self.word_translation.word_translated_id = self.word_translated.id
        self.word_translation2.word_translated_id = self.word_translated2.id
        self.word_translation2.word_original_id = self.word_original.id
        db.add_all([self.word_translation, self.word_translation2])
        db.commit()
        self.question = Question(self.word_translation)
        self.word_original = self.word_original.word
        self.word_translated = self.word_translated.word
        self.word_translated2 = self.word_translated2.word

    def test_give_answer_correct(self):
        result = self.question.give_answer(self.word_translated)
        assert result.correct_answer == self.word_translated
        assert result.is_correct is True

    def test_give_answer_correct2(self):
        result = self.question.give_answer(self.word_translated2)
        assert result.correct_answer == self.word_translated
        assert result.is_correct is True

    def test_give_answer_wrong(self):
        result = self.question.give_answer("wrong answer")
        assert result.correct_answer == self.word_translated
        assert result.is_correct is False

    def test_get_question(self):
        result = self.question.get()
        assert result.question == f"Translate the word: {self.word_original}"

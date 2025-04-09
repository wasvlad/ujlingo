from database import get_db
from database.models import SentenceTranslation as Translation, Sentence
from endpoints.user.hashing import hash_password
from test_system.sentences import TranslationQuestion
from test_system.main import Result
from unit_tests.tools import clear_database


class TestTranslationQuestion:
    def setup_class(self):
        clear_database()
        db = next(get_db())
        self.original = Sentence(sentence="hello world", language="en")
        self.translated = Sentence(sentence="привіт світ", language="ua")
        self.translated2 = Sentence(sentence="вітаю світ", language="ua")
        db.add_all([self.original, self.translated, self.translated2])
        db.commit()
        db.refresh(self.original)
        db.refresh(self.translated)
        db.refresh(self.translated2)
        db.expunge(self.original)
        db.expunge(self.translated)
        db.expunge(self.translated2)
        self.translation = Translation()
        self.translation2 = Translation()
        self.translation.sentence_original_id = self.original.id
        self.translation.sentence_translated_id = self.translated.id
        self.translation2.sentence_original_id = self.original.id
        self.translation2.sentence_translated_id = self.translated2.id
        db.add_all([self.translation, self.translation2])
        db.commit()
        db.refresh(self.translation)
        db.refresh(self.translation2)
        db.expunge(self.translation)
        db.expunge(self.translation2)
        self.question = TranslationQuestion(self.translation)

    def test_give_answer_correct(self):
        result = self.question.give_answer(self.translated.sentence)
        assert result.correct_answer == self.translated.sentence
        assert result.is_correct is True

    def test_give_answer_correct2(self):
        result = self.question.give_answer(self.translated2.sentence)
        assert result.correct_answer == self.translated.sentence
        assert result.is_correct is True

    def test_give_answer_wrong(self):
        result = self.question.give_answer("wrong answer")
        assert result.correct_answer == self.translated.sentence
        assert result.is_correct is False

    def test_give_answer_wrong2(self):
        result = self.question.give_answer(self.original.sentence)
        assert result.correct_answer == self.translated.sentence
        assert result.is_correct is False

    def test_get_question(self):
        result = self.question.get()
        assert result.question == f"Translate the sentence: {self.original.sentence}"

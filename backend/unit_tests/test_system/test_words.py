from database import get_db
from database.models import WordTranslation, Word, User, WordTranslationKnowledge as TranslationKnowledge
from endpoints.user.hashing import hash_password
from test_system.words import TranslationQuestion as Question, TranslationKnowledgeSaver, MSQQuestion, LanguageException
from test_system.main import Result
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
        assert result.type == 0


class TestTranslationKnowledgeSaver:
    def setup_method(self):
        clear_database()
        db = next(get_db())
        self.word_translation = WordTranslation()
        self.word_original = Word(word="hello", language="en")
        self.word_translated = Word(word="привіт", language="ua")
        db.add_all([self.word_original, self.word_translated])
        db.commit()
        self.word_translation.word_original_id = self.word_original.id
        self.word_translation.word_translated_id = self.word_translated.id
        db.add_all([self.word_translation])
        db.commit()
        self.user = User(email="test@example.com", name="Test", surname="User",
                         password_hash=hash_password("password"),
                         is_confirmed=True)
        db.add(self.user)
        db.commit()
        db.refresh(self.user)
        db.expunge(self.user)
        db.refresh(self.word_translated)
        db.expunge(self.word_translated)

    def test_normal_flow(self):
        saver = TranslationKnowledgeSaver(self.user, self.word_translation)
        saver.asked()
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(TranslationKnowledge.user_id == self.user.id,
                                                          TranslationKnowledge.word_translation_id == self.word_translation.id).first()
        assert knowledge is not None
        assert knowledge.knowledge == 0
        saver.answered(Result(is_correct=True, correct_answer="correct answer"))
        db.refresh(knowledge)
        assert knowledge.knowledge == 20
        knowledge.knowledge = 100
        db.commit()
        saver.asked()
        assert knowledge.knowledge == 75
        saver.answered(Result(is_correct=False, correct_answer="wrong answer"))
        db.refresh(knowledge)
        assert knowledge.knowledge == 50

    def test_not_asked(self):
        saver = TranslationKnowledgeSaver(self.user, self.word_translation)
        saver.answered(Result(is_correct=True, correct_answer="wrong answer"))
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(TranslationKnowledge.user_id == self.user.id,
                                                          TranslationKnowledge.word_translation_id == self.word_translation.id).first()
        assert knowledge is not None
        assert knowledge.knowledge == 20


class TestMSQQuestion:
    def setup_method(self):
        clear_database()
        db = next(get_db())
        self.word_original = Word(word="привіт", language="ua")
        self.word_translated = Word(word="hello", language="en")
        self.word_translated2 = Word(word="hi", language="en")
        self.word_bye = Word(word="bye", language="en")
        self.word_ua = Word(word="бувай", language="ua")
        db.add_all([self.word_original, self.word_translated, self.word_translated2,
                    self.word_bye, self.word_ua])
        db.commit()
        self.word_translation = WordTranslation()
        self.word_translation.word_original_id = self.word_original.id
        self.word_translation.word_translated_id = self.word_translated.id
        self.word_translation2 = WordTranslation()
        self.word_translation2.word_original_id = self.word_original.id
        self.word_translation2.word_translated_id = self.word_translated2.id
        db.add_all([self.word_translation, self.word_translation2])
        db.commit()
        db.refresh(self.word_translated)
        db.expunge(self.word_translated)
        db.refresh(self.word_original)
        db.expunge(self.word_original)
        db.refresh(self.word_translation)
        db.refresh(self.word_translation.word_original)
        db.refresh(self.word_translation.word_translated)
        db.expunge(self.word_translation)
        db.refresh(self.word_bye)
        db.expunge(self.word_bye)
        db.refresh(self.word_ua)
        db.expunge(self.word_ua)
        self.question = MSQQuestion(self.word_translation, options=[self.word_translated2, self.word_bye])

    def test_get(self):
        result = self.question.get()
        assert result.question == f"Translate the word: {self.word_original.word}"
        assert "hi" in result.options
        assert "bye" in result.options
        assert "hello" in result.options
        assert len(result.options) == 3
        assert result.type == 1

    def test_give_answer_ok(self):
        result = self.question.give_answer("hi")
        assert result.is_correct is True

    def test_give_answer_ok2(self):
        result = self.question.give_answer("hello")
        assert result.is_correct is True

    def test_give_answer_wrong(self):
        result = self.question.give_answer("bye")
        assert result.is_correct is False
        assert result.correct_answer == self.word_translated.word

    def test_init_error(self):
        try:
            MSQQuestion(self.word_translation, options=[self.word_ua])
        except LanguageException:
            assert True
            return
        assert False
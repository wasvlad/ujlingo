from database import get_db
from database.models import (SentenceTranslation as Translation, Sentence, User,
                             SentenceTranslationKnowledge as TranslationKnowledge)
from endpoints.user.hashing import hash_password
from test_system.main import QuestionTypeEnum, Result
from test_system.sentences import TranslationQuestion, ReorderTranslationQuestion, TranslationKnowledgeSaver
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
        db.refresh(self.translation.sentence_translated)
        db.refresh(self.translation.sentence_original)
        db.refresh(self.translation2)
        db.refresh(self.translation2.sentence_translated)
        db.refresh(self.translation2.sentence_original)
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


class TestReorderTranslationQuestion:
    def setup_class(self):
        clear_database()
        db = next(get_db())
        self.original = Sentence(sentence="hello world!", language="en")
        self.translated = Sentence(sentence="привіт світ!", language="ua")
        db.add_all([self.original, self.translated])
        db.commit()
        db.refresh(self.original)
        db.refresh(self.translated)
        db.expunge(self.original)
        db.expunge(self.translated)
        self.translation = Translation()
        self.translation.sentence_original_id = self.original.id
        self.translation.sentence_translated_id = self.translated.id
        db.add_all([self.translation])
        db.commit()
        db.refresh(self.translation)
        db.refresh(self.translation.sentence_translated)
        db.refresh(self.translation.sentence_original)
        db.expunge(self.translation)
        self.question = ReorderTranslationQuestion(self.translation)

    def test_give_answer_correct(self):
        result = self.question.give_answer(self.translated.sentence)
        assert result.correct_answer == self.translated.sentence
        assert result.is_correct is True

    def test_give_answer_wrong(self):
        result = self.question.give_answer("wrong answer")
        assert result.correct_answer == self.translated.sentence
        assert result.is_correct is False

    def test_get_question(self):
        result = self.question.get()
        assert result.question == f"Translate the sentence: {self.original.sentence}"
        tokens = ['привіт', 'світ', '!']
        for token in tokens:
            assert token in result.tokens
        for token in result.tokens:
            assert token in tokens
        assert result.type == QuestionTypeEnum.reorder.value


class TestTranslationKnowledgeSaver:
    def setup_method(self):
        clear_database()
        db = next(get_db())
        self.translation = Translation()
        self.original = Sentence(sentence="hello world", language="en")
        self.translated = Sentence(sentence="привіт світ", language="ua")
        db.add_all([self.original, self.translated])
        db.commit()
        db.refresh(self.original)
        db.refresh(self.translated)
        db.expunge(self.translated)
        db.expunge(self.original)
        self.translation.sentence_original_id = self.original.id
        self.translation.sentence_translated_id = self.translated.id
        db.add(self.translation)
        db.commit()
        db.refresh(self.translation)
        db.refresh(self.translation.sentence_translated)
        db.refresh(self.translation.sentence_original)
        db.expunge(self.translation)
        self.user = User(email="test@example.com", name="Test", surname="User",
                         password_hash=hash_password("password"),
                         is_confirmed=True)
        db.add(self.user)
        db.commit()
        db.refresh(self.user)
        db.expunge(self.user)

    def test_normal_flow(self):
        saver = TranslationKnowledgeSaver(self.user, self.translation)
        saver.asked()
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(TranslationKnowledge.user_id == self.user.id,
                                                          TranslationKnowledge.sentence_translation_id == self.translation.id).first()
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
        saver = TranslationKnowledgeSaver(self.user, self.translation)
        saver.answered(Result(is_correct=True, correct_answer="wrong answer"))
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(TranslationKnowledge.user_id == self.user.id,
                                                          TranslationKnowledge.sentence_translation_id == self.translation.id).first()
        assert knowledge is not None
        assert knowledge.knowledge == 20
from test_system.builder.question import *
from database import get_db
from database.models import (Word, WordTranslation, WordTranslationKnowledge, User, Sentence, SentenceTranslation,
                             SentenceTranslationKnowledge)
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

class TestGetNewWords:
    def setup_method(self):
        clear_database()
        self.user = User(email="test@example.com", name="Test", surname="User", password_hash="<PASSWORD>")
        self.user.is_confirmed = True
        self.db = next(get_db())
        self.db.add(self.user)
        self.db.commit()
        self.word_en = "hello"
        self.word_ua = "привіт"
        self.word_en2 = "hi"
        self.word_en_db = Word(word=self.word_en, language="en")
        self.word_ua_db = Word(word=self.word_ua, language="ua")
        self.word_en2_db = Word(word=self.word_en2, language="en")
        self.db.add_all([self.word_en_db, self.word_ua_db, self.word_en2_db])
        self.db.commit()
        self.word_translation = WordTranslation(word_translated_id=self.word_en_db.id, word_original_id=self.word_ua_db.id)
        self.word_translation2 = WordTranslation(word_translated_id=self.word_en2_db.id, word_original_id=self.word_ua_db.id)
        self.db.add_all([self.word_translation, self.word_translation2])
        self.db.commit()

    def test_ok(self):
        knowledge1 = WordTranslationKnowledge(word_translation_id=self.word_translation.id, knowledge=0,
                                              user_id=self.user.id)
        self.db.add_all([knowledge1])
        self.db.commit()
        new_words = get_new_word_translations(2, 10)
        assert len(new_words) == 2
        assert new_words[0].id == self.word_translation.id or new_words[0].id == self.word_translation2.id
        assert new_words[1].id == self.word_translation.id or new_words[1].id == self.word_translation2.id
        assert new_words[0].id != new_words[1].id

    def test_small_knowledge(self):
        self.db.commit()
        knowledge1 = WordTranslationKnowledge(word_translation_id=self.word_translation.id, knowledge=10,
                                              user_id=self.user.id)
        self.db.add_all([knowledge1])
        self.db.commit()
        new_words = get_new_word_translations(2, 0)
        assert len(new_words) == 1
        assert new_words[0].id == self.word_translation2.id

    def test_number_one(self):
        self.db.commit()
        knowledge1 = WordTranslationKnowledge(word_translation_id=self.word_translation.id, knowledge=10,
                                              user_id=self.user.id)
        self.db.add_all([knowledge1])
        self.db.commit()
        new_words = get_new_word_translations(1, 30)
        assert len(new_words) == 1
        assert new_words[0].id == self.word_translation.id or new_words[0].id == self.word_translation2.id


class TestGetWeakKnowledgeWords:
    def setup_method(self):
        clear_database()
        self.user = User(email="test@example.com", name="Test", surname="User", password_hash="<PASSWORD>")
        self.user.is_confirmed = True
        self.db = next(get_db())
        self.db.add(self.user)
        self.db.commit()
        self.word_en = "hello"
        self.word_ua = "привіт"
        self.word_en2 = "hi"
        self.word_en_db = Word(word=self.word_en, language="en")
        self.word_ua_db = Word(word=self.word_ua, language="ua")
        self.word_en2_db = Word(word=self.word_en2, language="en")
        self.db.add_all([self.word_en_db, self.word_ua_db, self.word_en2_db])
        self.db.commit()
        self.word_translation = WordTranslation(word_translated_id=self.word_en_db.id, word_original_id=self.word_ua_db.id)
        self.word_translation2 = WordTranslation(word_translated_id=self.word_en2_db.id, word_original_id=self.word_ua_db.id)
        self.db.add_all([self.word_translation, self.word_translation2])
        self.db.commit()
        self.knowledge1 = WordTranslationKnowledge(user_id=self.user.id, word_translation_id=self.word_translation.id, knowledge=30)
        self.db.add(self.knowledge1)
        self.db.commit()

    def test_ok(self):
        bad_words = get_word_translations_weak_knowledge(2)
        assert len(bad_words) == 1
        assert bad_words[0].id == self.word_translation.id

    def test_big_min(self):
        new_words = get_word_translations_weak_knowledge(2, min_knowledge=40)
        assert len(new_words) == 0

    def test_small_max(self):
        new_words = get_word_translations_weak_knowledge(2, max_knowledge=20)
        assert len(new_words) == 0


class TestGetStrongKnowledgeWords:
    def setup_method(self):
        clear_database()
        self.user = User(email="test@example.com", name="Test", surname="User", password_hash="<PASSWORD>")
        self.user.is_confirmed = True
        self.db = next(get_db())
        self.db.add(self.user)
        self.db.commit()
        self.word_en = "hello"
        self.word_ua = "привіт"
        self.word_en2 = "hi"
        self.word_en_db = Word(word=self.word_en, language="en")
        self.word_ua_db = Word(word=self.word_ua, language="ua")
        self.word_en2_db = Word(word=self.word_en2, language="en")
        self.db.add_all([self.word_en_db, self.word_ua_db, self.word_en2_db])
        self.db.commit()
        self.word_translation = WordTranslation(word_translated_id=self.word_en_db.id, word_original_id=self.word_ua_db.id)
        self.word_translation2 = WordTranslation(word_translated_id=self.word_en2_db.id, word_original_id=self.word_ua_db.id)
        self.db.add_all([self.word_translation, self.word_translation2])
        self.db.commit()
        self.knowledge1 = WordTranslationKnowledge(user_id=self.user.id, word_translation_id=self.word_translation.id, knowledge=100)
        self.db.add(self.knowledge1)
        self.db.commit()

    def test_ok(self):
        strong_words = get_word_translations_strong_knowledge(2)
        assert len(strong_words) == 1
        assert strong_words[0].id == self.word_translation.id

    def test_ok2(self):
        knowledge2 = WordTranslationKnowledge(user_id=self.user.id, word_translation_id=self.word_translation2.id,
                                                   knowledge=80)
        self.db.add(knowledge2)
        self.db.commit()
        strong_words = get_word_translations_strong_knowledge(2)
        assert len(strong_words) == 2
        assert strong_words[0].id in [self.word_translation.id, self.word_translation2.id]
        assert strong_words[1].id in [self.word_translation.id, self.word_translation2.id]
        assert strong_words[0].id != strong_words[1].id

    def test_ok3(self):
        knowledge2 = WordTranslationKnowledge(user_id=self.user.id, word_translation_id=self.word_translation2.id,
                                                   knowledge=80)
        self.db.add(knowledge2)
        self.db.commit()
        strong_words = get_word_translations_strong_knowledge(1)
        assert len(strong_words) == 1
        assert strong_words[0].id in [self.word_translation.id, self.word_translation2.id]

    def test_small_min(self):
        strong_words = get_word_translations_strong_knowledge(2, min_knowledge=40)
        assert len(strong_words) == 1
        assert strong_words[0].id == self.word_translation.id

    def test_big_min(self):
        knowledge2 = WordTranslationKnowledge(user_id=self.user.id, word_translation_id=self.word_translation2.id,
                                                   knowledge=80)
        self.db.add(knowledge2)
        self.db.commit()
        strong_words = get_word_translations_strong_knowledge(2, min_knowledge=90)
        assert len(strong_words) == 1
        assert strong_words[0].id == self.word_translation.id

class TestGetNewSentences:
    def setup_method(self):
        clear_database()
        self.user = User(email="test@example.com", name="Test", surname="User", password_hash="<PASSWORD>")
        self.user.is_confirmed = True
        self.db = next(get_db())
        self.db.add(self.user)
        self.db.commit()
        self.sentence_en = "hello world"
        self.sentence_ua = "привіт світ"
        self.sentence_ua2 = "хей світ"
        self.sentence_en_db = Sentence(sentence=self.sentence_en, language="en")
        self.sentence_ua2_db = Sentence(sentence=self.sentence_ua2, language="en")
        self.sentence_ua_db = Sentence(sentence=self.sentence_ua, language="ua")
        self.db.add_all([self.sentence_en_db, self.sentence_ua_db, self.sentence_ua2_db])
        self.db.commit()
        self.sentence_translation = SentenceTranslation(sentence_translated_id=self.sentence_en_db.id, sentence_original_id=self.sentence_ua_db.id)
        self.sentence_translation2 = SentenceTranslation(sentence_translated_id=self.sentence_en_db.id, sentence_original_id=self.sentence_ua2_db.id)
        self.db.add_all([self.sentence_translation, self.sentence_translation2])
        self.db.commit()

    def test_ok(self):
        knowledge1 = SentenceTranslationKnowledge(sentence_translation_id=self.sentence_translation.id, knowledge=0,
                                              user_id=self.user.id)
        self.db.add_all([knowledge1])
        self.db.commit()
        new_sentences = get_new_sentence_translations(2, 10)
        assert len(new_sentences) == 2
        assert new_sentences[0].id == self.sentence_translation.id or new_sentences[0].id == self.sentence_translation2.id
        assert new_sentences[1].id == self.sentence_translation.id or new_sentences[1].id == self.sentence_translation2.id
        # translations should be different
        assert new_sentences[0].id != new_sentences[1].id

    def test_small_knowledge(self):
        self.db.commit()
        knowledge1 = SentenceTranslationKnowledge(sentence_translation_id=self.sentence_translation.id, knowledge=10,
                                              user_id=self.user.id)
        self.db.add_all([knowledge1])
        self.db.commit()
        new_sentences = get_new_sentence_translations(2, 0)
        assert len(new_sentences) == 1
        assert new_sentences[0].id == self.sentence_translation2.id

    def test_number_one(self):
        self.db.commit()
        knowledge1 = SentenceTranslationKnowledge(sentence_translation_id=self.sentence_translation.id, knowledge=10,
                                              user_id=self.user.id)
        self.db.add_all([knowledge1])
        self.db.commit()
        new_sentences = get_new_sentence_translations(1, 30)
        assert len(new_sentences) == 1
        assert new_sentences[0].id in [self.sentence_translation.id, self.sentence_translation2.id]

class TestGetWeakKnowledgeSentences:
    def setup_method(self):
        clear_database()
        self.user = User(email="test@example.com", name="Test", surname="User", password_hash="<PASSWORD>")
        self.user.is_confirmed = True
        self.db = next(get_db())
        self.db.add(self.user)
        self.db.commit()
        self.sentence_en = "hello world"
        self.sentence_ua = "привіт світ"
        self.sentence_ua2 = "хей світ"
        self.sentence_en_db = Sentence(sentence=self.sentence_en, language="en")
        self.sentence_ua2_db = Sentence(sentence=self.sentence_ua2, language="ua")
        self.sentence_ua_db = Sentence(sentence=self.sentence_ua, language="ua")
        self.db.add_all([self.sentence_en_db, self.sentence_ua_db, self.sentence_ua2_db])
        self.db.commit()
        self.sentence_translation = SentenceTranslation(sentence_translated_id=self.sentence_en_db.id,
                                                        sentence_original_id=self.sentence_ua_db.id)
        self.sentence_translation2 = SentenceTranslation(sentence_translated_id=self.sentence_en_db.id,
                                                         sentence_original_id=self.sentence_ua2_db.id)
        self.db.add_all([self.sentence_translation, self.sentence_translation2])
        self.db.commit()
        self.knowledge1 = SentenceTranslationKnowledge(user_id=self.user.id, sentence_translation_id=self.sentence_translation.id, knowledge=30)
        self.db.add(self.knowledge1)
        self.db.commit()

    def test_ok(self):
        weak_sentences = get_sentence_translations_weak_knowledge(2)
        assert len(weak_sentences) == 1
        assert weak_sentences[0].id == self.sentence_translation.id

    def test_big_min(self):
        new_sentences = get_sentence_translations_weak_knowledge(2, min_knowledge=40)
        assert len(new_sentences) == 0

    def test_small_max(self):
        new_sentences = get_sentence_translations_weak_knowledge(2, max_knowledge=20)
        assert len(new_sentences) == 0
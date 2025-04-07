import pytest
from endpoints.admin.data_migration import words_translations_to_pairs
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from main import app
from database.models import User, Base, Word, WordTranslation, Sentence, SentenceTranslation
from database import get_db, DatabaseSession, engine
from endpoints.admin.tools import validate_admin_session

class TestWordsTranslationsToPairs:

    def test_words_translations_to_pairs(self):
        data = {
            "hello": ["привіт", "алло"],
            "world": ["світ", "планета"]
        }
        result = words_translations_to_pairs(data)
        assert result == [
            ("hello", "привіт"),
            ("hello", "алло"),
            ("world", "світ"),
            ("world", "планета")
        ]

# Mock dependencies
def override_validate_admin_session():
    return User(id=1, is_admin=True)

def override_get_db():
    return AsyncMock()

class TestMigrateWords:

    @pytest.fixture
    def client(self):
        app.dependency_overrides[validate_admin_session] = override_validate_admin_session
        return TestClient(app)

    @staticmethod
    def setup_method():
        DatabaseSession.close_all()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password"))
        db.commit()

    def teardown_class(self):
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_migrate_words_success(self, client):
        db = next(get_db())
        word_ua_1 = Word(word="привіт", language="ua")
        word_ua_2 = Word(word="алло", language="ua")
        word_ua_3 = Word(word="світ", language="ua")
        word_ua_4 = Word(word="До побачення", language="ua")
        word_en_1 = Word(word="hello", language="en")
        word_en_2 = Word(word="world", language="en")
        word_en_3 = Word(word="bye", language="en")
        db.add_all([word_ua_1, word_ua_2, word_ua_3, word_ua_4, word_en_1, word_en_2, word_en_3])
        db.commit()
        word_translation_1 = WordTranslation(word_original_id=word_en_1.id, word_translated_id=word_ua_1.id)
        word_translation_1r = WordTranslation(word_original_id=word_ua_1.id, word_translated_id=word_en_1.id)
        word_translation_2 = WordTranslation(word_original_id=word_en_1.id, word_translated_id=word_ua_2.id)
        word_translation_2r = WordTranslation(word_original_id=word_ua_2.id, word_translated_id=word_en_1.id)
        word_translation_3 = WordTranslation(word_original_id=word_en_2.id, word_translated_id=word_ua_3.id)
        word_translation_3r = WordTranslation(word_original_id=word_ua_3.id, word_translated_id=word_en_2.id)
        word_translation_4 = WordTranslation(word_original_id=word_en_3.id, word_translated_id=word_ua_4.id)
        word_translation_4r = WordTranslation(word_original_id=word_ua_4.id, word_translated_id=word_en_3.id)

        db.add_all([word_translation_1, word_translation_2, word_translation_3, word_translation_4])
        db.add_all([word_translation_1r, word_translation_2r, word_translation_3r, word_translation_4r])
        db.commit()

        mock_response = Mock()
        mock_response.json.return_value = {"hello": ["привіт", "алло"], "world": ["світ", "планета"]}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None  # Mock raise_for_status()
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            response = client.post("/admin/sync-words",
                                   headers={"content-type": "application/json", "access-token": "access_token"})
            assert response.status_code == 200
            assert response.json() == {"message": "Words migrated successfully"}
        expected = [("hello", "привіт"), ("hello", "алло"), ("world", "світ"), ("world", "планета")]
        expected_ua = ["привіт", "алло", "світ", "планета"]
        expected_en = ["hello", "world"]
        ua_words = db.query(Word).filter(Word.language == "ua").all()
        assert len(ua_words) == len(expected_ua)
        for word in ua_words:
            assert word.word in expected_ua
        en_words = db.query(Word).filter(Word.language == "en").all()
        assert len(en_words) == len(expected_en)
        for word in en_words:
            assert word.word in expected_en
        translations = db.query(WordTranslation).all()
        assert len(translations) == len(expected) * 2
        for translation in translations:
            word_en = None
            word_ua = None
            if translation.word_original.language == "ua":
                word_ua = translation.word_original.word
            elif translation.word_translated.language == "ua":
                word_ua = translation.word_translated.word
            if translation.word_original.language == "en":
                word_en = translation.word_original.word
            elif translation.word_translated.language == "en":
                word_en = translation.word_translated.word

            assert (word_en, word_ua) in expected


class TestMigrateSentences:

    @pytest.fixture
    def client(self):
        app.dependency_overrides[validate_admin_session] = override_validate_admin_session
        return TestClient(app)

    @staticmethod
    def setup_method():
        DatabaseSession.close_all()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password"))
        db.commit()

    def teardown_class(self):
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_migrate_sentences_success(self, client):
        db = next(get_db())
        sentence_ua_1 = Sentence(sentence="привіт світ", language="ua")
        sentence_ua_2 = Sentence(sentence="як справи?", language="ua")
        sentence_en_1 = Sentence(sentence="hello world", language="en")
        sentence_en_2 = Sentence(sentence="How are you?", language="en")
        db.add_all([sentence_ua_1, sentence_ua_2, sentence_en_1, sentence_en_2])
        db.commit()
        translation1 = SentenceTranslation(sentence_original_id=sentence_ua_1.id, sentence_translated_id=sentence_en_1.id)
        translation1_r = SentenceTranslation(sentence_original_id=sentence_en_1.id, sentence_translated_id=sentence_ua_1.id)
        translation2 = SentenceTranslation(sentence_original_id=sentence_ua_2.id, sentence_translated_id=sentence_en_2.id)
        translation2_r = SentenceTranslation(sentence_original_id=sentence_en_2.id, sentence_translated_id=sentence_ua_2.id)
        db.add_all([translation1, translation1_r, translation2, translation2_r])
        db.commit()

        mock_response = Mock()
        mock_response.json.return_value = {"як справи?": ["how are you?"], "що робиш?": ["what are you doing?"]}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None  # Mock raise_for_status()
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            response = client.post("/admin/sync-sentences",
                                   headers={"content-type": "application/json", "access-token": "access_token"})
            assert response.status_code == 200
            assert response.json() == {"message": "Sentences migrated successfully"}
        expected = [("як справи?", "how are you?"), ("що робиш?", "what are you doing?")]
        expected_ua = ["як справи?", "що робиш?"]
        expected_en = ["how are you?", "what are you doing?"]
        ua = db.query(Sentence).filter(Sentence.language == "ua").all()
        assert len(ua) == len(expected_ua)
        for sentence in ua:
            assert sentence.sentence in expected_ua
        en = db.query(Sentence).filter(Sentence.language == "en").all()
        assert len(en) == len(expected_en)
        for sentence in en:
            assert sentence.sentence in expected_en
        translations = db.query(SentenceTranslation).all()
        assert len(translations) == len(expected) * 2
        for translation in translations:
            en = None
            ua = None
            if translation.sentence_original.language == "ua":
                ua = translation.sentence_original.sentence
            elif translation.sentence_translated.language == "ua":
                ua = translation.sentence_translated.sentence
            if translation.sentence_original.language == "en":
                en = translation.sentence_original.sentence
            elif translation.sentence_translated.language == "en":
                en = translation.sentence_translated.sentence

            assert (ua, en) in expected

import pytest
from endpoints.admin.data_migration import words_translations_to_pairs
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from main import app
from database.models import User, Base, WordUa, WordTranslation, WordEn
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
    def setup_class(self):
        self.session = DatabaseSession()

    @pytest.fixture
    def client(self):
        app.dependency_overrides[get_db] = self.override_get_db
        app.dependency_overrides[validate_admin_session] = override_validate_admin_session
        return TestClient(app)

    @staticmethod
    def setup_method(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db = next(get_db())
        db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password"))
        db.commit()

    def override_get_db(self):
        return self.session

    def teardown_class(self):
        self.session.close()

    @pytest.mark.asyncio
    async def test_migrate_words_success(self, client):
        db = next(get_db())
        word_ua_1 = WordUa(word="привіт")
        word_ua_2 = WordUa(word="алло")
        word_ua_3 = WordUa(word="світ")
        word_ua_4 = WordUa(word="До побачення")
        word_en_1 = WordEn(word="hello")
        word_en_2 = WordEn(word="world")
        word_en_3 = WordEn(word="bye")
        db.add_all([word_ua_1, word_ua_2, word_ua_3, word_ua_4, word_en_1, word_en_2, word_en_3])
        db.commit()
        word_translation_1 = WordTranslation(word_en_id=word_en_1.id, word_ua_id=word_ua_1.id)
        word_translation_2 = WordTranslation(word_en_id=word_en_1.id, word_ua_id=word_ua_2.id)
        word_translation_3 = WordTranslation(word_en_id=word_en_2.id, word_ua_id=word_ua_3.id)
        word_translation_4 = WordTranslation(word_en_id=word_en_3.id, word_ua_id=word_ua_4.id)

        db.add_all([word_translation_1, word_translation_2, word_translation_3, word_translation_4])
        db.commit()

        mock_response = Mock()
        mock_response.json.return_value = {"hello": ["привіт", "алло"], "world": ["світ", "планета"]}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None  # Mock raise_for_status()
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            response = client.post("/admin/migrate-words",
                                   headers={"content-type": "application/json", "access-token": "access_token"})
            assert response.status_code == 200
            assert response.json() == {"message": "Words migrated successfully"}
        expected = [("hello", "привіт"), ("hello", "алло"), ("world", "світ"), ("world", "планета")]
        expected_ua = ["привіт", "алло", "світ", "планета"]
        expected_en = ["hello", "world"]
        ua_words = db.query(WordUa).all()
        assert len(ua_words) == len(expected_ua)
        for word in ua_words:
            assert word.word in expected_ua
        en_words = db.query(WordEn).all()
        assert len(en_words) == len(expected_en)
        for word in en_words:
            assert word.word in expected_en
        translations = db.query(WordTranslation).join(WordEn).join(WordUa).all()
        assert len(translations) == len(expected)
        for translation in translations:
            assert (translation.word_en.word, translation.word_ua.word) in expected

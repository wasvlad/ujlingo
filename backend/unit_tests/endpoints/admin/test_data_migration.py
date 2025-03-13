import pytest
from endpoints.admin.data_migration import words_translations_to_pairs
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from main import app
from database.models import User, Base, WordsToUa
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

class TestMigrateWordsToUa:
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
    async def test_migrate_words_to_ua_success(self, client):
        db = next(get_db())
        db.add(WordsToUa(original_word="bye", translated_word="Прощавай"))
        db.add(WordsToUa(original_word="bye", translated_word="До побачення"))
        db.add(WordsToUa(original_word="hello", translated_word="Привіт"))
        db.add(WordsToUa(original_word="hello", translated_word="Алло"))
        db.add(WordsToUa(original_word="hello", translated_word="Шо ти"))
        db.commit()
        mock_response = Mock()
        mock_response.json.return_value = {"hello": ["привіт", "алло"], "world": ["світ", "планета"]}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None  # Mock raise_for_status()
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            response = client.post("/admin/migrate-words-to-ua",
                                   headers={"content-type": "application/json", "access-token": "access_token"})
            assert response.status_code == 200
            assert response.json() == {"message": "Operation successful"}
        words = db.query(WordsToUa).all()
        expected = [("hello", "привіт"), ("hello", "алло"), ("world", "світ"), ("world", "планета")]
        for word in words:
            assert (word.original_word, word.translated_word) in expected
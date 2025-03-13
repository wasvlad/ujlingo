import pytest
from httpx import Response
from endpoints.admin.data_migration import words_translations_to_pairs, migrate_words_to_ua
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from main import app
from database.models import User
from database import get_db
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

    @pytest.fixture
    def mock_db(self):
        with patch("endpoints.user.tools.get_db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        app.dependency_overrides[validate_admin_session] = override_validate_admin_session
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_migrate_words_to_ua_success(self, client):
        mock_response = Mock()
        mock_response.json.return_value = {"hello": ["привіт", "алло"], "world": ["світ", "планета"]}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None  # Mock raise_for_status()
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            response = client.post("/admin/migrate-words-to-ua",
                                   headers={"content-type": "application/json", "access-token": "access_token"})
            assert response.status_code == 200
            assert response.json() == {"message": "Operation successful"}

    # @pytest.mark.asyncio
    # async def test_migrate_words_to_ua_failure(self, client):
    #     with patch("endpoints.admin.data_migration.httpx.AsyncClient.get",
    #                return_value=Response(404)), \
    #             patch("endpoints.admin.data_migration.validate_admin_session",
    #                   return_value=User(id=1, is_admin=True)), \
    #             patch("endpoints.admin.data_migration.get_db", return_value=AsyncMock()):
    #         response = client.post("/admin/migrate-words-to-ua",
    #                                headers={"content-type": "application/json", "access_token": "access_token"},)
    #         assert response.status_code == 404
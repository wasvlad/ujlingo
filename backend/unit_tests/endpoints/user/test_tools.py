import jwt
import pytest
from fastapi import HTTPException
from unittest.mock import patch
from endpoints.user.tools import validate_session

class TestValidateSession:

    @pytest.fixture
    def mock_db(self):
        with patch("endpoints.user.tools.get_db") as mock:
            yield mock

    @pytest.fixture
    def mock_jwt_decode(self):
        with patch("jwt.decode") as mock:
            yield mock

    def test_validate_session_success(self, mock_db, mock_jwt_decode):
        mock_jwt_decode.return_value = {"email": "test@example.com"}
        mock_db.query().filter().first.return_value = type("Session", (), {"is_active": True})

        token = "valid_token"
        result = validate_session(token, mock_db)
        assert result == token

    def test_validate_session_expired_token(self, mock_db, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError

        token = "expired_token"
        with pytest.raises(HTTPException) as exc_info:
            validate_session(token, mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token expired"

    def test_validate_session_invalid_token(self, mock_db, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.InvalidTokenError

        token = "invalid_token"
        with pytest.raises(HTTPException) as exc_info:
            validate_session(token, mock_db)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Invalid token"

    def test_validate_session_inactive_session(self, mock_db, mock_jwt_decode):
        mock_jwt_decode.return_value = {"email": "test@example.com"}
        mock_db.query().filter().first.return_value = type("Session", (), {"is_active": False})

        token = "inactive_token"
        with pytest.raises(HTTPException) as exc_info:
            validate_session(token, mock_db)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Invalid token"

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from endpoints.admin.tools import validate_admin_session

class TestValidateAdminSession:

    @patch("endpoints.admin.tools.validate_session")
    def test_validate_admin_session_valid(self, mock_validate_session):
        mock_user = MagicMock()
        mock_user.is_admin = True
        mock_user.id=1
        mock_validate_session.return_value = mock_user

        user = validate_admin_session(user=mock_user)
        assert user.is_admin
        assert user.id == 1

    @patch("endpoints.admin.tools.validate_session")
    def test_validate_admin_session_user_not_admin(self, mock_validate_session):
        mock_user = MagicMock()
        mock_user.is_admin = False
        mock_validate_session.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            validate_admin_session(user=mock_user)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Access denied"
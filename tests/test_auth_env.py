import os
import sys
import pytest
from unittest import mock
import importlib

# Ensure backend directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock sqlalchemy and db dependencies
mock_sqlalchemy = mock.MagicMock()
mock_db = mock.MagicMock()
mock_models = mock.MagicMock()

# Removed global mock assignment to avoid test suite pollution
# sys.modules['sqlalchemy'] = mock_sqlalchemy...


def test_auth_service_missing_secret():
    # If no secret key is provided, it should raise ValueError immediately
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="A secure SECRET_KEY must be provided"):
            with mock.patch.dict(sys.modules, {'sqlalchemy': mock_sqlalchemy, 'sqlalchemy.orm': mock.MagicMock(), 'sqlalchemy.ext.declarative': mock.MagicMock(), 'db': mock_db, 'models': mock_models}):
                import auth_service
                importlib.reload(auth_service)

def test_auth_service_with_secret():
    # If a secret key is provided, it should be loaded correctly
    with mock.patch.dict(os.environ, {'SECRET_KEY': 'super-secure-secret-key'}, clear=True):
        with mock.patch.dict(sys.modules, {'sqlalchemy': mock_sqlalchemy, 'sqlalchemy.orm': mock.MagicMock(), 'sqlalchemy.ext.declarative': mock.MagicMock(), 'db': mock_db, 'models': mock_models}):
            import auth_service
            importlib.reload(auth_service)
            assert auth_service.SECRET_KEY == 'super-secure-secret-key'

def test_auth_service_empty_secret():
    # If empty secret key is provided, it should raise ValueError
    with mock.patch.dict(os.environ, {'SECRET_KEY': ''}, clear=True):
        with pytest.raises(ValueError, match="A secure SECRET_KEY must be provided"):
            with mock.patch.dict(sys.modules, {'sqlalchemy': mock_sqlalchemy, 'sqlalchemy.orm': mock.MagicMock(), 'sqlalchemy.ext.declarative': mock.MagicMock(), 'db': mock_db, 'models': mock_models}):
                import auth_service
                importlib.reload(auth_service)

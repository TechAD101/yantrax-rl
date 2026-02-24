import pytest
import os
import sys

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture(autouse=True)
def mock_admin_key(monkeypatch):
    """Automatically set ADMIN_API_KEY for all tests to prevent auth failures."""
    monkeypatch.setenv("ADMIN_API_KEY", "test_secret")

    # Also patch Config if it's already imported
    try:
        from config import Config
        monkeypatch.setattr(Config, "ADMIN_API_KEY", "test_secret")
    except ImportError:
        pass

@pytest.fixture
def client():
    from main import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Add auth header to every request if possible, or just return client
        # Flask test client doesn't support global headers easily, so we might need a wrapper
        yield client

class AuthClientWrapper:
    def __init__(self, client, api_key):
        self.client = client
        self.api_key = api_key

    def get(self, *args, **kwargs):
        headers = kwargs.get('headers', {})
        headers['X-API-Key'] = self.api_key
        kwargs['headers'] = headers
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        headers = kwargs.get('headers', {})
        headers['X-API-Key'] = self.api_key
        kwargs['headers'] = headers
        return self.client.post(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.client, name)

@pytest.fixture
def auth_client(client):
    return AuthClientWrapper(client, "test_secret")

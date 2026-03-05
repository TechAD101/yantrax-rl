import os
import sys
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db import init_db, get_session
from auth_service import register_user, get_user

@pytest.fixture(scope='module', autouse=True)
def setup_db():
    init_db()
    yield

def test_get_user_success():
    """Test fetching an existing user by ID returns the correct user dictionary."""
    registered = register_user('get_user_tester', 'getuser@example.com', 'securepass123')
    user_id = registered.get('id')

    assert user_id is not None

    fetched_user = get_user(user_id)

    assert fetched_user is not None
    assert fetched_user['id'] == user_id
    assert fetched_user['username'] == 'get_user_tester'
    assert fetched_user['email'] == 'getuser@example.com'

def test_get_user_not_found():
    """Test fetching a non-existent user by ID returns None."""
    fetched_user = get_user(99999)
    assert fetched_user is None

import os
import sys
import pytest
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db import init_db
from auth_service import register_user, get_user

@pytest.fixture(scope='module', autouse=True)
def setup_db():
    init_db()
    yield

def test_get_user_success():
    """Test fetching an existing user by ID returns the correct user dictionary."""
    unique_id = str(uuid.uuid4())[:8]
    registered = register_user(f'tester_{unique_id}', f'test_{unique_id}@example.com', 'securepass123')
    user_id = registered.get('id')

    assert user_id is not None

    fetched_user = get_user(user_id)

    assert fetched_user is not None
    assert fetched_user['id'] == user_id
    assert fetched_user['username'] == f'tester_{unique_id}'
    assert fetched_user['email'] == f'test_{unique_id}@example.com'

def test_get_user_not_found():
    """Test fetching a non-existent user by ID returns None."""
    fetched_user = get_user(99999)
    assert fetched_user is None

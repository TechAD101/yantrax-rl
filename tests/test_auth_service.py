import os
import sys
import hashlib
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Use patch.dict to safely mock dependencies without polluting the global sys.modules for other tests
with patch.dict('sys.modules', {
    'sqlalchemy': MagicMock(),
    'sqlalchemy.orm': MagicMock(),
    'sqlalchemy.ext.declarative': MagicMock()
}):
    from auth_service import hash_password

def test_hash_password_basic():
    """Test hashing a normal string."""
    password = "my_secure_password"
    expected = hashlib.sha256(password.encode()).hexdigest()
    assert hash_password(password) == expected

def test_hash_password_empty():
    """Test hashing an empty string."""
    password = ""
    expected = hashlib.sha256(password.encode()).hexdigest()
    assert hash_password(password) == expected

def test_hash_password_special_chars():
    """Test hashing a string with special characters."""
    password = "!@#$%^&*()_+~`|}{[]:;?><,./-="
    expected = hashlib.sha256(password.encode()).hexdigest()
    assert hash_password(password) == expected

def test_hash_password_unicode():
    """Test hashing a string with Unicode characters (emojis)."""
    password = "hello🌍world🔥"
    expected = hashlib.sha256(password.encode()).hexdigest()
    assert hash_password(password) == expected

def test_hash_password_deterministic():
    """Test that hashing the same string twice produces the same result."""
    password = "deterministic_test"
    assert hash_password(password) == hash_password(password)

def test_hash_password_different_inputs():
    """Test that different inputs produce different hashes."""
    assert hash_password("password123") != hash_password("password124")

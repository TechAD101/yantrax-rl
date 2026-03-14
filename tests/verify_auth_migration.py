import sys
import hashlib
from unittest.mock import MagicMock, patch

# Mock dependencies
mock_passlib = MagicMock()
mock_passlib_context = MagicMock()
mock_passlib.context = mock_passlib_context

mock_sqlalchemy = MagicMock()
mock_db = MagicMock()
mock_models = MagicMock()

sys.modules['passlib'] = mock_passlib
sys.modules['passlib.context'] = mock_passlib_context
sys.modules['sqlalchemy'] = mock_sqlalchemy
sys.modules['db'] = mock_db
sys.modules['models'] = mock_models

# Now import the service under test
import backend.auth_service as auth_service

def test_legacy_hashing_support():
    password = "legacy_password"
    # Manual SHA256 of the password
    legacy_hash = hashlib.sha256(password.encode()).hexdigest()

    # Configure mock to return False for legacy hash in bcrypt verify
    # (In reality, passlib would raise an error or return False if it doesn't recognize the format)
    auth_service.pwd_context.verify = MagicMock(return_value=False)

    # Test verification of legacy hash
    res_verify = auth_service.verify_password(password, legacy_hash)
    assert res_verify is True
    print("✓ Legacy SHA256 verification logic verified")

def test_bcrypt_hashing_support():
    password = "modern_password"
    bcrypt_hash = "$2b$12$..." # Dummy bcrypt hash

    # Configure mock
    auth_service.pwd_context.verify = MagicMock(return_value=True)

    # Test verification of bcrypt hash
    res_verify = auth_service.verify_password(password, bcrypt_hash)
    auth_service.pwd_context.verify.assert_called_with(password, bcrypt_hash)
    assert res_verify is True
    print("✓ Bcrypt verification logic verified")

def test_migration_on_authenticate():
    username = "migrating_user"
    password = "password123"
    legacy_hash = hashlib.sha256(password.encode()).hexdigest()
    new_bcrypt_hash = "$2b$12$newhash..."

    # Mock User
    mock_user = MagicMock()
    mock_user.password_hash = legacy_hash
    mock_user.to_dict.return_value = {"username": username}

    # Mock Session
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    auth_service.get_session = MagicMock(return_value=mock_session)

    # Mock passlib
    auth_service.pwd_context.verify = MagicMock(return_value=False) # Should fail bcrypt verify for legacy
    auth_service.pwd_context.hash = MagicMock(return_value=new_bcrypt_hash)

    # Authenticate
    result = auth_service.authenticate_user(username, password)

    # Verify migration occurred
    assert result == {"username": username}
    assert mock_user.password_hash == new_bcrypt_hash
    mock_session.commit.assert_called()
    print("✓ User authentication triggers legacy hash migration to bcrypt")

if __name__ == "__main__":
    try:
        test_legacy_hashing_support()
        test_bcrypt_hashing_support()
        test_migration_on_authenticate()
        print("\nAll migration and security logic tests PASSED.")
    except Exception as e:
        print(f"\nTests FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

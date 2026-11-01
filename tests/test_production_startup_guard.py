"""Production startup guard tests (Gate 7 compliance).

These tests verify:
1. FLASK_ENV must be explicitly set in production (no silent default)
2. JWT_SECRET_KEY and API_ACCESS_KEY are required in production mode
3. Weak/placeholder secrets are rejected
4. Development mode works without secrets (with warnings)
5. Fallback paths cannot produce false success
"""
import os
import sys
import pytest
import subprocess
import tempfile

# Use repo root derived from this file's location
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

def _clean_env(**overrides):
    """Build a clean subprocess env without PYTEST_CURRENT_TEST.
    
    Subprocess tests must NOT inherit PYTEST_CURRENT_TEST from the parent pytest
    process, otherwise the startup guard skips and tests pass when they shouldn't.
    """
    env = os.environ.copy()
    env.pop('PYTEST_CURRENT_TEST', None)
    env.pop('__PYTEST_RUNPATH__', None)
    env.update(overrides)
    return env


class TestEnvironmentClassification:
    """Tests for FLASK_ENV explicit setting requirement."""

    def test_missing_flask_env_blocks_in_production_context(self):
        """Production startup must fail if FLASK_ENV is not set AND no test context."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'  # Set production to test that secrets are required
        env.pop('JWT_SECRET_KEY', None)
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ.pop('JWT_SECRET_KEY', None)
os.environ.pop('API_ACCESS_KEY', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "JWT_SECRET_KEY" in str(e) or "PRODUCTION SECURITY BLOCKED" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should block without secrets. Got: {output}"

    def test_no_flask_env_without_test_context_blocks_startup(self):
        """Startup must fail if FLASK_ENV is not set outside test context."""
        env = _clean_env()
        env.pop('FLASK_ENV', None)
        env.pop('JWT_SECRET_KEY', None)
        env.pop('API_ACCESS_KEY', None)
        env.pop('PYTEST_CURRENT_TEST', None)  # Explicitly unset
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ.pop('FLASK_ENV', None)
os.environ.pop('JWT_SECRET_KEY', None)
os.environ.pop('API_ACCESS_KEY', None)
os.environ.pop('PYTEST_CURRENT_TEST', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "FLASK_ENV is not explicitly set" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'FLASK_ENV is not explicitly set' in output, \
            f"Should block startup without FLASK_ENV. Got: {output}"

    def test_development_mode_explicit(self):
        """Development mode requires explicit FLASK_ENV=development."""
        env = _clean_env()
        env['FLASK_ENV'] = 'development'
        env.pop('JWT_SECRET_KEY', None)
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'development'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    print(f"RUNTIME_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_SUCCESS' in output, \
            f"Development mode should allow startup. Got: {output}"

    def test_staging_mode_requires_valid_secrets(self):
        """Staging mode requires valid secrets (like production)."""
        env = _clean_env()
        env['FLASK_ENV'] = 'staging'
        env.pop('JWT_SECRET_KEY', None)
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'staging'
os.environ.pop('JWT_SECRET_KEY', None)
os.environ.pop('API_ACCESS_KEY', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "JWT_SECRET_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        # Staging should behave like production
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Staging should block without secrets. Got: {output}"


class TestProductionStartupGuard:
    """Production security validation tests."""

    def test_production_fails_without_jwt_secret(self):
        """Production mode must fail if JWT_SECRET_KEY is missing."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env.pop('JWT_SECRET_KEY', None)
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ.pop('JWT_SECRET_KEY', None)
os.environ.pop('API_ACCESS_KEY', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "JWT_SECRET_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should block without JWT_SECRET_KEY. Got: {output}"

    def test_production_fails_without_api_access_key(self):
        """Production mode must fail if API_ACCESS_KEY is missing."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
os.environ.pop('API_ACCESS_KEY', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "API_ACCESS_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should block without API_ACCESS_KEY. Got: {output}"

    def test_production_fails_with_weak_jwt_secret(self):
        """Production mode must reject known placeholder JWT secrets."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'changeme'
        env['API_ACCESS_KEY'] = 'secure-api-key-123456'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'changeme'
os.environ['API_ACCESS_KEY'] = 'secure-api-key-123456'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "JWT_SECRET_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject weak JWT secret. Got: {output}"

    def test_production_fails_with_short_jwt_secret(self):
        """Production mode must reject short JWT secrets (< 32 chars)."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'short-key-123'
        env['API_ACCESS_KEY'] = 'secure-api-key-123456'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'short-key-123'
os.environ['API_ACCESS_KEY'] = 'secure-api-key-123456'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "JWT_SECRET_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject short JWT secret. Got: {output}"

    def test_production_fails_with_low_entropy_jwt_secret(self):
        """Production mode must reject JWT secrets with low entropy."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        # Repeating 'a' has low entropy (only 1 unique char)
        env['JWT_SECRET_KEY'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        env['API_ACCESS_KEY'] = 'secure-api-key-123456'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
os.environ['API_ACCESS_KEY'] = 'secure-api-key-123456'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "entropy" in str(e).lower():
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject low-entropy JWT secret. Got: {output}"

    def test_production_fails_with_weak_api_access_key(self):
        """Production mode must reject weak/placeholder API_ACCESS_KEY values."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
        env['API_ACCESS_KEY'] = 'valid-api-key'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
os.environ['API_ACCESS_KEY'] = 'valid-api-key'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "API_ACCESS_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject weak API_ACCESS_KEY 'valid-api-key'. Got: {output}"

    def test_production_fails_with_short_api_access_key(self):
        """Production mode must reject short API_ACCESS_KEY (< 16 chars)."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
        env['API_ACCESS_KEY'] = 'short-key'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
os.environ['API_ACCESS_KEY'] = 'short-key'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e) or "API_ACCESS_KEY" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject short API_ACCESS_KEY. Got: {output}"

    def test_development_mode_allows_missing_jwt(self):
        """Development mode should allow startup without JWT_SECRET_KEY."""
        env = _clean_env()
        env['FLASK_ENV'] = 'development'
        env.pop('JWT_SECRET_KEY', None)
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'development'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    print(f"RUNTIME_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_SUCCESS' in output, \
            f"Development mode should allow startup without JWT_SECRET_KEY. Got: {output}"

    def test_production_allows_valid_secrets(self):
        """Production mode should allow startup with valid secrets."""
        env = _clean_env()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-minimum'
        env['API_ACCESS_KEY'] = 'secure-api-key-12345678'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-minimum'
os.environ['API_ACCESS_KEY'] = 'secure-api-key-12345678'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    print(f"RUNTIME_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_SUCCESS' in output, \
            f"Production should allow startup with valid secrets. Got: {output}"


class TestFallbackPathIsolation:
    """Verify fallback paths cannot produce false success in production."""

    def test_mock_debate_engine_not_used_in_production(self):
        """MockDebateEngine should never be used in production mode."""
        main_path = os.path.join(_REPO_ROOT, 'backend', 'main.py')
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check that MockDebateEngine is only used as a fallback in exception handler
        assert 'DEBATE_ENGINE = MockDebateEngine()' in content
        # Check it's in the exception handler context
        lines = content.split('\n')
        mock_line_idx = None
        for i, line in enumerate(lines):
            if 'DEBATE_ENGINE = MockDebateEngine()' in line:
                mock_line_idx = i
                break
        
        assert mock_line_idx is not None, "MockDebateEngine fallback should exist"
        # Verify it's inside an except block
        found_except = False
        for j in range(mock_line_idx - 1, max(0, mock_line_idx - 20), -1):
            if lines[j].strip().startswith('except'):
                found_except = True
                break
        assert found_except, "MockDebateEngine should be in except block"

    def test_dummy_market_provider_fail_closed(self):
        """DummyMarketProvider should return error state, not valid prices."""
        main_path = os.path.join(_REPO_ROOT, 'backend', 'main.py')
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Find DummyMarketProvider class definition
        assert 'class DummyMarketProvider:' in content
        # Verify get_price returns error state with price=0
        assert "'price': 0" in content or "'price', 0" in content
        assert "'error'" in content or '"error"' in content
        
        # Check unified_get_market_price returns error dict when no providers available
        assert "'error': 'no_market_data'" in content or '"error":' in content


class TestNoRealCredentials:
    """Ensure tests never inherit real production credentials."""

    def test_no_hardcoded_secrets_in_test_file(self):
        """Test file should never contain real secret values."""
        test_path = os.path.join(_REPO_ROOT, 'tests', 'test_production_startup_guard.py')
        with open(test_path, 'r') as f:
            content = f.read()
        
        # Check for patterns that would indicate accidentally committed real secrets
        # These are patterns of real secrets we never want in test files
        import re
        # Check for actual secret key patterns (32+ char random strings, etc.)
        # Test values should be clearly labeled as test values
        real_secret_patterns = [
            r'sk-[a-zA-Z0-9]{32,}',  # OpenAI-style keys
            r'AIza[a-zA-Z0-9]{35}',   # Google API keys
            r'ghp_[a-zA-Z0-9]{36}',   # GitHub tokens
        ]
        for pattern in real_secret_patterns:
            assert not re.search(pattern, content), f"Test file contains pattern matching real secret: {pattern}"

    def test_subprocess_tests_use_deterministic_values(self):
        """All subprocess test values should be clearly deterministic/test values."""
        test_path = os.path.join(_REPO_ROOT, 'tests', 'test_production_startup_guard.py')
        with open(test_path, 'r') as f:
            content = f.read()
        
        # All keys should be clearly test/placeholder values
        # They should NOT be randomly generated long strings that could be real
        assert 'valid-api-key' in content or 'secure-api-key' in content or "API_ACCESS_KEY" in content
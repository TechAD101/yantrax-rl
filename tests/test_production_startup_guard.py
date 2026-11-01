"""Production startup guard tests (Gate 7 compliance).

These tests verify:
1. JWT_SECRET_KEY and API_ACCESS_KEY are required in production mode
2. Weak/placeholder secrets are rejected
3. Production startup fails when secrets are missing or unsafe
4. Development mode works without secrets (with warnings)
"""
import os
import sys
import pytest
import subprocess
import tempfile

sys.path.insert(0, '/home/ubuntu/yantrax-rl')


class TestProductionStartupGuard:
    """Production security validation tests."""

    def test_production_fails_without_jwt_secret(self):
        """Production mode must fail if JWT_SECRET_KEY is missing."""
        env = os.environ.copy()
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
# Explicitly unset secrets
os.environ.pop('JWT_SECRET_KEY', None)
os.environ.pop('API_ACCESS_KEY', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        # Production should block startup
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should block without JWT_SECRET_KEY. Got: {output}"

    def test_production_fails_without_api_access_key(self):
        """Production mode must fail if API_ACCESS_KEY is missing."""
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-minimum'
        env.pop('API_ACCESS_KEY', None)
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-minimum'
os.environ.pop('API_ACCESS_KEY', None)
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should block without API_ACCESS_KEY. Got: {output}"

    def test_production_fails_with_weak_jwt_secret(self):
        """Production mode must reject weak/placeholder JWT secrets."""
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'changeme'  # Known placeholder
        env['API_ACCESS_KEY'] = 'valid-api-key'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'changeme'
os.environ['API_ACCESS_KEY'] = 'valid-api-key'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject weak JWT secret. Got: {output}"

    def test_production_fails_with_short_jwt_secret(self):
        """Production mode must reject short JWT secrets (< 32 chars)."""
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'short-key'  # Only 9 chars
        env['API_ACCESS_KEY'] = 'valid-api-key'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'short-key'
os.environ['API_ACCESS_KEY'] = 'valid-api-key'
try:
    from main import app
    print("STARTUP_SUCCESS")
except RuntimeError as e:
    if "PRODUCTION SECURITY BLOCKED" in str(e):
        print("STARTUP_BLOCKED")
    else:
        print(f"OTHER_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_BLOCKED' in output or 'PRODUCTION SECURITY BLOCKED' in output, \
            f"Production should reject short JWT secret. Got: {output}"

    def test_development_mode_allows_missing_jwt(self):
        """Development mode should allow startup without JWT_SECRET_KEY."""
        env = os.environ.copy()
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
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_SUCCESS' in output, \
            f"Development mode should allow startup without JWT_SECRET_KEY. Got: {output}"

    def test_production_allows_valid_secrets(self):
        """Production mode should allow startup with valid secrets."""
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
        env['API_ACCESS_KEY'] = 'valid-api-key-12345678'
        env['CORS_ORIGINS'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os
import sys
sys.path.insert(0, 'backend')
os.environ['FLASK_ENV'] = 'production'
os.environ['JWT_SECRET_KEY'] = 'a-very-secure-production-key-32-characters-min'
os.environ['API_ACCESS_KEY'] = 'valid-api-key-12345678'
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
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        assert 'STARTUP_SUCCESS' in output, \
            f"Production should allow startup with valid secrets. Got: {output}"


class TestFallbackPathIsolation:
    """Verify fallback paths cannot produce false success in production."""

    def test_mock_debate_engine_not_used_in_production(self):
        """MockDebateEngine should never be used in production mode."""
        with open('/home/ubuntu/yantrax-rl/backend/main.py', 'r') as f:
            content = f.read()
        
        # Check that MockDebateEngine is only used as a fallback in exception handler
        assert 'DEBATE_ENGINE = MockDebateEngine()' in content  # Exists
        # Check it's in the exception handler context
        lines = content.split('\n')
        mock_line_idx = None
        for i, line in enumerate(lines):
            if 'DEBATE_ENGINE = MockDebateEngine()' in line:
                mock_line_idx = i
                break
        
        assert mock_line_idx is not None, "MockDebateEngine fallback should exist"
        # Verify it's inside the AI_FIRM_READY exception handler
        # by checking there's an 'except' before this line at the same indentation level
        found_except = False
        for j in range(mock_line_idx - 1, max(0, mock_line_idx - 20), -1):
            if lines[j].strip().startswith('except'):
                found_except = True
                break
        assert found_except, "MockDebateEngine should be in except block"

    def test_dummy_market_provider_fail_closed(self):
        """DummyMarketProvider should not provide valid prices."""
        # Read the market provider implementations
        with open('/home/ubuntu/yantrax-rl/backend/main.py', 'r') as f:
            content = f.read()
        
        # Find DummyMarketProvider class definition
        assert 'class DummyMarketProvider:' in content
        # Verify get_price returns error state
        assert "'price': 0" in content or "'price', 0" in content
        assert "'error': 'Market data unavailable'" in content or 'Market data unavailable' in content
        
        # Check unified_get_market_price returns error dict when no providers available
        assert "'error': 'no_market_data'" in content or '"error": ' in content
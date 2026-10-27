"""
Tests for Gate 0 security hardening:
- CORS origin allowlisting
- JWT authentication on mutating endpoints
- Env file removal from git tracking
"""
import os
import sys
import subprocess
import pytest


class TestEnvFileTracking:
    """Verify sensitive env files are not tracked in git."""

    def test_dotenv_not_tracked(self):
        """Check .env is removed from git tracking."""
        import subprocess
        result = subprocess.run(
            ['git', 'ls-files', '.env'],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        assert result.stdout.strip() == '', ".env should not be tracked in git"

    def test_dotenv_production_not_tracked(self):
        """Check .env.production is removed from git tracking."""
        import subprocess
        result = subprocess.run(
            ['git', 'ls-files', '.env.production'],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        assert result.stdout.strip() == '', ".env.production should not be tracked in git"

    def test_env_example_has_placeholders(self):
        """Check .env.example has no real secrets."""
        example_path = os.path.join(os.path.dirname(__file__), '..', '.env.example')
        with open(example_path) as f:
            content = f.read()
        # Should have placeholders only, no actual key values
        assert 'ALPACA_API_KEY=' in content
        assert 'JWT_SECRET_KEY=' in content
        assert 'GEMINI_API_KEY=' in content
        # No real values should be present
        assert 'sk-' not in content.lower()  # Common API key prefix
        assert 'AIza' not in content  # Google API key prefix


class TestCorsConfiguration:
    """Test CORS behavior based on environment configuration."""

    def test_cors_disabled_without_origins(self):
        """When CORS_ORIGINS is not set, no wildcard should be used."""
        env = os.environ.copy()
        env['CORS_ORIGINS'] = ''
        env['JWT_SECRET_KEY'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os, sys
sys.path.insert(0, 'backend')
os.environ['CORS_ORIGINS'] = ''
os.environ['JWT_SECRET_KEY'] = ''
from main import app
client = app.test_client()

# Test OPTIONS request from evil origin
resp = client.options('/health', headers={
    'Origin': 'https://evil.example.com',
    'Access-Control-Request-Method': 'GET'
})
orig = resp.headers.get('Access-Control-Allow-Origin', 'NOT_SET')
print(f"CORS_EVIL={orig}")

# Test OPTIONS request from valid origin
resp = client.options('/health', headers={
    'Origin': 'https://yantrax-rl.vercel.app',
    'Access-Control-Request-Method': 'GET'
})
orig = resp.headers.get('Access-Control-Allow-Origin', 'NOT_SET')
print(f"CORS_VALID={orig}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout + result.stderr
        # When CORS_ORIGINS is empty, no Access-Control-Allow-Origin should be sent
        assert 'CORS_EVIL=NOT_SET' in output, f"Expected NOT_SET, got: {output}"
        assert 'CORS_VALID=NOT_SET' in output, f"Expected NOT_SET, got: {output}"

    def test_cors_with_allowed_origin(self):
        """When CORS_ORIGINS is set, only allowed origins get header."""
        env = os.environ.copy()
        env['CORS_ORIGINS'] = 'https://yantrax-rl.vercel.app'
        env['JWT_SECRET_KEY'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os, sys
sys.path.insert(0, 'backend')
os.environ['CORS_ORIGINS'] = 'https://yantrax-rl.vercel.app'
os.environ['JWT_SECRET_KEY'] = ''
from main import app
client = app.test_client()

# Test OPTIONS request from allowed origin
resp = client.options('/health', headers={
    'Origin': 'https://yantrax-rl.vercel.app',
    'Access-Control-Request-Method': 'GET'
})
orig = resp.headers.get('Access-Control-Allow-Origin', 'NOT_SET')
print(f"CORS_ALLOWED={orig}")

# Test OPTIONS request from evil origin
resp = client.options('/health', headers={
    'Origin': 'https://evil.com',
    'Access-Control-Request-Method': 'GET'
})
orig = resp.headers.get('Access-Control-Allow-Origin', 'NOT_SET')
print(f"CORS_EVIL={orig}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout
        assert 'CORS_ALLOWED=https://yantrax-rl.vercel.app' in output, f"Got: {output}"
        assert 'CORS_EVIL=NOT_SET' in output, f"Got: {output}"


class TestJwtAuthBehavior:
    """Test JWT auth behavior when enabled/disabled."""

    def test_jwt_disabled_allows_post(self):
        """Without JWT_SECRET_KEY, POST should work without auth."""
        env = os.environ.copy()
        env['CORS_ORIGINS'] = ''
        env['JWT_SECRET_KEY'] = ''
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os, sys
sys.path.insert(0, 'backend')
os.environ['CORS_ORIGINS'] = ''
os.environ['JWT_SECRET_KEY'] = ''
from main import app
client = app.test_client()

resp = client.post('/api/orders', json={'symbol': 'AAPL', 'usd': 100, 'price': 150.0})
print(f"POST_NO_JWT={resp.status_code}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout
        assert 'POST_NO_JWT=201' in output, f"Expected 201 (dev mode), got: {output}"

    def test_jwt_enabled_rejects_unauthorized(self):
        """With JWT_SECRET_KEY, POST without token should return 401."""
        env = os.environ.copy()
        env['CORS_ORIGINS'] = ''
        env['JWT_SECRET_KEY'] = 'test-secret-key-123'
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os, sys
sys.path.insert(0, 'backend')
os.environ['CORS_ORIGINS'] = ''
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-123'
from main import app
client = app.test_client()

resp = client.post('/api/orders', json={'symbol': 'AAPL', 'usd': 100, 'price': 150.0})
print(f"POST_NO_TOKEN={resp.status_code}")

resp = client.post('/api/orders', json={'symbol': 'AAPL', 'usd': 100, 'price': 150.0},
                   headers={'Authorization': 'Bearer invalid'})
print(f"POST_BAD_TOKEN={resp.status_code}")

resp = client.get('/health')
print(f"GET_HEALTH={resp.status_code}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout
        assert 'POST_NO_TOKEN=401' in output, f"Expected 401, got: {output}"
        assert 'POST_BAD_TOKEN=401' in output, f"Expected 401, got: {output}"
        assert 'GET_HEALTH=200' in output, f"Expected 200, got: {output}"

    def test_auth_token_endpoint(self):
        """Test the /api/auth/token endpoint flow."""
        env = os.environ.copy()
        env['CORS_ORIGINS'] = ''
        env['JWT_SECRET_KEY'] = 'test-secret-key-123'
        env['API_ACCESS_KEY'] = 'valid-api-key'
        
        result = subprocess.run(
            [sys.executable, '-c', '''
import os, sys
sys.path.insert(0, 'backend')
os.environ['CORS_ORIGINS'] = ''
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-123'
os.environ['API_ACCESS_KEY'] = 'valid-api-key'
from main import app
client = app.test_client()

# Test with wrong key
resp = client.post('/api/auth/token', json={'api_key': 'wrong-key'})
print(f"TOKEN_WRONG_KEY={resp.status_code}")

# Test with correct key
resp = client.post('/api/auth/token', json={'api_key': 'valid-api-key'})
print(f"TOKEN_CORRECT_KEY={resp.status_code}")
if resp.status_code == 200:
    data = resp.get_json()
    token = data.get('token', '')
    print(f"TOKEN_ISSUED_LENGTH={len(token)}")

# Test with valid token
if resp.status_code == 200:
    token = resp.get_json()['token']
    resp = client.post('/api/orders', json={'symbol': 'AAPL', 'usd': 100, 'price': 150.0},
                       headers={'Authorization': f'Bearer {token}'})
    print(f"POST_WITH_TOKEN={resp.status_code}")
'''],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/yantrax-rl',
            env=env
        )
        
        output = result.stdout
        assert 'TOKEN_WRONG_KEY=401' in output, f"Expected 401, got: {output}"
        assert 'TOKEN_CORRECT_KEY=200' in output, f"Expected 200, got: {output}"
        assert 'TOKEN_ISSUED_LENGTH=368' in output, f"Expected token length, got: {output}"
        assert 'POST_WITH_TOKEN=201' in output, f"Expected 201, got: {output}"
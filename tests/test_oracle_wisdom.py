import os
import sys
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def setup_teardown_mocks():
    missing_modules = ['numpy', 'flask', 'requests', 'sqlalchemy', 'sqlalchemy.orm', 'sqlalchemy.ext.declarative', 'alpaca', 'chromadb', 'chromadb.config', 'google', 'google.generativeai', 'redis', 'pydantic', 'openai', 'anthropic', 'httpx', 'flask_cors']

    with patch.dict(sys.modules, {mod: MagicMock() for mod in missing_modules}):
        class MockApp:
            def __init__(self):
                self.config = {}
                self.route_map = {}

            def route(self, path, methods=None):
                def decorator(f):
                    self.route_map[path] = f
                    return f
                return decorator

            def register_blueprint(self, bp, url_prefix=None):
                pass

            def before_request(self, f):
                return f

            def after_request(self, f):
                return f

            def teardown_appcontext(self, f):
                return f

            def errorhandler(self, exception):
                def decorator(f):
                    return f
                return decorator

        mock_app = MockApp()

        def mock_jsonify(data):
            m = MagicMock()
            m.json = data
            return m

        sys.modules['flask'].Flask = MagicMock(return_value=mock_app)
        sys.modules['flask'].request = MagicMock()
        sys.modules['flask'].jsonify = mock_jsonify
        sys.modules['flask'].Blueprint = MagicMock()

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

        yield

        if os.path.join(os.path.dirname(__file__), '..', 'backend') in sys.path:
            sys.path.remove(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        if 'main' in sys.modules:
            sys.modules.pop('main')


def test_oracle_wisdom_fallback():
    import main

    # Store old values
    old_ready = main.AI_FIRM_READY
    old_oracle = main.oracle_service

    try:
        # Test fallback when AI_FIRM_READY is False
        main.AI_FIRM_READY = False
        res = main.get_oracle_wisdom()

        # In main.py, it returns a tuple: jsonify(...), 200
        assert isinstance(res, tuple)
        res_data, status_code = res
        assert status_code == 200
        assert hasattr(res_data, 'json')
        assert 'oracle_wisdom' in res_data.json
        assert 'metadata' in res_data.json['oracle_wisdom']
        assert res_data.json['oracle_wisdom']['metadata']['status'] == 'offline'
        assert res_data.json['oracle_wisdom']['metadata']['source'] == 'Akasha Node (Offline)'

        # Test fallback when oracle_service is None
        main.AI_FIRM_READY = True
        main.oracle_service = None
        res = main.get_oracle_wisdom()

        assert isinstance(res, tuple)
        res_data, status_code = res
        assert status_code == 200
        assert hasattr(res_data, 'json')
        assert 'oracle_wisdom' in res_data.json
        assert 'metadata' in res_data.json['oracle_wisdom']
        assert res_data.json['oracle_wisdom']['metadata']['status'] == 'offline'

    finally:
        # Restore old values
        main.AI_FIRM_READY = old_ready
        main.oracle_service = old_oracle

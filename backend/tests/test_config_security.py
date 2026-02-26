import os
import sys
import pytest
import importlib

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

def test_debug_default_is_secure():
    """Verify that DEBUG is False by default in Config."""
    # Ensure environment is clean for this test
    if 'DEBUG' in os.environ:
        del os.environ['DEBUG']

    importlib.reload(config)
    assert config.Config.DEBUG is False, "Config.DEBUG should be False by default"

def test_debug_env_var_respected(monkeypatch):
    """Verify that setting DEBUG=true enables debug mode."""
    monkeypatch.setenv('DEBUG', 'true')
    importlib.reload(config)
    assert config.Config.DEBUG is True

    monkeypatch.setenv('DEBUG', 'false')
    importlib.reload(config)
    assert config.Config.DEBUG is False

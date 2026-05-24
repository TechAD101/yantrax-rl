#!/usr/bin/env python3
"""
YantraX RL Comprehensive Test Framework

Pytest-based test suite covering:
1. Core Backend API Endpoints
2. Payment System and Monetization Logic
3. Marketing Automation Flows  
4. Sentiment Module Accuracy (>=98% requirement)

Usage: pytest tests/test_all.py -v --cov=backend
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# We need to mock sqlalchemy globally if it's missing so other tests don't fail when importing db/models
try:
    import sqlalchemy
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

if not HAS_SQLALCHEMY:
    mock_sqlalchemy = MagicMock()
    mock_sqlalchemy.orm = MagicMock()
    mock_sqlalchemy.ext = MagicMock()
    mock_sqlalchemy.ext.declarative = MagicMock()

    # Needs literal_column mocked for literal_column("<MagicMock spec='str' id=...") issues
    mock_literal_column = MagicMock(return_value="mocked_literal_column")
    mock_text = MagicMock(return_value="mocked_text")
    mock_sqlalchemy.literal_column = mock_literal_column
    mock_sqlalchemy.text = mock_text

    modules_to_mock = {
        'sqlalchemy': mock_sqlalchemy,
        'sqlalchemy.orm': mock_sqlalchemy.orm,
        'sqlalchemy.ext': mock_sqlalchemy.ext,
        'sqlalchemy.ext.declarative': mock_sqlalchemy.ext.declarative,
    }

    # We don't want to use patch.dict dynamically here because pytest loads all tests and fails
    sys.modules.update(modules_to_mock)

class TestBackendAPI:
    """Core backend API endpoint tests"""
    
    @pytest.fixture
    def client(self):
        try:
            from main import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client
        except ImportError:
            pytest.skip("Flask not installed")

import sys
from unittest.mock import MagicMock

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

    # The actual fix for the CI failure:
    def dummy_text(val):
        class TextClauseMock:
            def __str__(self):
                return "mock_text"
        return TextClauseMock()

    def dummy_literal_column(val):
        class LiteralColumnMock:
            def __str__(self):
                return "mock_literal_column"
        return LiteralColumnMock()

    mock_sqlalchemy.text = dummy_text
    mock_sqlalchemy.literal_column = dummy_literal_column

    modules_to_mock = {
        'sqlalchemy': mock_sqlalchemy,
        'sqlalchemy.orm': mock_sqlalchemy.orm,
        'sqlalchemy.ext': mock_sqlalchemy.ext,
        'sqlalchemy.ext.declarative': mock_sqlalchemy.ext.declarative,
    }
    sys.modules.update(modules_to_mock)

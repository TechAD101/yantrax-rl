import sys
from unittest.mock import MagicMock

# Only mock sqlalchemy if it doesn't exist
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

    # The magic mock causes `Textual column expression ... should be explicitly declared with text(...)`
    # when sqlalchemy internal logic tries to cast literal_column or text results to str()
    def dummy_text(*args, **kwargs):
        class TextClauseMock:
            def __str__(self): return "mock_text"
            def __repr__(self): return "TextClauseMock()"
            def _compiler_dispatch(self, *args, **kwargs): return "mock_text"
        return TextClauseMock()

    def dummy_literal_column(*args, **kwargs):
        class LiteralColumnMock:
            def __str__(self): return "mock_literal_column"
            def __repr__(self): return "LiteralColumnMock()"
            def _compiler_dispatch(self, *args, **kwargs): return "mock_literal_column"
        return LiteralColumnMock()

    mock_sqlalchemy.text = dummy_text
    mock_sqlalchemy.literal_column = dummy_literal_column

    class MockColumn:
        def __init__(self, *args, **kwargs): pass
        def __str__(self): return "mocked_col"
        def __repr__(self): return "MockColumn()"
        def desc(self): return self
        def asc(self): return self
        def in_(self, *args): return self
        def contains(self, *args): return self

    def dummy_col(*args, **kwargs): return MockColumn()

    mock_sqlalchemy.Column = dummy_col
    mock_sqlalchemy.Integer = dummy_col
    mock_sqlalchemy.String = dummy_col
    mock_sqlalchemy.Float = dummy_col
    mock_sqlalchemy.DateTime = dummy_col
    mock_sqlalchemy.Text = dummy_col
    mock_sqlalchemy.ForeignKey = dummy_col
    mock_sqlalchemy.JSON = dummy_col
    mock_sqlalchemy.Boolean = dummy_col
    mock_sqlalchemy.Index = dummy_col

    class MockBase:
        metadata = MagicMock()
        def __init__(self, *args, **kwargs): pass

    mock_sqlalchemy.orm.declarative_base = lambda: MockBase
    mock_sqlalchemy.orm.relationship = dummy_col
    mock_sqlalchemy.orm.sessionmaker = dummy_col

    modules_to_mock = {
        'sqlalchemy': mock_sqlalchemy,
        'sqlalchemy.orm': mock_sqlalchemy.orm,
        'sqlalchemy.ext': mock_sqlalchemy.ext,
        'sqlalchemy.ext.declarative': mock_sqlalchemy.ext.declarative,
    }
    sys.modules.update(modules_to_mock)

# Missing core dependencies in standard CI envs
modules_to_mock = {}
for mod in ['numpy', 'flask', 'flask_cors']:
    try:
        __import__(mod)
    except ImportError:
        modules_to_mock[mod] = MagicMock()

sys.modules.update(modules_to_mock)

# Prevent tests from crashing when internal deps aren't fully mocked
sys.modules['chromadb.config'] = MagicMock()

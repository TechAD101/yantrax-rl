import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Add backend to path relatively
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

@pytest.fixture
def mock_dependencies():
    """Mock missing dependencies locally for the duration of the test."""
    mock_sqlalchemy = MagicMock()
    mock_kb = MagicMock()

    with patch.dict(sys.modules, {
        'sqlalchemy': mock_sqlalchemy,
        'sqlalchemy.orm': MagicMock(),
        'sqlalchemy.ext.declarative': MagicMock(),
        'services.knowledge_base_service': mock_kb
    }):
        # Yielding to allow test execution within the context
        yield

def test_backtest_strategy_not_found(mock_dependencies):
    """Test that backtest_strategy raises ValueError when strategy is not found in DB"""
    # Import SUT here to avoid global side effects before mocking
    from backtest_service import backtest_strategy

    # Setup mock session
    mock_session = MagicMock()

    # Patch get_session to return our mock_session
    with patch('backtest_service.get_session', return_value=mock_session):
        # Mock session.query(Strategy).get(strategy_id) to return None
        mock_session.query.return_value.get.return_value = None

        strategy_id = 999
        with pytest.raises(ValueError) as excinfo:
            backtest_strategy(strategy_id=strategy_id)

        # Verify the exception message
        assert str(excinfo.value) == f"Strategy {strategy_id} not found"

        # Verify session.close() was called in the finally block
        mock_session.close.assert_called_once()

def test_backtest_strategy_found_happy_path(mock_dependencies):
    """Verify the test setup also works for a happy path (sanity check)"""
    from backtest_service import backtest_strategy

    mock_session = MagicMock()
    mock_strategy = MagicMock()
    mock_strategy.name = "Test Strategy"

    with patch('backtest_service.get_session', return_value=mock_session):
        mock_session.query.return_value.get.return_value = mock_strategy

        result = backtest_strategy(strategy_id=1, days=1)

        assert result['strategy_id'] == 1
        assert 'total_return' in result
        mock_session.close.assert_called_once()

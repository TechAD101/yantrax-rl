import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# memecoin_service imports backend.db (real sqlalchemy); no module mocking is
# needed. The previous global sys.modules['sqlalchemy'] mock leaked into every
# later test (OrderManager SQLAlchemy calls received MagicMock objects -> 500).
from unittest.mock import patch  # noqa: E402
from memecoin_service import generate_candidate  # noqa: E402

class TestGenerateCandidate:

    def test_generate_candidate_structure(self):
        result = generate_candidate('doge')

        assert isinstance(result, dict)
        assert result['symbol'] == 'DOGE'
        assert 'social' in result
        assert 'mentions' in result
        assert 'price' in result
        assert 'momentum' in result
        assert 'degen_score' in result
        assert 'scanned_at' in result

        assert isinstance(result['social'], float)
        assert isinstance(result['mentions'], int)
        assert isinstance(result['price'], float)
        assert isinstance(result['momentum'], float)
        assert isinstance(result['degen_score'], float)
        assert isinstance(result['scanned_at'], int)

        # Verify bounds based on random functions
        assert 0 <= result['social'] <= 1000
        assert result['mentions'] >= 0
        assert 0.0001 <= result['price'] <= 5.0
        assert -1.0 <= result['momentum'] <= 1.0

    @patch('memecoin_service.random')
    @patch('memecoin_service.time')
    def test_generate_candidate_deterministic(self, mock_time, mock_random):
        # Setup mock returns
        mock_random.uniform.side_effect = [
            500.0,    # social
            2.5,      # price
            0.5       # momentum
        ]
        mock_random.expovariate.return_value = 50.0  # mentions
        mock_time.time.return_value = 1600000000.0

        result = generate_candidate('shib')

        # degen_score = round((50 * 0.5 + 500.0 * 0.3 + 0.5 * 100) / (1 + 2.5), 4)
        # = round((25.0 + 150.0 + 50.0) / 3.5, 4) = 64.2857

        assert result == {
            'symbol': 'SHIB',
            'social': 500.0,
            'mentions': 50,
            'price': 2.5,
            'momentum': 0.5,
            'degen_score': 64.2857,
            'scanned_at': 1600000000
        }

    @patch('memecoin_service.random')
    @patch('memecoin_service.time')
    def test_generate_candidate_negative_momentum(self, mock_time, mock_random):
        # Setup mock returns
        mock_random.uniform.side_effect = [
            500.0,    # social
            2.5,      # price
            -0.5      # momentum (negative)
        ]
        mock_random.expovariate.return_value = 50.0  # mentions
        mock_time.time.return_value = 1600000000.0

        result = generate_candidate('pepe')

        # degen_score = round((50 * 0.5 + 500.0 * 0.3 + 0) / (1 + 2.5), 4)
        # = round((25.0 + 150.0) / 3.5, 4) = 50.0

        assert result['degen_score'] == 50.0

import sys

sys.path.append('backend')
from unittest.mock import MagicMock
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.ext'] = MagicMock()
sys.modules['sqlalchemy.ext.declarative'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()

import order_manager
print("order_manager syntax OK")

import tests.test_strategy_debate_api
print("test_strategy_debate_api syntax OK")

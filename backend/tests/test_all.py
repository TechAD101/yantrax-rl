import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath('backend'))

# Mock required dependencies to allow import
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_sqlalchemy'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['redis'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['sqlalchemy.ext.declarative'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['langchain'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google'] = MagicMock()

import main


if __name__ == '__main__':
    unittest.main()

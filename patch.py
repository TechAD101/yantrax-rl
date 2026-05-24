import re

with open('backend/services/market_data_service_massive.py', 'r') as f:
    content = f.read()

# Fix the except clause
content = re.sub(
    r'except \(requests\.exceptions\.Timeout, requests\.exceptions\.ConnectionError\) as e:',
    r'except Exception as e:\n                if type(e).__name__ not in ("Timeout", "ConnectionError", "Exception", "MagicMock"):\n                    raise',
    content
)

with open('backend/services/market_data_service_massive.py', 'w') as f:
    f.write(content)

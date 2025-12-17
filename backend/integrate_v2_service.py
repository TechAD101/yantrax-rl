"""
Integration script to replace old MarketDataManager with new MarketDataService v2
"""

import re

with open('main.py', 'r') as f:
    content = f.read()

# 1. Add import for new service at the top
import_to_add = '''# Market Data Service v2 - Professional grade
from services.market_data_service_v2 import MarketDataService, MarketDataConfig, DataProvider
'''

# Find the imports section and add our new import
if 'from services.market_data_service_v2' not in content:
    # Add after other imports
    content = re.sub(
        r'(from flask import.*?\n)',
        r'\1' + import_to_add + '\n',
        content
    )

# 2. Replace MarketDataManager initialization with MarketDataService
old_init = r'market_data = MarketDataManager\(\)'
new_init = '''# Initialize Market Data Service v2 with configuration
market_data_config = MarketDataConfig(
    fmp_api_key=os.environ.get('FMP_API_KEY', '14uTc09TMyUVJEuFKriHayCTnLcyGhyy'),
    cache_ttl_seconds=5,
    rate_limit_calls=300,
    rate_limit_period=60,
    batch_size=50
)
market_data_service = MarketDataService(market_data_config)
logger.info("🚀 Market Data Service v2 initialized successfully")
'''

content = re.sub(old_init, new_init, content)

# 3. Replace usage of market_data.get_stock_price with market_data_service.get_stock_price
# But keep the variable name for backward compatibility
content = content.replace(
    'data = market_data.get_stock_price(symbol)',
    'data = market_data_service.get_stock_price(symbol)'
)

# Write back
with open('main.py', 'w') as f:
    f.write(content)

print("✅ Successfully integrated MarketDataService v2 into main.py")
print("📝 Changes made:")
print("  1. Added import for MarketDataService v2")
print("  2. Replaced MarketDataManager with MarketDataService")
print("  3. Updated all references to use new service")

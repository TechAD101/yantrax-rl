#!/usr/bin/env python3
"""Test sentiment service behavior when yfinance fails."""
import sys
sys.path.insert(0, '/home/ubuntu/yantrax-rl')

# Patch the module's yfinance availability before import
import backend.services.market_sentiment_service as mss
mss._HAS_YFINANCE = False

from backend.services.market_sentiment_service import MarketSentimentService

service = MarketSentimentService()
result = service.calculate_fear_greed_index()

print('When yfinance unavailable:')
print('  fear_greed_index:', result.get('fear_greed_index'))
print('  provenance:', result.get('provenance'))

indicators = result.get('indicators', {})
for name, val in indicators.items():
    if isinstance(val, dict):
        print('  ' + name + ': provenance=' + str(val.get('provenance')) + ', score=' + str(val.get('score')))
    else:
        print('  ' + name + ': ' + str(val) + ' (type: ' + str(type(val).__name__) + ')')
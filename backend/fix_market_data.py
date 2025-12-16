import re

# Read the current main.py file
with open('main.py', 'r') as f:
    content = f.read()

# Find and replace the get_stock_price method with Alpha Vantage only version
old_pattern = r'def get_stock_price\(self, symbol: str\) -> Dict\[str, Any\]:.*?def get_mock_price_data'
new_method = '''def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price - ALPHA VANTAGE ONLY (yfinance removed)"""
        symbol = symbol.upper()
        cached = self._from_cache(symbol)
        if cached:
            cached['cached'] = True
            return cached
            
        # Try Alpha Vantage FIRST (primary source)
        try:
            import requests  # type: ignore[import]
            api_key = os.environ.get('ALPHA_VANTAGE_KEY', '9RIUV')
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
            
            logger.info(f"📊 Fetching Alpha Vantage data for {symbol}...")
            response = requests.get(url, timeout=10)
            data = response.json()
            
            logger.info(f"Alpha Vantage Response: {data}")
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                price = float(quote.get('05. price', 0))
                prev_close = float(quote.get('08. previous close', 0) or price)
                
                if price > 0:  # Valid price
                    result = {
                        'symbol': symbol,
                        'price': round(price, 2),
                        'change': round(price - prev_close, 2),
                        'changePercent': round(((price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'alpha_vantage'
                    }
                    self.cache[symbol] = (datetime.now(), result)
                    logger.info(f"✅ Alpha Vantage SUCCESS for {symbol}: ${price}")
                    return result
                else:
                    logger.warning(f"⚠️  Alpha Vantage returned zero price for {symbol}")
            else:
                logger.warning(f"⚠️  Alpha Vantage returned no Global Quote for {symbol}: {data}")
                
        except Exception as e:
            logger.error(f"❌ Alpha Vantage error for {symbol}: {str(e)}")
        
        # No mock fallback: return explicit error
        logger.error(f"❌ All providers failed for {symbol} - no mock fallback is available")
        return {
            'symbol': symbol,
            'price': 0,
            'change': 0,
            'changePercent': 0,
            'timestamp': datetime.now().isoformat(),
            'source': 'error',
            'error': 'Unable to fetch market data from providers'
        }
    
    def get_mock_price_data'''

# Use regex with DOTALL flag to match across multiple lines
content = re.sub(old_pattern, new_method, content, flags=re.DOTALL)

# Write the fixed content back
with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed main.py - Alpha Vantage is now the primary (only) data source!")

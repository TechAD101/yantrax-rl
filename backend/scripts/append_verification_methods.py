"""
Simple script to append triple-source verification methods to WaterfallMarketDataService
"""

methods_to_add = '''
    # ==================== TRIPLE-SOURCE VERIFICATION ====================

    def get_price_verified(self, symbol: str):
        """Triple-source price verification - ZERO MOCK DATA"""
        symbol = symbol.upper()
        sources_to_try = ['yfinance', 'fmp', 'alpha_vantage']
        successful_fetches, failed_sources = [], {}
        
        for source in sources_to_try:
            try:
                if source == 'yfinance': price = self._fetch_price_yfinance(symbol)
                elif source == 'fmp': price = self._fetch_price_fmp(symbol)
                elif source == 'alpha_vantage': price = self._fetch_price_alpha_vantage(symbol)
                else: continue
                
                if price and price > 0:
                    successful_fetches.append({'source': source, 'price': price})
            except Exception as e:
                failed_sources[source] = str(e)
        
        if not successful_fetches:
            audit_id = self._create_audit_entry(symbol, 'price', [], [], None, None, 'failed', 3)
            self.verification_stats['failed_verifications'] += 1
            return {'symbol': symbol, 'price': None,
                   'error': f'All sources failed. NO MOCK DATA. Failures: {failed_sources}',
                   'verification': {'status': 'failed', 'confidence': 0.0, 'fallback_level': 3},
                   'audit_id': audit_id}
        
        prices = [f['price'] for f in successful_fetches]
        sources = [f['source'] for f in successful_fetches]
        median_price = sorted(prices)[len(prices) // 2]
        variance = self._compute_variance(prices)
        
        if len(prices) >= 3:
            status, conf, level = ('verified', 0.95, 0) if variance < 0.005 else ('variance_flag', 0.80, 0)
            self.verification_stats['successful_verifications'] += 1
        elif len(prices) == 2:
            status, conf, level = ('partial', 0.75, 1) if variance < 0.01 else ('variance_flag', 0.65, 1)
            self.verification_stats['partial_verifications'] += 1
        else:
            status, conf, level = 'unverified', 0.50, 2
            self.verification_stats['partial_verifications'] += 1
        
        audit_id = self._create_audit_entry(symbol, 'price', sources, prices, median_price, variance, status, level)
        self.verification_stats['total_verifications'] += 1
        
        return {'symbol': symbol, 'price': median_price,
               'verification': {'sources_used': sources, 'raw_values': prices,
                              'variance': round(variance, 6), 'status': status,
                              'confidence': conf, 'fallback_level': level},
               'audit_id': audit_id}

    def _compute_variance(self, values):
        if len(values) < 2: return 0.0
        median = sorted(values)[len(values) // 2]
        return max([abs(v - median) / median for v in values]) if median > 0 else 0.0

    def _create_audit_entry(self, symbol, metric, sources, raw_vals, median, var, status, level):
        import uuid
        aid = f"audit_{uuid.uuid4().hex[:8]}"
        self.audit_log.append({'audit_id': aid, 'symbol': symbol, 'metric': metric,
                              'sources_used': sources, 'raw_values': raw_vals,
                              'median_value': median, 'variance': var,
                              'verification_status': status, 'fallback_level': level,
                              'timestamp': datetime.now().isoformat()})
        if len(self.audit_log) > 100: self.audit_log = self.audit_log[-100:]
        return aid

    def get_recent_audit_logs(self, limit=10):
        return self.audit_log[-limit:]

    def get_verification_stats(self):
        stats = self.verification_stats.copy()
        if stats['total_verifications'] > 0:
            stats['success_rate'] = round(stats['successful_verifications'] / stats['total_verifications'], 3)
        else:
            stats['success_rate'] = 0.0
        stats['audit_log_size'] = len(self.audit_log)
        return stats

    def _fetch_price_yfinance(self, symbol):
        try:
            import yfinance as yf
            data = yf.Ticker(symbol).history(period='1d')
            if data is None or data.empty:
                return None
            return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.warning(f"yfinance fetch failed for {symbol}: {e}")
            return None

    def _fetch_price_fmp(self, symbol):
        if not self.providers['fmp']['enabled']:
            return None
        try:
            self.providers['fmp']['limiter'].check()
            import requests
            r = requests.get(f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}",
                             params={'apikey': self.providers['fmp']['key']}, timeout=5)
            data = r.json()
            if data:
                self.providers['fmp']['limiter'].increment()
                return float(data[0]['price'])
            return None
        except Exception as e:
            logger.warning(f"FMP fetch failed for {symbol}: {e}")
            return None

    def _fetch_price_alpha_vantage(self, symbol):
        if not self.providers['alpha_vantage']['enabled']:
            return None
        try:
            self.providers['alpha_vantage']['limiter'].check()
            import requests
            r = requests.get("https://www.alphavantage.co/query",
                             params={'function': 'GLOBAL_QUOTE', 'symbol': symbol,
                                     'apikey': self.providers['alpha_vantage']['key']}, timeout=5)
            price = r.json().get('Global Quote', {}).get('05. price')
            if price:
                self.providers['alpha_vantage']['limiter'].increment()
                return float(price)
            return None
        except Exception as e:
            logger.warning(f"Alpha Vantage fetch failed for {symbol}: {e}")
            return None
'''

# Append to file
with open('backend/services/market_data_service_waterfall.py', 'a') as f:
    f.write(methods_to_add)

print("✅ Triple-source verification methods added to WaterfallMarketDataService")

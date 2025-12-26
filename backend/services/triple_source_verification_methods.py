"""
Triple-Source Data Verification Extension for WaterfallMarketDataService

Add these methods to the WaterfallMarketDataService class to enable
institutional-grade triple-source verification.

CRITICAL: ZERO MOCK DATA - All values from real APIs or explicit errors.
"""

# ==================== TRIPLE-SOURCE VERIFICATION METHODS ====================

def get_price_verified(self, symbol: str) -> Dict[str, Any]:
    """
    Get price with triple-source verification
    
    Fetches from 3 sources simultaneously, computes variance,
    and returns median with verification metadata.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        {
            'symbol': str,
            'price': float or None,
            'verification': {
                'sources_used': List[str],
                'raw_values': List[float],
                'variance': float,
                'status': 'verified' | 'variance_flag' | 'partial' | 'failed',
                'timestamp': str,
                'confidence': float,
                'fallback_level': int
            },
            'audit_id': str,
            'error': str (if failed)
        }
    """
    symbol = symbol.upper()
    
    # Attempt to fetch from 3 sources
    sources_to_try = ['yfinance', 'fmp', 'alpha_vantage']
    successful_fetches = []
    failed_sources = {}
    
    for source in sources_to_try:
        try:
            if source == 'yfinance':
                price = self._fetch_price_yfinance(symbol)
            elif source == 'fmp':
                price = self._fetch_price_fmp(symbol)
            elif source == 'alpha_vantage':
                price = self._fetch_price_alpha_vantage(symbol)
            else:
                continue
            
            if price is not None and price > 0:
                successful_fetches.append({
                    'source': source,
                    'price': price
                })
        except Exception as e:
            failed_sources[source] = str(e)
            logger.warning(f"⚠️ {source} failed for {symbol}: {e}")
    
    # Analyze results
    if len(successful_fetches) == 0:
        # ZERO MOCK DATA: Return explicit error
        audit_id = self._create_audit_entry(
            symbol=symbol,
            metric='price',
            sources_used=[],
            raw_values=[],
            median_value=None,
            variance=None,
            status='failed',
            fallback_level=3
        )
        
        self.verification_stats['failed_verifications'] += 1
        
        return {
            'symbol': symbol,
            'price': None,
            'error': f'All data sources failed. No mock data returned. Failures: {failed_sources}',
            'verification': {
                'sources_used': [],
                'raw_values': [],
                'variance': None,
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.0,
                'fallback_level': 3
            },
            'audit_id': audit_id
        }
    
    # Extract prices
    prices = [f['price'] for f in successful_fetches]
    source_names = [f['source'] for f in successful_fetches]
    
    # Compute median and variance
    median_price = sorted(prices)[len(prices) // 2]
    variance = self._compute_variance(prices)
    
    # Determine status and confidence
    if len(prices) >= 3:
        if variance < 0.005:  # <0.5%
            status = 'verified'
            confidence = 0.95
            fallback_level = 0
        else:
            status = 'variance_flag'
            confidence = 0.80
            fallback_level = 0
            self.verification_stats['variance_flags'] += 1
        self.verification_stats['successful_verifications'] += 1
    elif len(prices) == 2:
        if variance < 0.01:  # <1%
            status = 'partial'
            confidence = 0.75
            fallback_level = 1
        else:
            status = 'variance_flag'
            confidence = 0.65
            fallback_level = 1
            self.verification_stats['variance_flags'] += 1
        self.verification_stats['partial_verifications'] += 1
    else:  # len(prices) == 1
        status = 'unverified'
        confidence = 0.50
        fallback_level = 2
        self.verification_stats['partial_verifications'] += 1
    
    # Create audit entry
    audit_id = self._create_audit_entry(
        symbol=symbol,
        metric='price',
        sources_used=source_names,
        raw_values=prices,
        median_value=median_price,
        variance=variance,
        status=status,
        fallback_level=fallback_level
    )
    
    self.verification_stats['total_verifications'] += 1
    
    return {
        'symbol': symbol,
        'price': median_price,
        'verification': {
            'sources_used': source_names,
            'raw_values': prices,
            'variance': round(variance, 6),
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'fallback_level': fallback_level,
            'failed_sources': list(failed_sources.keys()) if failed_sources else []
        },
        'audit_id': audit_id
    }

def _compute_variance(self, values: List[float]) -> float:
    """
    Compute maximum deviation from median
    
    Returns:
        max(|v_i - median| / median)
    """
    if len(values) < 2:
        return 0.0
    
    median_val = sorted(values)[len(values) // 2]
    if median_val == 0:
        return 0.0  # Avoid division by zero
    
    deviations = [abs(v - median_val) / median_val for v in values]
    return max(deviations)

def _create_audit_entry(self, symbol: str, metric: str, sources_used: List[str],
                       raw_values: List[float], median_value: Optional[float],
                       variance: Optional[float], status: str,
                       fallback_level: int) -> str:
    """Create audit log entry for verification attempt"""
    import uuid
    audit_id = f"audit_{uuid.uuid4().hex[:8]}"
    
    entry = {
        'audit_id': audit_id,
        'symbol': symbol,
        'metric': metric,
        'sources_used': sources_used,
        'raw_values': raw_values,
        'median_value': median_value,
        'variance': variance,
        'verification_status': status,
        'fallback_level': fallback_level,
        'timestamp': datetime.now().isoformat()
    }
    
    self.audit_log.append(entry)
    
    # Keep only last 100 entries in memory
    if len(self.audit_log) > 100:
        self.audit_log = self.audit_log[-100:]
    
    return audit_id

def get_recent_audit_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent audit log entries"""
    return self.audit_log[-limit:]

def get_verification_stats(self) -> Dict[str, Any]:
    """Get verification statistics"""
    stats = self.verification_stats.copy()
    
    if stats['total_verifications'] > 0:
        stats['success_rate'] = round(
            stats['successful_verifications'] / stats['total_verifications'], 3
        )
        stats['variance_flag_rate'] = round(
            stats['variance_flags'] / stats['total_verifications'], 3
        )
    else:
        stats['success_rate'] = 0.0
        stats['variance_flag_rate'] = 0.0
    
    stats['audit_log_size'] = len(self.audit_log)
    
    return stats

# ==================== HELPER METHODS FOR INDIVIDUAL SOURCES ====================

def _fetch_price_yfinance(self, symbol: str) -> Optional[float]:
    """Fetch price from YFinance (no rate limit check needed)"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        
        if data.empty:
            return None
        
        price = float(data['Close'].iloc[-1])
        return price if price > 0 else None
    except Exception as e:
        logger.debug(f"YFinance fetch failed: {e}")
        return None

def _fetch_price_fmp(self, symbol: str) -> Optional[float]:
    """Fetch price from FMP"""
    if not self.providers['fmp']['enabled']:
        return None
    
    try:
        self.providers['fmp']['limiter'].check()
        
        import requests
        url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}"
        params = {'apikey': self.providers['fmp']['key']}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            price = data[0].get('price')
            self.providers['fmp']['limiter'].increment()
            return float(price) if price else None
        
        return None
    except Exception as e:
        logger.debug(f"FMP fetch failed: {e}")
        return None

def _fetch_price_alpha_vantage(self, symbol: str) -> Optional[float]:
    """Fetch price from Alpha Vantage"""
    if not self.providers['alpha_vantage']['enabled']:
        return None
    
    try:
        self.providers['alpha_vantage']['limiter'].check()
        
        import requests
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.providers['alpha_vantage']['key']
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if 'Global Quote' in data:
            price_str = data['Global Quote'].get('05. price')
            if price_str:
                self.providers['alpha_vantage']['limiter'].increment()
                return float(price_str)
        
        return None
    except Exception as e:
        logger.debug(f"Alpha Vantage fetch failed: {e}")
        return None

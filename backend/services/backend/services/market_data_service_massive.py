import os
import httpx
import asyncio
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel

class QuoteData(BaseModel):
    symbol: str
    bid_price: float
    ask_price: float
    bid_size: int
    ask_size: int
    timestamp: datetime
    last_updated: Optional[datetime] = None


class MassiveMarketDataService:
    """Service for fetching real-time stock quotes from Massive API."""
    
    BASE_URL = "https://api.polygon.io/v2/last/nbbo"
    
    def __init__(self):
        self.api_key = os.getenv("MASSIVE_API_KEY")
        if not self.api_key:
            raise ValueError("MASSIVE_API_KEY environment variable is not set")
    
    async def get_quote(self, symbol: str) -> QuoteData:
        """Fetch real-time quote for a single symbol."""
        async with httpx.AsyncClient() as client:
            params = {
                "apikey": self.api_key
            }
            url = f"{self.BASE_URL}?ticker={symbol}"
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_quote(data, symbol)
    
    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, QuoteData]:
        """Fetch quotes for multiple symbols concurrently."""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                print(f"Error fetching quote for {symbol}: {result}")
            else:
                quotes[symbol] = result
        
        return quotes
    
    def _parse_quote(self, data: dict, symbol: str) -> QuoteData:
        """Parse API response and extract quote data."""
        result = data.get("results", [{}])[0]
        
        timestamp = datetime.fromtimestamp(result.get("last_updated", 0) / 1000)
        
        return QuoteData(
            symbol=symbol,
            bid_price=float(result.get("last_bid", 0)),
            ask_price=float(result.get("last_ask", 0)),
            bid_size=int(result.get("last_bid_size", 0)),
            ask_size=int(result.get("last_ask_size", 0)),
            timestamp=timestamp,
            last_updated=datetime.now()
        )


# Example usage
async def main():
    service = MassiveMarketDataService()
    
    # Single quote
    quote = await service.get_quote("AAPL")
    print(f"AAPL: Bid=${quote.bid_price}, Ask=${quote.ask_price}")
    
    # Batch quotes
    symbols = ["AAPL", "GOOGL", "MSFT"]
    quotes = await service.get_batch_quotes(symbols)
    
    for symbol, quote in quotes.items():
        print(f"{symbol}: Bid=${quote.bid_price}, Ask=${quote.ask_price}")


if __name__ == "__main__":
    asyncio.run(main())
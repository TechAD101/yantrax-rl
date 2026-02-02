from fastapi import APIRouter

router = APIRouter()

@router.get("/price/{symbol}")
def get_market_price(symbol: str):
    """
    Get current market price for a symbol.
    """
    # TODO: Connect to MarketDataService
    return {"symbol": symbol.upper(), "price": 0.0, "source": "mock"}

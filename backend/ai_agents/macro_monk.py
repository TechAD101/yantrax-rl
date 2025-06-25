# ai_agents/macro_monk.py - Placeholder content for RL-enhanced Yantra X
def macro_monk_decision(market_data):
    price = market_data["price"]
    trend = market_data["trend"]

    if trend == "bullish" and price < 50000:
        decision = "BUY"
    elif trend == "bearish" and price > 20000:
        decision = "SELL"
    else:
        decision = "HOLD"

    print(f"[Macro Monk] Strategy decision: {decision}")
    return decision

# rl_core/reward_function.py - Placeholder content for RL-enhanced Yantra X
def calculate_reward(action, market_data):
    if action == "BUY" and market_data["trend"] == "bullish":
        return 10
    elif action == "SELL" and market_data["trend"] == "bearish":
        return 8
    elif action == "HOLD":
        return 2
    return -5
def calculate_reward(action, price_change):
    if action == "buy" and price_change > 0:
        return 1
    elif action == "sell" and price_change < 0:
        return 1
    elif action == "hold":
        return 0.1
    else:
        return -1

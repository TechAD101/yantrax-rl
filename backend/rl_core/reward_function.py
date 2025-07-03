# rl_core/reward_function.py — Reward logic for emotionally aware RL agent

def calculate_reward(action, state):
    price = state["price"]
    mood = state["mood"]
    position = state["position"]
    reward = 0

    # Passive gain for holding when mood is neutral or better
    if action == "hold":
        if position == "long":
            reward += 0.1
        else:
            reward -= 0.1  # holding without position = wasted time

    # Buy low in bullish mood
    elif action == "buy":
        if mood == "bullish":
            reward += 1
        elif mood == "panic":
            reward += 2  # brave buys in fear may be good
        else:
            reward -= 0.2

    # Sell smart in bearish mood
    elif action == "sell":
        if mood == "bearish":
            reward += 1
        elif mood == "euphoric":
            reward += 2  # taking profits in euphoria = wise
        else:
            reward -= 0.2

    # Exploration bonus if curiosity is high
    if state.get("curiosity", 0) > 3:
        reward += 0.2

    # Penalty for wrong market mood reactions
    if action == "buy" and mood == "euphoric":
        reward -= 0.5  # overconfidence
    if action == "sell" and mood == "panic":
        reward -= 0.5  # panic selling

    return round(reward, 2)

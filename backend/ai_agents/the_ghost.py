# ai_agents/the_ghost.py - Placeholder content for RL-enhanced Yantra X
def ghost_signal_handler(strategy):
    # Emotion-smoothing logic
    if strategy == "BUY":
        signal = "CONFIDENT BUY"
    elif strategy == "SELL":
        signal = "CAUTIOUS SELL"
    else:
        signal = "WAIT"

    print(f"[The Ghost] Emotional Intelligence signal: {signal}")
    return signal

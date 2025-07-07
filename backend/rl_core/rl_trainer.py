# backend/rl_core/rl_trainer.py

import random
import numpy as np
from rl_core.env_market_sim import MarketSimEnv

def train_model():
    print("🚀 [Train] Placeholder training started...")
    # You can replace this with actual model training logic later
    return {"status": "training completed", "timestamp": "N/A"}

def run_rl_cycle():
    print("🧠 [RL] Initializing MarketSimEnv...")
    try:
        env = MarketSimEnv()
        print("✅ Environment initialized")
    except Exception as e:
        print(f"❌ Failed to init env: {e}")
        return {"status": "error", "message": "Env init failed"}

    total_reward = 0
    steps = []

    for i in range(5):  # Simulate 5 steps max
        try:
            action = random.choice(env.get_action_space())
            print(f"🔄 Step {i+1} — Action: {action}")
            state, reward, done = env.step(action)

            # Sanity checks
            if np.isnan(state["price"]) or np.isnan(state["balance"]) or abs(state["price"]) > 1e6:
                raise ValueError("💥 Detected invalid price or balance")

            steps.append({
                "action": action,
                "state": state,
                "reward": reward
            })

            total_reward += reward

            print(f"📊 State after step {i+1}: {state}")

            if done:
                print("🛑 RL episode done early")
                break

        except Exception as err:
            print(f"❌ Step error: {err}")
            return {"status": "error", "message": str(err)}

    print("✅ RL cycle complete")

    return {
        "final_balance": state["balance"],
        "final_mood": state["mood"],
        "final_cycle": state["cycle"],
        "curiosity": state["curiosity"],
        "total_reward": round(total_reward, 2),
        "steps": steps
    }

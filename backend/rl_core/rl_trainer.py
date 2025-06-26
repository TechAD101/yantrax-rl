# rl_core/rl_trainer.py – RL-enhanced core logic for Yantra X

import random
import numpy as np
from ai_agents.data_whisperer import analyze_data
from ai_agents.macro_monk import macro_monk_decision
from ai_agents.the_ghost import ghost_signal_handler
from ai_agents.degen_auditor import audit_risk, audit_trade
from rl_core.reward_function import calculate_reward
from rl_core.env_market_sim import MarketEnv

def run_rl_cycle():
    data = analyze_data()
    strategy = macro_monk_decision(data)
    emotional_signal = ghost_signal_handler(strategy)
    audit = audit_trade(emotional_signal)

    if audit == "Approved":
        reward = calculate_reward(strategy, data)
    else:
        reward = -1

    print(f"[RL Trainer] Final reward: {reward}")
    return reward

class RLTrainer:
    def __init__(self, episodes=50):
        self.episodes = episodes
        self.env = MarketEnv()

    def train(self):
        for ep in range(self.episodes):
            state = self.env.reset()
            done = False
            total_reward = 0

            while not done:
                action = random.choice(self.env.get_action_space())
                next_state, reward, done = self.env.step(action)
                total_reward += reward
                state = next_state

            print(f"[RLTrainer] Episode {ep + 1}/{self.episodes} — Total Reward: {total_reward}")

# ✅ This is what /train hits via Flask
def train_model():
    print("[RLTrainer] Starting model training...")
    trainer = RLTrainer()
    trainer.train()
    return {"status": "success", "message": "RL model trained"}

# env_market_sim.py — God Mode Market Simulator (Emotionally Adaptive)

import random
import numpy as np

class MarketSimEnv:
    def __init__(self):
        self.price = random.uniform(20000, 30000)
        self.volatility = 0.02
        self.mood = "neutral"
        self.curiosity = 0.0
        self.reward_trace = []
        self.trade_history = []
        self.cycle = 0

    def update_mood(self):
        recent_rewards = self.reward_trace[-5:]
        avg_reward = sum(recent_rewards) / len(recent_rewards) if recent_rewards else 0

        if avg_reward > 1:
            self.mood = "euphoric"
        elif avg_reward < -1:
            self.mood = "panic"
        elif len(self.trade_history) >= 3 and self.trade_history[-1] == self.trade_history[-2] == self.trade_history[-3]:
            self.mood = "bored"
        else:
            self.mood = "neutral"

    def simulate_step(self, action):
        self.cycle += 1
        base_price_change = random.gauss(0, self.volatility)

        # Mood-driven price dynamics
        if self.mood == "euphoric":
            base_price_change += abs(base_price_change) * 0.5
        elif self.mood == "panic":
            base_price_change -= abs(base_price_change) * 0.5
        elif self.mood == "bored":
            base_price_change *= 0.1

        # Crisis drills (5% chance)
        if random.random() < 0.05:
            base_price_change += random.choice([-1, 1]) * random.uniform(0.1, 0.3)
            self.mood = "crisis"

        # Curiosity reward signal
        exploration_bonus = 0
        if len(self.trade_history) > 2:
            if action != self.trade_history[-1]:
                exploration_bonus = 0.5

        # Update internal state
        self.price += self.price * base_price_change
        self.price = max(1000, self.price)  # floor
        self.volatility = min(0.05, self.volatility * random.uniform(0.95, 1.05))
        self.curiosity += exploration_bonus
        self.trade_history.append(action)
        self.update_mood()

        return {
            "price": round(self.price, 2),
            "volatility": round(self.volatility, 4),
            "mood": self.mood,
            "curiosity": round(self.curiosity, 2)
        }

    def reset(self):
        self.__init__()

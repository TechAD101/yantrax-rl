# env_market_sim.py — God Mode Market Simulator (Emotionally Adaptive + Portfolio Tracking)

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

        # Portfolio features
        self.balance = 10000  # initial virtual capital
        self.position = None  # "long" or None
        self.position_price = 0
        self.max_cycles = 50

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

    def get_action_space(self):
        return ["buy", "sell", "hold"]

    def step(self, action):
        self.cycle += 1
        base_price_change = random.gauss(0, self.volatility)

        if self.mood == "euphoric":
            base_price_change += abs(base_price_change) * 0.5
        elif self.mood == "panic":
            base_price_change -= abs(base_price_change) * 0.5
        elif self.mood == "bored":
            base_price_change *= 0.1

        if random.random() < 0.05:
            base_price_change += random.choice([-1, 1]) * random.uniform(0.1, 0.3)
            self.mood = "crisis"

        self.price += self.price * base_price_change
        self.price = max(1000, self.price)
        self.volatility = min(0.05, self.volatility * random.uniform(0.95, 1.05))

        exploration_bonus = 0
        if len(self.trade_history) > 2 and action != self.trade_history[-1]:
            exploration_bonus = 0.5

        reward = 0

        if action == "buy" and self.position is None:
            self.position = "long"
            self.position_price = self.price
            reward -= 0.1  # minor transaction fee

        elif action == "sell" and self.position == "long":
            pnl = self.price - self.position_price
            reward += pnl / 100  # scaled profit/loss
            self.balance += pnl
            self.position = None
            self.position_price = 0

        elif action == "hold" and self.position == "long":
            reward += (self.price - self.position_price) / 1000  # passive reward/loss

        else:
            reward -= 0.05  # penalty for invalid/no-op trades

        reward += exploration_bonus
        self.curiosity += exploration_bonus
        self.trade_history.append(action)
        self.reward_trace.append(reward)
        self.update_mood()

        done = self.balance <= 0 or self.cycle >= self.max_cycles

        state = {
            "price": round(self.price, 2),
            "volatility": round(self.volatility, 4),
            "mood": self.mood,
            "curiosity": round(self.curiosity, 2),
            "balance": round(self.balance, 2),
            "position": self.position or "none",
            "cycle": self.cycle,
            "reward": round(reward, 2)
        }

        return state, reward, done

    def reset(self):
        self.__init__()

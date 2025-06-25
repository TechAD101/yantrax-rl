# rl_core/env_market_sim.py - Placeholder content for RL-enhanced Yantra X
import gym
from gym import spaces
import numpy as np
import random

class MarketSimEnv(gym.Env):
    def __init__(self):
        super(MarketSimEnv, self).__init__()
        self.action_space = spaces.Discrete(3)  # BUY, SELL, HOLD
        self.observation_space = spaces.Box(low=0, high=1, shape=(3,), dtype=np.float32)
        self.reset()

    def reset(self):
        self.price = random.uniform(0.3, 0.7)
        self.volume = random.uniform(0.1, 0.9)
        self.trend = random.uniform(0.1, 0.9)
        return np.array([self.price, self.volume, self.trend])

    def step(self, action):
        reward = 0
        done = False
        info = {}

        if action == 0:  # BUY
            reward = self.price * self.volume * 1.5
        elif action == 1:  # SELL
            reward = self.price * (1 - self.volume)
        elif action == 2:  # HOLD
            reward = 0.01

        obs = self.reset()
        return obs, reward, done, info
import random

class MarketEnv:
    def __init__(self):
        self.price = 100.0
        self.step_count = 0

    def reset(self):
        self.price = 100.0
        self.step_count = 0
        return self.price

    def step(self, action):
        self.step_count += 1
        change = random.uniform(-1, 1)

        if action == "buy":
            self.price += change
        elif action == "sell":
            self.price -= change

        reward = change
        done = self.step_count >= 10
        return self.price, reward, done

    def get_action_space(self):
        return ["buy", "sell", "hold"]

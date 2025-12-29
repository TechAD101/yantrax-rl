# backend/rl_core/rl_trainer.py - Production RL Training System


import numpy as np
import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime
import logging
import asyncio

from rl_core.env_market_sim import MarketSimEnv

logger = logging.getLogger(__name__)

class PPOAgent:
    """
    Proximal Policy Optimization (PPO) Agent for trading decisions
    """

    def __init__(self, state_size: int = 8, action_size: int = 3, learning_rate: float = 0.0003):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate

        # PPO hyperparameters
        self.gamma = 0.99  # Discount factor
        self.epsilon = 0.2  # PPO clip parameter
        self.entropy_coeff = 0.01  # Entropy bonus for exploration
        self.value_coeff = 0.5  # Value function loss coefficient

        # Experience buffer
        self.memory = PPOMemory()

        # Simple neural network approximation (placeholder for actual NN)
        self.policy_network = self._initialize_policy_network()
        self.value_network = self._initialize_value_network()

        # Training statistics
        self.training_stats = {
            "episodes": 0,
            "total_reward": 0,
            "avg_reward": 0,
            "policy_losses": [],
            "value_losses": [],
            "best_reward": float('-inf'),
            "convergence_score": 0.0
        }

    def _initialize_policy_network(self) -> Dict:
        """Initialize policy network weights (simplified)"""
        return {
            "weights": np.random.randn(self.state_size, self.action_size) * 0.1,
            "bias": np.zeros(self.action_size)
        }

    def _initialize_value_network(self) -> Dict:
        """Initialize value network weights (simplified)"""
        return {
            "weights": np.random.randn(self.state_size, 1) * 0.1,
            "bias": np.zeros(1)
        }

    def get_action(self, state: np.ndarray, training: bool = True) -> Tuple[int, float]:
        """
        Get action using current policy with optional exploration
        """
        # Convert state dict to numpy array if needed
        if isinstance(state, dict):
            state_array = self._state_dict_to_array(state)
        else:
            state_array = state

        # Policy network forward pass (simplified)
        logits = np.dot(state_array, self.policy_network["weights"]) + self.policy_network["bias"]

        # Apply softmax for action probabilities
        exp_logits = np.exp(logits - np.max(logits))  # Numerical stability
        action_probs = exp_logits / np.sum(exp_logits)

        if training:
            # Sample action from policy during training
            action = np.random.choice(self.action_size, p=action_probs)
        else:
            # Use greedy policy during evaluation
            action = np.argmax(action_probs)

        action_prob = action_probs[action]

        return action, action_prob

    def get_value(self, state: np.ndarray) -> float:
        """Get state value estimate"""
        if isinstance(state, dict):
            state_array = self._state_dict_to_array(state)
        else:
            state_array = state

        # Value network forward pass (simplified)
        value = np.dot(state_array, self.value_network["weights"]) + self.value_network["bias"]
        return float(value[0])

    def _state_dict_to_array(self, state_dict: Dict) -> np.ndarray:
        """Convert state dictionary to numpy array for neural network"""
        return np.array([
            state_dict.get("price", 0) / 50000.0,  # Normalized price
            state_dict.get("volatility", 0) * 10,  # Scaled volatility
            state_dict.get("balance", 0) / 20000.0,  # Normalized balance
            1.0 if state_dict.get("position") == "long" else 0.0,  # Position encoding
            state_dict.get("cycle", 0) / 50.0,  # Normalized cycle
            state_dict.get("curiosity", 0),  # Curiosity level
            self._mood_to_numeric(state_dict.get("mood", "neutral")),  # Mood encoding
            state_dict.get("reward", 0) / 10.0  # Normalized reward
        ])

    def _mood_to_numeric(self, mood: str) -> float:
        """Convert mood string to numeric value"""
        mood_map = {
            "euphoric": 1.0,
            "neutral": 0.0,
            "panic": -1.0,
            "bored": -0.5,
            "crisis": -1.5
        }
        return mood_map.get(mood, 0.0)

    def store_transition(self, state, action, action_prob, reward, next_state, done):
        """Store transition in memory buffer"""
        self.memory.store_transition(state, action, action_prob, reward, next_state, done)

    def train(self) -> Dict[str, float]:
        """
        Train the agent using PPO algorithm
        """
        if len(self.memory.states) < 32:  # Minimum batch size
            return {"policy_loss": 0.0, "value_loss": 0.0}

        # Get batch data
        states, actions, old_probs, rewards, next_states, dones = self.memory.get_batch()

        # Convert states to arrays
        state_arrays = np.array([self._state_dict_to_array(s) for s in states])
        next_state_arrays = np.array([self._state_dict_to_array(s) for s in next_states])

        # Calculate advantages using TD error
        values = np.array([self.get_value(s) for s in state_arrays])
        next_values = np.array([self.get_value(s) for s in next_state_arrays])

        # Calculate TD targets and advantages
        td_targets = rewards + self.gamma * next_values * (1 - np.array(dones))
        advantages = td_targets - values

        # Normalize advantages
        advantages = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-8)

        # PPO policy update (simplified)
        policy_loss = self._update_policy(state_arrays, actions, old_probs, advantages)

        # Value function update
        value_loss = self._update_value_function(state_arrays, td_targets)

        # Clear memory after training
        self.memory.clear()

        # Update training statistics
        self.training_stats["policy_losses"].append(policy_loss)
        self.training_stats["value_losses"].append(value_loss)

        return {
            "policy_loss": policy_loss,
            "value_loss": value_loss,
            "avg_advantage": np.mean(advantages)
        }

    def _update_policy(self, states: np.ndarray, actions: List[int], old_probs: List[float], advantages: np.ndarray) -> float:
        """Update policy network using PPO loss"""
        total_loss = 0.0

        for i in range(len(states)):
            # Get current action probabilities
            logits = np.dot(states[i], self.policy_network["weights"]) + self.policy_network["bias"]
            exp_logits = np.exp(logits - np.max(logits))
            action_probs = exp_logits / np.sum(exp_logits)

            # Calculate probability ratio
            new_prob = action_probs[actions[i]]
            old_prob = old_probs[i]
            ratio = new_prob / (old_prob + 1e-8)

            # PPO clipped objective
            clipped_ratio = np.clip(ratio, 1 - self.epsilon, 1 + self.epsilon)
            policy_loss = -min(ratio * advantages[i], clipped_ratio * advantages[i])

            # Add entropy bonus for exploration
            entropy = -np.sum(action_probs * np.log(action_probs + 1e-8))
            policy_loss -= self.entropy_coeff * entropy

            total_loss += policy_loss

            # Simple gradient update (placeholder for actual backprop)
            gradient = self._calculate_policy_gradient(states[i], actions[i], advantages[i], ratio)
            self.policy_network["weights"] -= self.learning_rate * gradient["weights"]
            self.policy_network["bias"] -= self.learning_rate * gradient["bias"]

        return total_loss / len(states)

    def _update_value_function(self, states: np.ndarray, targets: np.ndarray) -> float:
        """Update value function network"""
        total_loss = 0.0

        for i in range(len(states)):
            # Current value prediction
            current_value = np.dot(states[i], self.value_network["weights"]) + self.value_network["bias"]

            # MSE loss
            value_loss = 0.5 * (targets[i] - current_value[0]) ** 2
            total_loss += value_loss

            # Simple gradient update
            error = targets[i] - current_value[0]
            self.value_network["weights"] += self.learning_rate * error * states[i].reshape(-1, 1)
            self.value_network["bias"] += self.learning_rate * error

        return total_loss / len(states)

    def _calculate_policy_gradient(self, state: np.ndarray, action: int, advantage: float, ratio: float) -> Dict:
        """Calculate policy gradient (simplified)"""
        # This is a simplified gradient calculation
        # In practice, you'd use automatic differentiation
        gradient_scale = advantage * min(1, max(-1, ratio))

        return {
            "weights": gradient_scale * np.outer(state, np.eye(self.action_size)[action]),
            "bias": gradient_scale * np.eye(self.action_size)[action]
        }

    def save_model(self, filepath: str):
        """Save model weights and training statistics"""
        model_data = {
            "policy_network": self.policy_network,
            "value_network": self.value_network,
            "training_stats": self.training_stats,
            "hyperparameters": {
                "state_size": self.state_size,
                "action_size": self.action_size,
                "learning_rate": self.learning_rate,
                "gamma": self.gamma,
                "epsilon": self.epsilon
            }
        }

        # Convert numpy arrays to lists for JSON serialization
        for network in ["policy_network", "value_network"]:
            for param in model_data[network]:
                if isinstance(model_data[network][param], np.ndarray):
                    model_data[network][param] = model_data[network][param].tolist()

        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)

        logger.info(f"✅ Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load model weights and training statistics"""
        if not os.path.exists(filepath):
            logger.warning(f"Model file {filepath} not found, using random initialization")
            return

        with open(filepath, 'r') as f:
            model_data = json.load(f)

        # Restore networks
        for network in ["policy_network", "value_network"]:
            for param in model_data[network]:
                model_data[network][param] = np.array(model_data[network][param])

        self.policy_network = model_data["policy_network"]
        self.value_network = model_data["value_network"]
        self.training_stats = model_data["training_stats"]

        logger.info(f"✅ Model loaded from {filepath}")


class PPOMemory:
    """Memory buffer for PPO training"""

    def __init__(self):
        self.states = []
        self.actions = []
        self.action_probs = []
        self.rewards = []
        self.next_states = []
        self.dones = []

    def store_transition(self, state, action, action_prob, reward, next_state, done):
        self.states.append(state)
        self.actions.append(action)
        self.action_probs.append(action_prob)
        self.rewards.append(reward)
        self.next_states.append(next_state)
        self.dones.append(done)

    def get_batch(self):
        return (
            self.states,
            self.actions,
            self.action_probs,
            np.array(self.rewards),
            self.next_states,
            self.dones
        )

    def clear(self):
        self.states = []
        self.actions = []
        self.action_probs = []
        self.rewards = []
        self.next_states = []
        self.dones = []



class AdvancedRLTrainer:
    """
    Advanced RL training coordinator with multiple agents and strategies
    """

    def __init__(self):
        self.agents = {
            "primary": PPOAgent(),
            "exploration": PPOAgent(learning_rate=0.001),  # Higher LR for exploration
            "conservative": PPOAgent(learning_rate=0.0001)  # Lower LR for stability
        }
        self.training_history = []
        self.best_performance = {
            "agent": None,
            "reward": float('-inf'),
            "episode": 0
        }

    async def train_model_async(self, episodes: int = 100, learning_rate: float = 0.0003) -> Dict:
        """
        Enhanced async training with multiple agents and performance tracking
        """
        logger.info(f"🧠 Starting advanced RL training (async): {episodes} episodes")
        env = MarketSimEnv()
        training_results = {
            "episodes_completed": 0,
            "total_reward": 0,
            "best_reward": float('-inf'),
            "convergence_metrics": {},
            "agent_performance": {},
            "training_time": datetime.now().isoformat()
        }
        for episode in range(episodes):
            episode_results = await asyncio.to_thread(self._train_episode, env, episode)
            training_results["episodes_completed"] = episode + 1
            training_results["total_reward"] += episode_results["reward"]
            training_results["best_reward"] = max(training_results["best_reward"], episode_results["reward"])
            if episode_results["reward"] > self.best_performance["reward"]:
                self.best_performance.update({
                    "agent": episode_results["best_agent"],
                    "reward": episode_results["reward"],
                    "episode": episode
                })
            if (episode + 1) % 25 == 0:
                await asyncio.to_thread(self._evaluate_agents, env)
                await asyncio.to_thread(self._save_best_models)
                logger.info(f"📊 Episode {episode + 1}/{episodes} | Best Reward: {training_results['best_reward']:.3f}")
        avg_reward = training_results["total_reward"] / episodes
        convergence_score = self._calculate_convergence_score()
        training_results.update({
            "average_reward": avg_reward,
            "convergence_score": convergence_score,
            "status": "completed",
            "best_agent": self.best_performance["agent"]
        })
        logger.info(f"✅ Training completed | Avg Reward: {avg_reward:.3f} | Convergence: {convergence_score:.3f}")
        return training_results

    def _train_episode(self, env: MarketSimEnv, episode: int) -> Dict:
        """Train a single episode with agent coordination"""
        state = env.reset()
        episode_reward = 0
        steps = 0
        agent_rewards = defaultdict(float)

        # Select agent for this episode (ensemble approach)
        if episode % 3 == 0:
            current_agent = self.agents["primary"]
            agent_name = "primary"
        elif episode % 3 == 1:
            current_agent = self.agents["exploration"]  
            agent_name = "exploration"
        else:
            current_agent = self.agents["conservative"]
            agent_name = "conservative"

        done = False
        while not done and steps < 50:
            # Get action from current agent
            action_idx, action_prob = current_agent.get_action(state, training=True)

            # Convert action index to action string
            actions = ["buy", "sell", "hold"]
            action = actions[action_idx]

            # Execute action in environment
            next_state, reward, done = env.step(action)

            # Store transition for training
            current_agent.store_transition(state, action_idx, action_prob, reward, next_state, done)

            # Update episode tracking
            episode_reward += reward
            agent_rewards[agent_name] += reward
            state = next_state
            steps += 1

        # Train agent after episode
        if len(current_agent.memory.states) >= 10:  # Minimum batch size
            training_losses = current_agent.train()

        return {
            "reward": episode_reward,
            "steps": steps,
            "best_agent": agent_name,
            "agent_rewards": dict(agent_rewards)
        }

    def _evaluate_agents(self, env: MarketSimEnv):
        """Evaluate all agents on test episodes"""
        logger.info("🔍 Evaluating agent performance...")

        for agent_name, agent in self.agents.items():
            test_rewards = []

            for _ in range(5):  # 5 evaluation episodes
                state = env.reset()
                episode_reward = 0
                done = False
                steps = 0

                while not done and steps < 50:
                    action_idx, _ = agent.get_action(state, training=False)  # Greedy policy
                    actions = ["buy", "sell", "hold"]
                    action = actions[action_idx]

                    next_state, reward, done = env.step(action)
                    episode_reward += reward
                    state = next_state
                    steps += 1

                test_rewards.append(episode_reward)

            avg_test_reward = np.mean(test_rewards)
            logger.info(f"📈 {agent_name.capitalize()} Agent | Avg Test Reward: {avg_test_reward:.3f}")

    def _save_best_models(self):
        """Save the best performing models"""
        models_dir = "models"
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        for agent_name, agent in self.agents.items():
            filepath = f"{models_dir}/ppo_{agent_name}_best.json"
            agent.save_model(filepath)

    def _calculate_convergence_score(self) -> float:
        """Calculate training convergence score"""
        if not self.training_history:
            return 0.0

        # Simple convergence metric based on reward stability
        recent_rewards = [ep["reward"] for ep in self.training_history[-20:]]
        if len(recent_rewards) < 10:
            return 0.0

        reward_std = np.std(recent_rewards)
        reward_mean = np.mean(recent_rewards)

        # Lower variance relative to mean indicates better convergence
        convergence_score = max(0, 1 - (reward_std / (abs(reward_mean) + 1)))
        return min(1.0, convergence_score)


# Global trainer instance

# Global trainer instance (must be after class definition)

# Global trainer instance (must be after class definition)



def train_model(episodes: int = 100, learning_rate: float = 0.0003) -> Dict:
    """
    Main training function - Production ready RL training
    """
    return global_trainer.train_model(episodes, learning_rate)


# Global trainer instance (must be after class definition)
global_trainer = AdvancedRLTrainer()

def run_rl_cycle() -> Dict:
    """
    Enhanced RL cycle with production features
    """
    logger.info("🔥 Initializing Enhanced RL Cycle...")

    try:
        env = MarketSimEnv()
        agent = global_trainer.agents["primary"]  # Use best performing agent

        state = env.reset()
        total_reward = 0
        steps = []
        performance_metrics = {
            "decision_confidence": [],
            "risk_adjusted_returns": [],
            "exploration_rate": []
        }

        # Run enhanced episode with detailed tracking
        for step_idx in range(10):  # More steps for better analysis
            # Get action with confidence tracking
            action_idx, action_prob = agent.get_action(state, training=False)
            actions = ["buy", "sell", "hold"]
            action = actions[action_idx]

            # Execute action
            next_state, reward, done = env.step(action)

            # Calculate performance metrics
            confidence = action_prob
            risk_adj_return = reward / max(0.1, state.get("volatility", 0.1))  # Risk-adjusted
            exploration_rate = 1.0 - confidence  # Higher when less confident

            performance_metrics["decision_confidence"].append(confidence)
            performance_metrics["risk_adjusted_returns"].append(risk_adj_return)
            performance_metrics["exploration_rate"].append(exploration_rate)

            # Enhanced step tracking
            step_data = {
                "action": action,
                "state": next_state,
                "reward": reward,
                "confidence": confidence,
                "risk_adjusted_return": risk_adj_return,
                "value_estimate": agent.get_value(state)
            }
            steps.append(step_data)

            total_reward += reward
            state = next_state

            if done:
                logger.info(f"🛑 RL episode completed early at step {step_idx + 1}")
                break

        # Calculate advanced metrics
        avg_confidence = np.mean(performance_metrics["decision_confidence"])
        risk_adjusted_performance = np.mean(performance_metrics["risk_adjusted_returns"])
        exploration_level = np.mean(performance_metrics["exploration_rate"])

        # Market adaptation score
        price_changes = [step["state"]["price"] for step in steps]
        market_volatility = np.std(price_changes) if len(price_changes) > 1 else 0
        adaptation_score = 1.0 / (1.0 + market_volatility / 1000)  # Higher score for better adaptation

        logger.info("✅ Enhanced RL cycle completed successfully")

        return {
            "status": "success",
            "final_balance": state["balance"],
            "final_mood": state["mood"],
            "final_cycle": state["cycle"],
            "curiosity": state["curiosity"],
            "total_reward": round(total_reward, 3),
            "steps": steps,
            "performance_metrics": {
                "average_confidence": round(avg_confidence, 3),
                "risk_adjusted_performance": round(risk_adjusted_performance, 3),
                "exploration_level": round(exploration_level, 3),
                "market_adaptation_score": round(adaptation_score, 3)
            },
            "advanced_analytics": {
                "volatility_handled": round(market_volatility, 2),
                "decision_consistency": round(1.0 - np.std(performance_metrics["decision_confidence"]), 3),
                "profit_efficiency": round(total_reward / max(1, len(steps)), 3)
            }
        }

    except Exception as e:
        logger.error(f"❌ Enhanced RL cycle failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

def get_training_stats() -> Dict:
    """Get comprehensive training statistics"""
    return {
        "best_performance": global_trainer.best_performance,
        "agent_count": len(global_trainer.agents),
        "training_episodes": len(global_trainer.training_history),
        "convergence_score": global_trainer._calculate_convergence_score()
    }

def reset_training() -> Dict:
    """Reset training state for fresh start"""
    global global_trainer
    global_trainer = AdvancedRLTrainer()
    logger.info("🔄 Training state reset successfully")
    return {"status": "reset_complete", "timestamp": datetime.now().isoformat()}

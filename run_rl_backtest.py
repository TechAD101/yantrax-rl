import sys
import os

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from rl_core.rl_trainer import run_rl_cycle  # noqa: E402


def run_backtest():
    print("🧠 Starting RL Backtest Cycle...")
    print("Target: MarketSimEnv (Emotionally Adaptive Simulator)")

    try:
        results = run_rl_cycle()

        if results["status"] == "success":
            print("✅ Backtest Completed Successfully!")
            print(f"Total Reward: {results['total_reward']}")
            print(f"Final Balance: ${results['final_balance']}")
            print(f"Final Mood: {results['final_mood']}")
            print(f"Curiosity Score: {results['curiosity']}")

            print("\n📈 Performance Metrics:")
            for k, v in results["performance_metrics"].items():
                print(f"  - {k}: {v}")

            print("\n📊 Advanced Analytics:")
            for k, v in results["advanced_analytics"].items():
                print(f"  - {k}: {v}")

            print("\n📝 Sample Steps:")
            for i, step in enumerate(results["steps"][:3]):
                action = step['action']
                price = step['state']['price']
                reward = step['reward']
                print(f"  Step {i + 1}: {action} | Price: ${price} | Reward: {reward}")

            return True
        else:
            print(f"❌ Backtest failed: {results.get('message')}")
            return False

    except Exception as e:
        print(f"❌ Execution error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_backtest()
    sys.exit(0 if success else 1)

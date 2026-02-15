import json
import os
import random
from datetime import datetime, timezone


class ReinforcementLearner:
    """
    Q-Learning Reinforcement Learner with persistent auction history.

    The brain (Q-table) adapts over time:
    - ENGAGE vs INTIMIDATE weights shift based on win/loss outcomes
    - Auction history builds a dataset for deeper self-tutoring
    - Exploration rate (epsilon) decays as experience grows
    """

    def __init__(self, brain_path="brain.json", history_path="auction_history.json"):
        self.brain_path = brain_path
        self.history_path = history_path
        self.q_table = self._load_brain()
        self.history = self._load_history()
        # Actions to track
        self.actions = ["ENGAGE", "INTIMIDATE"]
        self.last_action = None
        self._session_actions = []  # All actions taken this auction

        # Exploration vs exploitation
        self.epsilon = max(0.05, 0.3 - (len(self.history) * 0.02))
        self.learning_rate = 0.1
        self.discount_factor = 0.95

    def _load_brain(self):
        if os.path.exists(self.brain_path):
            with open(self.brain_path, 'r') as f:
                return json.load(f)
        # Initial weights: Slightly favor standard engagement
        return {"ENGAGE": 0.5, "INTIMIDATE": 0.5}

    def _load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, 'r') as f:
                return json.load(f)
        return []

    def record_action(self, action):
        self.last_action = action
        self._session_actions.append(action)

    def should_explore(self) -> bool:
        """Epsilon-greedy: occasionally try the less-favored action."""
        return random.random() < self.epsilon

    def get_preferred_action(self) -> str:
        """Return the action with the highest Q-value, or explore."""
        if self.should_explore():
            return random.choice(self.actions)
        return max(self.actions, key=lambda a: self.q_table.get(a, 0.5))

    def update_strategy(self, won_auction: bool, final_price_ratio: float):
        """
        Called after auction ends.
        won_auction: Boolean
        final_price_ratio: Final Price / Max Budget (Lower is better)
        """
        if not self.last_action:
            return

        # Calculate reward signal
        reward = 0
        if won_auction:
            reward += 1.0
            # Bonus for winning cheaply
            if final_price_ratio < 0.6:
                reward += 1.0   # Great deal
            elif final_price_ratio < 0.8:
                reward += 0.5   # Good deal
            elif final_price_ratio > 0.95:
                reward -= 0.2   # Won, but paid near ceiling
        else:
            reward -= 0.5

        # Q-learning update for each action used this session
        actions_used = set(self._session_actions)
        for action in actions_used:
            current_val = self.q_table.get(action, 0.5)
            # Bellman-style update: Q(s,a) = Q(s,a) + alpha * (reward - Q(s,a))
            self.q_table[action] = current_val + self.learning_rate * (reward - current_val)

        # Decay epsilon as we gain experience
        self.epsilon = max(0.05, self.epsilon - 0.01)

        self._save_brain()
        self._session_actions = []

    def record_auction_result(self, lot_id: str, lot_url: str, max_budget: float,
                               greediness: int, won: bool, final_price: float,
                               actions_taken: list):
        """
        Persist a complete auction record for future self-tutoring and analysis.
        """
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lot_id": lot_id,
            "lot_url": lot_url,
            "max_budget": max_budget,
            "greediness": greediness,
            "won": won,
            "final_price": final_price,
            "price_ratio": final_price / max_budget if max_budget > 0 else 0,
            "actions_taken": actions_taken,
            "q_table_snapshot": dict(self.q_table),
        }
        self.history.append(record)
        self._save_history()

    def get_win_rate(self) -> float:
        """Overall win rate across all recorded auctions."""
        if not self.history:
            return 0.0
        wins = sum(1 for r in self.history if r["won"])
        return wins / len(self.history)

    def get_avg_savings(self) -> float:
        """Average savings ratio on won auctions (1.0 - price_ratio)."""
        won_records = [r for r in self.history if r["won"]]
        if not won_records:
            return 0.0
        return sum(1.0 - r["price_ratio"] for r in won_records) / len(won_records)

    def get_stats(self) -> dict:
        """Full learner statistics for dashboards and analysis."""
        return {
            "q_table": dict(self.q_table),
            "epsilon": self.epsilon,
            "total_auctions": len(self.history),
            "win_rate": self.get_win_rate(),
            "avg_savings": self.get_avg_savings(),
            "preferred_action": self.get_preferred_action(),
        }

    def _save_brain(self):
        with open(self.brain_path, 'w') as f:
            json.dump(self.q_table, f, indent=2)

    def _save_history(self):
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f, indent=2)

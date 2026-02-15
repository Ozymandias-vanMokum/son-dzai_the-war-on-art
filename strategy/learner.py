import json
import os
import random

class ReinforcementLearner:
    def __init__(self, brain_path="brain.json"):
        self.brain_path = brain_path
        self.q_table = self._load_brain()
        # Actions to track
        self.actions = ["ENGAGE", "INTIMIDATE"]
        self.last_action = None

    def _load_brain(self):
        if os.path.exists(self.brain_path):
            with open(self.brain_path, 'r') as f:
                return json.load(f)
        # Initial weights: Slightly favor standard engagement
        return {"ENGAGE": 0.5, "INTIMIDATE": 0.5}

    def record_action(self, action):
        self.last_action = action

    def update_strategy(self, won_auction: bool, final_price_ratio: float):
        """
        Called after auction ends.
        won_auction: Boolean
        final_price_ratio: Final Price / Max Budget (Lower is better)
        """
        if not self.last_action: return

        reward = 0
        if won_auction:
            reward += 1.0
            # Bonus for winning cheaply
            if final_price_ratio < 0.8: reward += 0.5
        else:
            reward -= 0.5

        # Simple Update Rule
        current_val = self.q_table.get(self.last_action, 0.5)
        self.q_table[self.last_action] = current_val + (0.1 * reward)

        self._save_brain()

    def _save_brain(self):
        with open(self.brain_path, 'w') as f:
            json.dump(self.q_table, f)

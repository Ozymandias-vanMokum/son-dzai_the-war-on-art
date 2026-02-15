import random
from typing import Tuple
from .inputs import AuctionParams

class WarOnArtEngine:
    def __init__(self, params: AuctionParams, learner=None):
        self.params = params
        self.learner = learner  # Reinforcement Learning Module
        self.my_last_bid = 0

    def evaluate_state(self, current_highest_bid: float, time_remaining_s: int, is_leader: bool) -> Tuple[str, float, str]:
        """
        Returns: (ACTION, BID_AMOUNT, LOG_REASON)
        Actions: 'WAIT', 'ANCHOR', 'ENGAGE', 'INTIMIDATE', 'ABANDON'
        """
        # 1. THE "WINNER'S CURSE" GUARDRAIL
        next_min_bid = self._get_next_increment(current_highest_bid)
        total_cost = self.params.calculate_total_acquisition_cost(next_min_bid)

        if total_cost > self.params.true_ceiling:
            return "ABANDON", 0.0, "Budget exceeded. Retreating with discipline."

        # 2. THE OPENING (Days 1 - 6)
        # "He will win who knows when not to fight."
        if time_remaining_s > 3600: # > 1 Hour
            return "WAIT", 0.0, "Too early. Concealing intent."

        # 3. THE SKIRMISH (Last Hour)
        if 60 < time_remaining_s <= 3600:
            # If we haven't bid yet, place ONE anchor to signal intent if Greediness is moderate
            if not is_leader and self.my_last_bid == 0 and self.params.greediness > 40:
                return "ANCHOR", next_min_bid, "Setting Anchor Bid."
            return "WAIT", 0.0, "Holding position."

        # 4. THE BATTLEFIELD (Last 60 Seconds)
        if time_remaining_s <= 60:
            if is_leader:
                return "WAIT", 0.0, "We have Sente (Initiative). Waiting."

            # THE "DEAD ZONE" LOGIC
            # Only engage when time is critical to force the 90s reset loop
            if time_remaining_s < 15:
                # TACTIC: INTIMIDATION (The Jump Bid)
                # If Greediness is High (>70%), we skip a step to break their will.
                if self.params.greediness > 70:
                    jump_bid = self._get_jump_bid(current_highest_bid)
                    if self.params.calculate_total_acquisition_cost(jump_bid) <= self.params.true_ceiling:
                        if self.learner: self.learner.record_action("INTIMIDATE")
                        return "INTIMIDATE", jump_bid, "Executing Rapid Jump-Bid."

                # TACTIC: STANDARD ENGAGE
                if self.learner: self.learner.record_action("ENGAGE")
                return "ENGAGE", next_min_bid, "Standard Counter-Bid."

            return "WAIT", 0.0, "Letting the opponent sweat (Gote)."

        return "WAIT", 0.0, "No state change."

    def _get_next_increment(self, current_bid: float) -> float:
        """Official Catawiki Increments"""
        if current_bid < 100: return current_bid + 5
        if current_bid < 200: return current_bid + 10
        if current_bid < 500: return current_bid + 20
        if current_bid < 1000: return current_bid + 50
        return current_bid + 100

    def _get_jump_bid(self, current_bid: float) -> float:
        """Calculates a Double-Increment Jump"""
        step_one = self._get_next_increment(current_bid)
        return self._get_next_increment(step_one)

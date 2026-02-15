from dataclasses import dataclass

@dataclass
class AuctionParams:
    """
    Captures Codruta's inputs and calculates the hidden 'True Ceiling'.
    """
    lot_id: str
    lot_url: str
    max_budget: float  # The absolute Euro limit (e.g., 500)
    greediness: int    # 0-100: 100 = "Whatever it takes" (Aggressive Jump Bids)

    @property
    def true_ceiling(self) -> float:
        """
        Calculates the 'Ozymandias Offset'.
        Never bid a round number. If Budget is €500, True Ceiling becomes €511.
        This clears the psychological barriers of other humans.
        """
        base_max = self.max_budget

        # If the budget is round (divisible by 5 or 10), add a prime offset
        if base_max % 5 == 0:
            # Adds ~2.2% buffer to break round-number walls
            offset = (base_max * 0.022) // 1
            return base_max + offset
        return base_max

    def calculate_total_acquisition_cost(self, bid_amount: float) -> float:
        """
        Catawiki Fee Calculation:
        Bid + 9% Auction Fee + €3 Protection Fee
        """
        return bid_amount + (bid_amount * 0.09) + 3

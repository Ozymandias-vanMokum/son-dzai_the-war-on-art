"""
Auction Monitor -- The Heartbeat Loop.

Connects the Strategic Mind (WarOnArtEngine) to the Mechanical Hand (CatawikiBrowser).
Polls the auction state every second and executes the engine's tactical commands.
"""

import asyncio
import logging
from datetime import datetime, timezone

from strategy.inputs import AuctionParams
from strategy.engine import WarOnArtEngine
from strategy.learner import ReinforcementLearner
from catawiki.browser import CatawikiBrowser, AuctionState

logger = logging.getLogger("catawiki.monitor")


class AuctionMonitor:
    """
    Real-time auction controller.

    Lifecycle:
    1. Initialize with Codruta's params
    2. Call run() to begin the polling loop
    3. Engine evaluates state every tick
    4. When engine returns ENGAGE/INTIMIDATE/ANCHOR, browser places the bid
    5. After auction closes, feeds result back to the Learner for self-tutoring
    """

    def __init__(
        self,
        params: AuctionParams,
        browser: CatawikiBrowser,
        learner: ReinforcementLearner,
        poll_interval: float = 2.0,
        log_callback=None,
    ):
        self.params = params
        self.browser = browser
        self.learner = learner
        self.engine = WarOnArtEngine(params, learner)
        self.poll_interval = poll_interval
        self.log_callback = log_callback  # For Jupyter / UI output

        self._running = False
        self._battle_log = []

    async def run(self):
        """
        Main auction loop. Polls until the auction closes or we ABANDON.
        """
        self._running = True
        self._log("DEPLOY", f"War Room active for lot {self.params.lot_id}")
        self._log("INTEL", f"Budget: EUR {self.params.max_budget} | "
                           f"True Ceiling: EUR {self.params.true_ceiling} | "
                           f"Greediness: {self.params.greediness}%")

        abandoned = False

        try:
            while self._running:
                # 1. Observe
                state = await self.browser.get_auction_state(self.params.lot_url)

                if state.closed:
                    self._log("END", f"Auction closed. Final bid: EUR {state.current_bid}")
                    break

                # 2. Think
                action, amount, reason = self.engine.evaluate_state(
                    state.current_bid,
                    state.time_remaining_s,
                    state.is_leader,
                )

                self._log(action, f"EUR {amount:.2f} | {reason} | "
                                  f"Bid: EUR {state.current_bid} | "
                                  f"Time: {state.time_remaining_s}s | "
                                  f"Leader: {state.is_leader}")

                # 3. Act
                if action in ("ENGAGE", "INTIMIDATE", "ANCHOR"):
                    success = await self.browser.place_bid(self.params.lot_url, amount)
                    if success:
                        self.engine.my_last_bid = amount
                        self._log("EXECUTED", f"Bid EUR {amount:.2f} placed ({action})")
                    else:
                        self._log("FAILED", f"Bid EUR {amount:.2f} was not confirmed")

                elif action == "ABANDON":
                    abandoned = True
                    self._log("RETREAT", "Budget exceeded. Leaving the battlefield.")
                    break

                # 4. Adaptive polling: faster in the Dead Zone
                if state.time_remaining_s <= 60:
                    await asyncio.sleep(1.0)
                elif state.time_remaining_s <= 3600:
                    await asyncio.sleep(min(self.poll_interval, 5.0))
                else:
                    await asyncio.sleep(min(self.poll_interval * 5, 30.0))

        except asyncio.CancelledError:
            self._log("ABORT", "Monitor cancelled by user.")
        except Exception as e:
            self._log("ERROR", str(e))
            raise
        finally:
            self._running = False

        # 5. Post-battle: feed results to the Learner
        if not abandoned:
            final_state = await self.browser.get_auction_state(self.params.lot_url)
            won = final_state.is_leader
            ratio = final_state.current_bid / self.params.max_budget if self.params.max_budget > 0 else 1.0
            self.learner.update_strategy(won, ratio)

            self._log("DEBRIEF",
                      f"Won: {won} | Final: EUR {final_state.current_bid} | "
                      f"Ratio: {ratio:.2%} | Brain updated.")

        return self._battle_log

    def stop(self):
        """Gracefully stop the monitor loop."""
        self._running = False

    def _log(self, tag: str, message: str):
        """Record a battle log entry."""
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"[{ts}] [{tag:>10}] {message}"
        self._battle_log.append(entry)
        logger.info(entry)
        if self.log_callback:
            self.log_callback(entry)

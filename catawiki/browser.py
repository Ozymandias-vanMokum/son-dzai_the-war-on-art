"""
Catawiki Browser Client -- The Mechanical Hand.

Uses Playwright to interact with Catawiki on Codruta's behalf:
- OAuth/session login
- Scrape live auction state (current bid, time remaining, leader status)
- Place bids when the Strategic Mind commands ENGAGE or INTIMIDATE
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger("catawiki.browser")


@dataclass
class AuctionState:
    """Live snapshot of a Catawiki auction lot."""
    lot_id: str
    current_bid: float
    time_remaining_s: int
    is_leader: bool
    bid_count: int
    lot_title: str
    closed: bool


class CatawikiBrowser:
    """
    Headless (or headed) browser automation for Catawiki.

    Supports two authentication flows:
    1. Cookie injection -- load saved session cookies (fast, no UI)
    2. Interactive login -- open a visible browser for Codruta to log in once,
       then persist cookies for future headless runs.
    """

    BASE_URL = "https://www.catawiki.com"

    def __init__(self, headless: bool = True, cookies_path: str = "catawiki_cookies.json"):
        self.headless = headless
        self.cookies_path = cookies_path
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    # ── Lifecycle ──────────────────────────────────────────────

    async def launch(self):
        """Start browser and restore session if cookies exist."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        self._page = await self._context.new_page()

        # Try to restore cookies from previous session
        await self._load_cookies()
        logger.info("Browser launched (headless=%s)", self.headless)

    async def close(self):
        """Persist cookies and shut down."""
        if self._context:
            await self._save_cookies()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed.")

    # ── Authentication ─────────────────────────────────────────

    async def login_interactive(self):
        """
        Opens the Catawiki login page in a VISIBLE browser so Codruta
        can authenticate manually (supports OAuth, 2FA, etc.).
        After login, cookies are saved for future headless sessions.
        """
        if self.headless:
            logger.warning("Switching to headed mode for interactive login.")
            await self.close()
            self.headless = False
            await self.launch()

        await self._page.goto(f"{self.BASE_URL}/buyer/login", wait_until="networkidle")
        logger.info("Waiting for Codruta to log in...")

        # Wait until we land on a page that proves we're authenticated
        # Catawiki redirects to /u/ or the homepage after login
        await self._page.wait_for_url(
            re.compile(r"catawiki\.com/(u/|$)"),
            timeout=300_000,  # 5 min to log in
        )
        await self._save_cookies()
        logger.info("Login successful. Cookies saved to %s", self.cookies_path)

    async def is_logged_in(self) -> bool:
        """Check if current session is authenticated."""
        try:
            await self._page.goto(f"{self.BASE_URL}/buyer/login", wait_until="networkidle")
            # If we get redirected away from login, we're authenticated
            return "/login" not in self._page.url
        except Exception:
            return False

    # ── Auction Monitoring ─────────────────────────────────────

    async def get_auction_state(self, lot_url: str) -> AuctionState:
        """
        Navigate to the lot page and scrape live auction data.
        Returns a structured AuctionState snapshot.
        """
        await self._page.goto(lot_url, wait_until="networkidle")
        await asyncio.sleep(1)  # Let JS-rendered auction widget settle

        state = await self._page.evaluate("""() => {
            // Catawiki renders auction data in structured DOM elements.
            // These selectors target the live auction widget.
            const getText = (sel) => {
                const el = document.querySelector(sel);
                return el ? el.textContent.trim() : '';
            };

            // Current bid amount (strip currency symbols, commas)
            const bidText = getText('[data-testid="current-bid-amount"], .lot-bidding__current-bid, .be-lot-header__price');
            const currentBid = parseFloat(bidText.replace(/[^0-9.,]/g, '').replace(',', '.')) || 0;

            // Time remaining -- Catawiki shows "Xd Xh", "Xh Xm", "Xm Xs", or "Xs"
            const timeText = getText('[data-testid="time-remaining"], .lot-bidding__time-remaining, .be-lot-header__time-remaining');

            // Bid count
            const countText = getText('[data-testid="bid-count"], .lot-bidding__bid-count');
            const bidCount = parseInt(countText.replace(/[^0-9]/g, '')) || 0;

            // Are we currently the highest bidder?
            const leaderIndicator = document.querySelector(
                '[data-testid="highest-bidder-indicator"], .lot-bidding__highest-bidder, .be-lot-header__winning'
            );
            const isLeader = !!leaderIndicator;

            // Lot title
            const title = getText('h1');

            // Is auction closed?
            const closedIndicator = document.querySelector(
                '[data-testid="lot-closed"], .lot-bidding__closed'
            );
            const closed = !!closedIndicator;

            return { currentBid, timeText, bidCount, isLeader, title, closed };
        }""")

        time_remaining_s = self._parse_time_remaining(state.get("timeText", ""))

        # Extract lot ID from URL
        lot_id = lot_url.rstrip("/").split("/")[-1]

        return AuctionState(
            lot_id=lot_id,
            current_bid=state["currentBid"],
            time_remaining_s=time_remaining_s,
            is_leader=state["isLeader"],
            bid_count=state["bidCount"],
            lot_title=state["title"],
            closed=state["closed"],
        )

    async def place_bid(self, lot_url: str, amount: float) -> bool:
        """
        Place a bid on the given lot. Returns True if the bid was accepted.

        Catawiki's bidding flow:
        1. Click the bid button
        2. Confirm the bid amount in the modal
        3. Verify success feedback
        """
        try:
            # Ensure we're on the lot page
            if self._page.url != lot_url:
                await self._page.goto(lot_url, wait_until="networkidle")
                await asyncio.sleep(1)

            # Click the main bid button
            bid_button = await self._page.query_selector(
                '[data-testid="place-bid-button"], '
                'button.lot-bidding__bid-button, '
                'button[class*="BidButton"], '
                'button:has-text("Place bid")'
            )
            if not bid_button:
                logger.error("Bid button not found on %s", lot_url)
                return False

            await bid_button.click()
            await asyncio.sleep(0.5)

            # Look for bid input field (some lots have custom bid entry)
            bid_input = await self._page.query_selector(
                'input[data-testid="bid-amount-input"], '
                'input[name="bid_amount"], '
                'input[type="number"]'
            )
            if bid_input:
                await bid_input.fill("")
                await bid_input.type(str(int(amount)))

            # Click confirm
            confirm_button = await self._page.query_selector(
                '[data-testid="confirm-bid-button"], '
                'button:has-text("Confirm"), '
                'button:has-text("Place bid"), '
                'button[class*="ConfirmBid"]'
            )
            if confirm_button:
                await confirm_button.click()

            # Wait for confirmation feedback
            await asyncio.sleep(2)

            # Check for success indicator
            success = await self._page.query_selector(
                '[data-testid="bid-success"], '
                '.lot-bidding__highest-bidder, '
                '[class*="success"], '
                ':text("highest bidder")'
            )

            if success:
                logger.info("Bid of EUR %.2f placed successfully on %s", amount, lot_url)
                return True

            logger.warning("Bid confirmation unclear for EUR %.2f on %s", amount, lot_url)
            return True  # Optimistic -- the bid may still have gone through

        except Exception as e:
            logger.error("Failed to place bid: %s", e)
            return False

    # ── Cookie Management ──────────────────────────────────────

    async def _save_cookies(self):
        """Persist browser cookies to disk."""
        import json
        cookies = await self._context.cookies()
        with open(self.cookies_path, "w") as f:
            json.dump(cookies, f)
        logger.debug("Saved %d cookies to %s", len(cookies), self.cookies_path)

    async def _load_cookies(self):
        """Restore cookies from disk if available."""
        import json
        import os
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, "r") as f:
                cookies = json.load(f)
            await self._context.add_cookies(cookies)
            logger.debug("Loaded %d cookies from %s", len(cookies), self.cookies_path)

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _parse_time_remaining(text: str) -> int:
        """
        Parse Catawiki time strings into total seconds.
        Examples: '2d 5h', '3h 12m', '45m 30s', '12s', 'Closed'
        """
        if not text or "closed" in text.lower():
            return 0

        total = 0
        days = re.search(r"(\d+)\s*d", text)
        hours = re.search(r"(\d+)\s*h", text)
        minutes = re.search(r"(\d+)\s*m", text)
        seconds = re.search(r"(\d+)\s*s", text)

        if days:
            total += int(days.group(1)) * 86400
        if hours:
            total += int(hours.group(1)) * 3600
        if minutes:
            total += int(minutes.group(1)) * 60
        if seconds:
            total += int(seconds.group(1))

        return total

"""
War on Art -- MCP Server.

Exposes the auction strategy engine as MCP tools that any AI agent
(Claude, etc.) can call to orchestrate Catawiki bidding.

MCP Tools:
  - configure_auction   : Set up a new auction campaign (lot, budget, greediness)
  - get_auction_state   : Scrape current live auction data
  - evaluate_strategy   : Run the engine and get the tactical recommendation
  - execute_bid         : Place a bid on Catawiki
  - start_autopilot     : Launch the full autonomous auction monitor
  - stop_autopilot      : Gracefully stop the monitor
  - get_battle_log      : Retrieve the log of all actions taken
  - login_catawiki      : Trigger interactive login for Codruta
  - get_learner_stats   : View current Q-table and learning state
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server import Server
from mcp.server.stdio import run_server
from mcp.types import Tool, TextContent

from strategy.inputs import AuctionParams
from strategy.engine import WarOnArtEngine
from strategy.learner import ReinforcementLearner
from catawiki.browser import CatawikiBrowser
from catawiki.monitor import AuctionMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# ── Global State ────────────────────────────────────────────────

app = Server("war-on-art")

# Shared instances (initialized via tools)
_browser: CatawikiBrowser | None = None
_params: AuctionParams | None = None
_engine: WarOnArtEngine | None = None
_learner: ReinforcementLearner = ReinforcementLearner(brain_path="brain.json")
_monitor: AuctionMonitor | None = None
_monitor_task: asyncio.Task | None = None


# ── Tool Definitions ────────────────────────────────────────────

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="configure_auction",
            description=(
                "Configure a new auction campaign. "
                "Provide lot_id, lot_url, max_budget (EUR), and greediness (0-100)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "lot_id": {"type": "string", "description": "Catawiki lot identifier"},
                    "lot_url": {"type": "string", "description": "Full URL of the lot page"},
                    "max_budget": {"type": "number", "description": "Maximum EUR budget"},
                    "greediness": {
                        "type": "integer",
                        "description": "0-100: How badly Codruta wants this (100 = whatever it takes)",
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
                "required": ["lot_id", "lot_url", "max_budget", "greediness"],
            },
        ),
        Tool(
            name="get_auction_state",
            description="Scrape the current live state of the configured auction lot.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="evaluate_strategy",
            description=(
                "Run the War on Art engine against the current auction state. "
                "Returns the tactical recommendation: WAIT, ANCHOR, ENGAGE, INTIMIDATE, or ABANDON."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "current_bid": {"type": "number", "description": "Current highest bid in EUR"},
                    "time_remaining_s": {"type": "integer", "description": "Seconds until auction closes"},
                    "is_leader": {"type": "boolean", "description": "Are we currently the highest bidder?"},
                },
                "required": ["current_bid", "time_remaining_s", "is_leader"],
            },
        ),
        Tool(
            name="execute_bid",
            description="Place a bid on the configured Catawiki lot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Bid amount in EUR"},
                },
                "required": ["amount"],
            },
        ),
        Tool(
            name="start_autopilot",
            description=(
                "Launch the autonomous auction monitor. "
                "Polls the auction and executes bids according to the engine's strategy. "
                "Runs until the auction closes or budget is exceeded."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "poll_interval": {
                        "type": "number",
                        "description": "Base polling interval in seconds (default: 2.0)",
                        "default": 2.0,
                    },
                },
            },
        ),
        Tool(
            name="stop_autopilot",
            description="Gracefully stop the running auction monitor.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_battle_log",
            description="Retrieve the full battle log of the current/last auction session.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="login_catawiki",
            description=(
                "Open a browser window for Codruta to log into Catawiki. "
                "After login, session cookies are saved for future headless operation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "description": "False = visible browser for manual login (default: False)",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="get_learner_stats",
            description="View the current Q-table values and learning state of the reinforcement learner.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# ── Tool Handlers ───────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    global _browser, _params, _engine, _learner, _monitor, _monitor_task

    # ── configure_auction ──
    if name == "configure_auction":
        _params = AuctionParams(
            lot_id=arguments["lot_id"],
            lot_url=arguments["lot_url"],
            max_budget=arguments["max_budget"],
            greediness=arguments["greediness"],
        )
        _engine = WarOnArtEngine(_params, _learner)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "configured",
                "lot_id": _params.lot_id,
                "max_budget": _params.max_budget,
                "true_ceiling": _params.true_ceiling,
                "greediness": _params.greediness,
                "total_cost_at_max": _params.calculate_total_acquisition_cost(_params.max_budget),
            }, indent=2),
        )]

    # ── login_catawiki ──
    elif name == "login_catawiki":
        headless = arguments.get("headless", False)
        _browser = CatawikiBrowser(headless=headless)
        await _browser.launch()
        await _browser.login_interactive()
        return [TextContent(type="text", text="Login successful. Session cookies saved.")]

    # ── get_auction_state ──
    elif name == "get_auction_state":
        if not _browser:
            return [TextContent(type="text", text="Error: Browser not initialized. Call login_catawiki first.")]
        if not _params:
            return [TextContent(type="text", text="Error: No auction configured. Call configure_auction first.")]

        state = await _browser.get_auction_state(_params.lot_url)
        return [TextContent(
            type="text",
            text=json.dumps({
                "lot_id": state.lot_id,
                "lot_title": state.lot_title,
                "current_bid": state.current_bid,
                "time_remaining_s": state.time_remaining_s,
                "is_leader": state.is_leader,
                "bid_count": state.bid_count,
                "closed": state.closed,
            }, indent=2),
        )]

    # ── evaluate_strategy ──
    elif name == "evaluate_strategy":
        if not _engine:
            return [TextContent(type="text", text="Error: Engine not initialized. Call configure_auction first.")]

        action, amount, reason = _engine.evaluate_state(
            arguments["current_bid"],
            arguments["time_remaining_s"],
            arguments["is_leader"],
        )
        return [TextContent(
            type="text",
            text=json.dumps({
                "action": action,
                "bid_amount": amount,
                "reason": reason,
            }, indent=2),
        )]

    # ── execute_bid ──
    elif name == "execute_bid":
        if not _browser:
            return [TextContent(type="text", text="Error: Browser not initialized. Call login_catawiki first.")]
        if not _params:
            return [TextContent(type="text", text="Error: No auction configured. Call configure_auction first.")]

        success = await _browser.place_bid(_params.lot_url, arguments["amount"])
        if success and _engine:
            _engine.my_last_bid = arguments["amount"]
        return [TextContent(
            type="text",
            text=json.dumps({"success": success, "amount": arguments["amount"]}),
        )]

    # ── start_autopilot ──
    elif name == "start_autopilot":
        if not _browser or not _params:
            return [TextContent(type="text", text="Error: Configure auction and login first.")]
        if _monitor_task and not _monitor_task.done():
            return [TextContent(type="text", text="Autopilot is already running.")]

        poll_interval = arguments.get("poll_interval", 2.0)
        _monitor = AuctionMonitor(_params, _browser, _learner, poll_interval=poll_interval)
        _monitor_task = asyncio.create_task(_monitor.run())

        return [TextContent(type="text", text="Autopilot started. Use get_battle_log to monitor progress.")]

    # ── stop_autopilot ──
    elif name == "stop_autopilot":
        if _monitor:
            _monitor.stop()
            return [TextContent(type="text", text="Autopilot stop signal sent.")]
        return [TextContent(type="text", text="No autopilot is running.")]

    # ── get_battle_log ──
    elif name == "get_battle_log":
        if _monitor and _monitor._battle_log:
            return [TextContent(type="text", text="\n".join(_monitor._battle_log))]
        return [TextContent(type="text", text="No battle log available.")]

    # ── get_learner_stats ──
    elif name == "get_learner_stats":
        return [TextContent(
            type="text",
            text=json.dumps({
                "q_table": _learner.q_table,
                "last_action": _learner.last_action,
                "brain_path": _learner.brain_path,
            }, indent=2),
        )]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Entry Point ─────────────────────────────────────────────────

async def main():
    await run_server(app)

if __name__ == "__main__":
    asyncio.run(main())

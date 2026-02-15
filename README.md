# The War on Art

*by Son Dzai*

> *"The supreme art of war is to subdue the enemy without fighting."*
> -- Sun Tzu, The Art of War

Inspired by Sun Tzu's brilliant writing *The Art of War*, this is its mirror image: **The War on Art**. Where the ancient strategist wrote about armies and terrain, Son Dzai -- a name forged from the same letters as its creator, Ozymandias -- applies those principles to a different battlefield: the final seconds of an online art auction.

**The War on Art** is an intelligent and strategic agent with a single intent: win every Catawiki auction where the human-in-the-loop bidder has mandated the agent to partake in.

The architecture separates the **Strategic Mind** from the **Mechanical Hand**. The mind is the decision engine -- a matrix of game theory, Go strategy (Sente and Gote -- initiative and response), and Q-learning reinforcement that decides *when* to strike, *how hard*, and *when to walk away*. The hand is the browser automation that reads the auction state and clicks the bid button when the mind commands it.

Between them sits a protocol: **Wait, Act, or Abandon.** The agent conceals its intent for days, observes the enemy's patterns, and strikes only in the Dead Zone -- the final 15 seconds where Catawiki's timer-reset mechanic turns the auction into a war of attrition. Jump-bids break psychological round-number barriers. The Ozymandias Offset ensures we never bid a round figure. And after every battle, win or lose, the agent's memory updates -- learning which tactics work for Codruta's style and adapting its strategy for the next fight.

The human stays in the loop. Codruta provides four inputs -- a lot URL, a budget in euros, a greediness factor from 0 to 100 (where 100 means "whatever it takes within budget"), and her login session. The agent handles the rest. When the greediness is low, it bids conservatively. When it's high, it deploys intimidation tactics. When the budget is exceeded, it retreats with discipline. No exceptions.

The reinforcement learning module (a Q-learning implementation) treats each auction as an episode, each bid as an action, and the outcome as a reward signal. Over time, the Q-table converges on the optimal balance between standard engagement and aggressive jump-bids -- the agent literally teaches itself to meet Codruta's demands better with every auction it fights.

The MCP server wraps the entire system as a set of tools that any AI agent -- Claude, or whatever comes next -- can call to orchestrate the bidding. Or Codruta can run the Jupyter notebook directly, watch the battle log scroll in real time, and pull the plug whenever she wants.

---

## How It Works

```
You (Codruta)                    The Program                         Catawiki
─────────────                    ───────────                         ────────
Lot URL         ──►
Max Budget (EUR) ──►  Strategic Mind (engine.py)
Greediness 0-100 ──►  decides: WAIT / ENGAGE /    ──► Browser places bid ──► Catawiki
                       INTIMIDATE / ABANDON
                                 ▲
                       Mechanical Hand (browser.py)
                       scrapes live auction state   ◄── current bid, time, leader
                                 ▲
                       Memory (learner.py)
                       gets smarter each auction
```

The engine runs a **polling loop**: every 1-2 seconds it reads the auction page, feeds the state into the decision matrix, and acts on the result. It stays silent during the opening days, may place one anchor bid in the last hour, and fights aggressively only in the final 15 seconds -- the "Dead Zone" -- where it forces Catawiki's 90-second timer reset to exhaust opponents.

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Desktop computer** (Windows, macOS, or Linux) -- the program controls a Chromium browser via [Playwright](https://playwright.dev/python/). This is a desktop application; it does not run on mobile.
- A **Catawiki account** with a registered payment method (required to bid).

### 1. Clone and install

```bash
git clone https://github.com/Ozymandias-vanMokum/son-dzai_the-war-on-art.git
cd son-dzai_the-war-on-art

pip install -r requirements.txt
playwright install chromium
```

The `playwright install chromium` step downloads the Chromium browser binary that the program uses to interact with Catawiki. This is a one-time download (~150 MB).

### 2. Run the program

Open the repo in **VS Code**, **Cursor**, or any editor with Jupyter support. Both VS Code and Cursor have built-in notebook rendering -- install the **Jupyter** extension if prompted.

Open `notebooks/war_room.ipynb`. Select a Python kernel (top right corner) that points to the environment where you installed the requirements. Run cells with **Shift+Enter**.

Alternatively, launch from the terminal:

```bash
jupyter notebook notebooks/war_room.ipynb
```

The notebook is divided into two sections:

| Section | Cells | What it does |
|---|---|---|
| **Simulation** (top half) | 1-7 | Test the strategy engine offline with mock scenarios. No browser, no Catawiki account needed. |
| **Live Auction** (bottom half) | 8-13 | Connect to a real Catawiki auction and run the full autonomous bidding loop. |

#### Running a live auction

**Step 1 -- Configure your bid** (Cell 9). Fill in four values:

```python
LOT_ID     = "12345"                                  # Catawiki lot number
LOT_URL    = "https://www.catawiki.com/l/12345"       # Full lot URL
BUDGET     = 500                                       # Maximum EUR you want to spend
GREEDINESS = 85                                        # 0-100 (see below)
```

| Greediness | Behavior |
|---|---|
| 0-40 | Conservative. Minimal bidding, standard increments only. |
| 41-70 | Moderate. Places an anchor bid in the last hour, standard counter-bids in the Dead Zone. |
| 71-100 | Aggressive. Uses jump-bids (double increments) to intimidate opponents in the final seconds. |

The program automatically calculates the **True Ceiling** (Ozymandias Offset): if your budget is a round number like EUR 500, it adds a ~2.2% buffer (EUR 511) to clear the psychological barriers where most human bidders stop. Total acquisition cost includes Catawiki's 9% fee + EUR 3 protection fee.

**Step 2 -- Log in to Catawiki** (Cell 10). Run this cell once. A **visible Chromium browser window** will open on your desktop showing the Catawiki login page. Log in manually with your email/password, Google, Facebook, or any method Catawiki supports -- including 2FA. You have 5 minutes. After login, your session cookies are saved to `catawiki_cookies.json` so future runs are headless (no visible browser).

**Step 3 -- Launch autopilot** (Cell 11). This starts the real-time auction loop. The notebook output shows a live battle log:

```
[14:32:01]  [   DEPLOY] War Room active for lot 12345
[14:32:01]  [    INTEL] Budget: EUR 500 | True Ceiling: EUR 511.0 | Greediness: 85%
[14:32:03]  [     WAIT] EUR 0.00 | Too early. Concealing intent. | Bid: EUR 180 | Time: 7200s
[14:59:45]  [   ANCHOR] EUR 190.00 | Setting Anchor Bid. | Bid: EUR 180 | Time: 900s
[15:00:48]  [     WAIT] EUR 0.00 | Letting the opponent sweat (Gote). | Time: 42s
[15:01:05]  [INTIMIDATE] EUR 240.00 | Executing Rapid Jump-Bid. | Time: 9s
[15:01:08]  [ EXECUTED] Bid EUR 240.00 placed (INTIMIDATE)
[15:02:35]  [      END] Auction closed. Final bid: EUR 240
[15:02:36]  [  DEBRIEF] Won: True | Final: EUR 240 | Ratio: 48.00% | Brain updated.
```

**Step 4 -- Review results** (Cells 12-13). Print the full battle log and updated learner statistics, then close the browser.

### 3. Run the program (CLI Script)

If you prefer the terminal over notebooks:

```bash
python run_auction.py
```

The script prompts you for the lot URL, budget, and greediness level, shows a configuration summary, and then launches the full auction loop. Press `Ctrl+C` to abort at any time.

### 4. Run the program (MCP Server -- for AI agents)

If you want Claude or another AI agent to orchestrate the bidding:

```bash
python mcp_server/server.py
```

Or add this to your Claude Code MCP config (`~/.claude/claude_mcp_config.json`):

```json
{
  "mcpServers": {
    "war-on-art": {
      "command": "python",
      "args": ["mcp_server/server.py"],
      "env": {}
    }
  }
}
```

The MCP server exposes 9 tools:

| Tool | Purpose |
|---|---|
| `login_catawiki` | Open browser for manual login (run once) |
| `configure_auction` | Set lot URL, budget, greediness |
| `get_auction_state` | Scrape live auction data |
| `evaluate_strategy` | Get tactical recommendation without bidding |
| `execute_bid` | Place a single bid |
| `start_autopilot` | Launch the autonomous auction loop |
| `stop_autopilot` | Gracefully stop the loop |
| `get_battle_log` | Retrieve all actions taken |
| `get_learner_stats` | View Q-table and learning state |

---

## How to Abort

| Situation | Action |
|---|---|
| **Notebook running in VS Code / Cursor** | Click the **Interrupt** button (square icon) next to the running cell, or press `Ctrl+C` in the integrated terminal. The monitor catches the cancellation and logs `ABORT`. |
| **Notebook running in browser (Jupyter)** | Click the **Stop** button (square icon) in the toolbar, or press `I I` (press I twice) in command mode. |
| **MCP autopilot running** | Call the `stop_autopilot` tool. The monitor sets `_running = False` and the polling loop exits on the next tick. |
| **Budget exceeded** | Automatic. The engine returns `ABANDON` and the loop stops itself. No bid is placed. |
| **Browser window stuck** | Close the Chromium window manually. The monitor will catch the exception and stop. |
| **Everything is broken** | `Ctrl+C` in the terminal kills the Python process immediately. No bid can be placed after the process dies. Your Catawiki account is unaffected. |

---

## Browser and Platform Details

- **Browser**: Chromium, downloaded and managed by Playwright. You do not need Chrome, Firefox, or any other browser installed.
- **Platform**: Desktop only -- Windows, macOS, Linux. Not designed for mobile.
- **First login**: Opens a visible browser window on your desktop. You interact with it directly (click, type, 2FA).
- **Subsequent runs**: Fully headless (no visible window). The saved cookies maintain your session.
- **Cookie expiry**: If your session expires, re-run the login cell. Catawiki sessions typically last several days.

---

## Self-Tutoring & Reinforcement Learning

After each auction, the engine feeds the outcome back to the learner:

- **Won cheaply** (< 60% of budget): high reward, Q-values for the actions used go up
- **Won at fair price** (60-80%): moderate reward
- **Won but overpaid** (> 95%): small penalty even on a win
- **Lost**: negative reward

Over time, the Q-table shifts to favor the action (ENGAGE vs INTIMIDATE) that produces better outcomes for Codruta's bidding style. The exploration rate (epsilon) starts at 30% and decays to 5% as experience grows, so the system always keeps a small chance of trying the less-favored tactic.

All auction history is persisted to `auction_history.json` with timestamps, actions taken, and Q-table snapshots -- building a dataset for deeper analysis.

Run the **50-Auction Simulation** cell in the notebook to see how Q-values evolve over time with matplotlib charts.

---

## Project Structure

```
son-dzai_the-war-on-art/
|
|-- strategy/                    # The Strategic Mind
|   |-- inputs.py                # AuctionParams, Ozymandias Offset, fee calculations
|   |-- engine.py                # Decision matrix: WAIT / ANCHOR / ENGAGE / INTIMIDATE / ABANDON
|   |-- learner.py               # Q-learning with epsilon-greedy exploration and auction history
|
|-- catawiki/                    # The Mechanical Hand
|   |-- browser.py               # Playwright: login, scrape auction state, place bids
|   |-- monitor.py               # Real-time polling loop, adaptive timing, battle log
|
|-- mcp_server/                  # AI Agent Interface
|   |-- server.py                # 9 MCP tools for Claude / AI orchestration
|   |-- claude_mcp_config.json   # Drop-in config for Claude Code
|
|-- notebooks/
|   |-- war_room.ipynb           # Simulation + Live Auction Control Panel
|
|-- run_auction.py               # CLI entry point (interactive terminal alternative)
|-- requirements.txt             # numpy, pandas, playwright, mcp, matplotlib
|
|-- (runtime, gitignored)
|   |-- brain.json               # Persisted Q-table (created after first auction)
|   |-- auction_history.json     # Full auction records (created after first auction)
|   |-- catawiki_cookies.json    # Session cookies (created after first login)
```

---

## License

See [LICENSE](LICENSE).

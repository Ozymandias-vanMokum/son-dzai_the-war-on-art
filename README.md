# The War On Art - Catawiki Auction Bidding Automation

<p align="center">
  <em>An intelligent, strategic auction bidding system inspired by Sun Tzu's Art of War</em>
</p>

---

## 🎯 Overview

**The War On Art** is an autonomous bidding agent that participates in [Catawiki](https://www.catawiki.com) auctions on your behalf. Using strategic timing, psychological pricing tactics, and reinforcement learning, it executes sophisticated bidding strategies to help you win auctions while minimizing costs.

The system monitors live auctions, analyzes bidding patterns, and places bids at optimal moments—particularly in the crucial final seconds of an auction.

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [How to Run the Program](#-how-to-run-the-program)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Configuration & Input Parameters](#-configuration--input-parameters)
- [Usage Examples](#-usage-examples)
- [How to Stop/Abort](#-how-to-stopabort)
- [Browser Requirements](#-browser-requirements)
- [Project Structure](#-project-structure)
- [Strategy & Features](#-strategy--features)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Ozymandias-vanMokum/son-dzai_the-war-on-art.git
cd son-dzai_the-war-on-art

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Create and run a simple bidding script
python3 -c "import asyncio; from run_auction import main; asyncio.run(main())"
```

---

## 🎮 How to Run the Program

### Method 1: Interactive Python Script (Recommended for Beginners)

The easiest way to run The War On Art is through an interactive Python script that prompts you for all required parameters.

1. **Create a run file** (`run_auction.py`):

```python
import asyncio
from catawiki.browser import CatawikiBrowser
from catawiki.monitor import AuctionMonitor
from strategy.inputs import AuctionParams
from strategy.learner import ReinforcementLearner

async def main():
    print("=" * 60)
    print("THE WAR ON ART - Catawiki Auction Bidding System")
    print("=" * 60)
    print()
    
    # Prompt for auction parameters
    lot_url = input("Enter the Catawiki lot URL: ").strip()
    lot_id = lot_url.rstrip("/").split("/")[-1]
    
    max_budget = float(input("Enter your maximum budget (EUR): "))
    greediness = int(input("Enter greediness level (0-100, where 100 = 'must win'): "))
    
    # Confirm settings
    print("\n" + "=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Lot ID: {lot_id}")
    print(f"Lot URL: {lot_url}")
    print(f"Maximum Budget: €{max_budget}")
    print(f"Greediness Level: {greediness}%")
    
    params = AuctionParams(
        lot_id=lot_id,
        lot_url=lot_url,
        max_budget=max_budget,
        greediness=greediness
    )
    print(f"True Ceiling (with fees): €{params.true_ceiling:.2f}")
    print("=" * 60)
    
    confirm = input("\nProceed with these settings? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Aborted.")
        return
    
    # Initialize components
    browser = CatawikiBrowser(headless=False)  # Visible browser
    learner = ReinforcementLearner()
    
    try:
        # Launch browser and login
        print("\n🚀 Launching browser...")
        await browser.launch()
        
        # Check if already logged in
        is_logged_in = await browser.is_logged_in()
        if not is_logged_in:
            print("\n🔐 Please log in to Catawiki in the browser window...")
            await browser.login_interactive()
        else:
            print("✅ Already logged in (using saved session)")
        
        # Start the auction monitor
        print("\n⚔️  Starting auction monitor...")
        print("📊 The system will now monitor the auction and bid strategically.")
        print("💡 Press Ctrl+C to stop at any time.")
        print()
        
        monitor = AuctionMonitor(params, browser, learner, poll_interval=2.0)
        battle_log = await monitor.run()
        
        # Display results
        print("\n" + "=" * 60)
        print("BATTLE REPORT")
        print("=" * 60)
        for entry in battle_log:
            print(entry)
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted. Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await browser.close()
        print("\n✅ Browser closed. Session complete.")

if __name__ == "__main__":
    asyncio.run(main())
```

2. **Run the script**:

```bash
python3 run_auction.py
```

3. **Follow the prompts**:
   - Enter the Catawiki auction URL (e.g., `https://www.catawiki.com/l/12345678-vintage-artwork`)
   - Enter your maximum budget in EUR
   - Enter your greediness level (0-100)
   - The program will open a browser window for you to log in to Catawiki
   - Once logged in, the automated bidding begins

### Method 2: Jupyter Notebook (For Testing & Simulation)

If you want to test the strategy without connecting to real auctions:

```bash
jupyter notebook notebooks/war_room.ipynb
```

This allows you to simulate different scenarios and understand the bidding logic.

### Method 3: MCP Server (For AI Agent Integration)

For advanced users who want to integrate with AI agents like Claude:

```bash
python3 mcp_server/server.py
```

Then use MCP tools to control the auction bidding programmatically.

---

## 💻 System Requirements

### Platform
- **Desktop Only** (not mobile)
- **Operating Systems**: Windows, macOS, or Linux
- Python 3.8 or higher

### Browser
- **Chromium-based browser** (automatically managed by Playwright)
- The system uses a **desktop browser** (not mobile browser)
- Can run in **headless mode** (no visible window) or **headed mode** (visible browser window)
  - **Headed mode recommended** for first-time setup to handle login
  - **Headless mode** can be used after cookies are saved

### Network
- Stable internet connection required
- Low latency preferred (especially for final seconds of auction)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ozymandias-vanMokum/son-dzai_the-war-on-art.git
cd son-dzai_the-war-on-art
```

### 2. Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `playwright` - Browser automation
- `numpy` & `pandas` - Data processing
- `matplotlib` - Visualization (for notebooks)
- `mcp` - MCP server framework

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright will use for automation.

---

## ⚙️ Configuration & Input Parameters

When running the program, you'll be asked to provide these parameters:

### Required Input Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| **Lot URL** | String | Full URL of the Catawiki auction lot | `https://www.catawiki.com/l/12345678-vintage-artwork` |
| **Maximum Budget** | Float | Your maximum spending limit in EUR | `500.0` |
| **Greediness** | Integer (0-100) | How aggressively to bid<br>• 0-30: Conservative<br>• 30-70: Moderate<br>• 70-100: Aggressive | `85` |

### What These Parameters Control

#### Maximum Budget (€)
- The absolute maximum you're willing to spend
- The system adds a small "Ozymandias Offset" to overcome psychological price barriers
- **Important**: Total cost includes Catawiki's fees (9% + €3)

#### Greediness Level (0-100)
- **Low (0-40)**: Patient bidding, minimal early activity
- **Medium (40-70)**: Balanced approach, occasional anchor bids
- **High (70-100)**: Aggressive tactics including "jump bids" to intimidate opponents

### Automatic Calculations

The system automatically calculates:
- **True Ceiling**: Your max budget + Ozymandias offset (typically +2.2%)
- **Total Acquisition Cost**: Bid + 9% fee + €3 protection fee
- **Bid Increments**: Following Catawiki's official increment rules

---

## 📚 Usage Examples

### Example 1: Conservative Bidding

```python
# Target: €200 painting
# Strategy: Wait until final minutes, only bid if necessary
lot_url = "https://www.catawiki.com/l/87654321-oil-painting"
max_budget = 200.0
greediness = 30  # Conservative
```

### Example 2: Aggressive Must-Win

```python
# Target: €500 collectible
# Strategy: Jump bids, intimidation tactics
lot_url = "https://www.catawiki.com/l/12345678-rare-collectible"
max_budget = 500.0
greediness = 90  # Highly aggressive
```

### Example 3: Moderate Strategy

```python
# Target: €350 artwork
# Strategy: Balanced, one anchor bid early, active in final minute
lot_url = "https://www.catawiki.com/l/45678912-modern-art"
max_budget = 350.0
greediness = 55  # Moderate
```

---

## ⛔ How to Stop/Abort

### During Active Bidding

The program can be stopped safely at any point:

#### Method 1: Keyboard Interrupt (Recommended)
```
Press Ctrl+C (or Cmd+C on Mac)
```
This triggers a graceful shutdown that:
- Stops the monitoring loop
- Saves any learning data
- Closes the browser properly

#### Method 2: Close the Terminal
Simply close the terminal window running the script. The browser will close automatically.

#### Method 3: Kill the Process
```bash
# Find the process ID
ps aux | grep python

# Kill it
kill <PID>
```

### Emergency Stop
If the program becomes unresponsive:
1. Close the browser window manually
2. Use `Ctrl+C` multiple times
3. Force-kill the Python process

### What Happens When You Stop?
- All pending bids in the queue are cancelled
- Browser session is saved (cookies remain for next run)
- Any bids already placed on Catawiki **cannot be undone**
- Learning data is persisted to disk

---

## 🌐 Browser Requirements

### Browser Type
- **Chromium** (automatically installed via Playwright)
- Not compatible with mobile browsers
- Desktop-only operation

### Operating Modes

#### 1. Headed Mode (Visible Browser)
```python
browser = CatawikiBrowser(headless=False)
```
- **Recommended for**: First-time setup, debugging
- Browser window is visible
- You can see what the automation is doing
- Required for interactive login

#### 2. Headless Mode (Invisible)
```python
browser = CatawikiBrowser(headless=True)
```
- **Recommended for**: Subsequent runs after login
- No visible browser window
- Faster and uses less resources
- Requires saved authentication cookies

### Authentication & Cookies
- First run: Browser opens visibly for you to log in
- Cookies are saved to `catawiki_cookies.json`
- Future runs: Automatically logged in (headless mode possible)
- Session persistence: Cookies remain valid for weeks

### Browser Location
The browser is managed by Playwright and installed at:
- **Linux**: `~/.cache/ms-playwright/chromium-*/`
- **macOS**: `~/Library/Caches/ms-playwright/chromium-*/`
- **Windows**: `%USERPROFILE%\AppData\Local\ms-playwright\chromium-*\`

---

## 📁 Project Structure

```
son-dzai_the-war-on-art/
├── catawiki/                   # Browser automation & monitoring
│   ├── browser.py             # Playwright-based Catawiki client
│   └── monitor.py             # Auction monitoring loop
├── strategy/                   # Bidding strategy & AI
│   ├── engine.py              # Core decision-making engine
│   ├── inputs.py              # Input parameters & calculations
│   └── learner.py             # Reinforcement learning module
├── mcp_server/                # MCP server for AI agent integration
│   └── server.py              # MCP tool definitions
├── notebooks/                  # Jupyter notebooks for testing
│   └── war_room.ipynb         # Strategy simulation notebook
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore                # Git ignore rules
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **browser.py** | Handles all Catawiki interactions via Playwright |
| **monitor.py** | Main control loop that monitors and executes bids |
| **engine.py** | Strategic decision-making based on Sun Tzu principles |
| **learner.py** | Q-learning agent that improves over time |
| **inputs.py** | Parameter validation and cost calculations |

---

## 🎯 Strategy & Features

### The War On Art Philosophy

The bidding strategy is inspired by Sun Tzu's *The Art of War*:

1. **The Opening (Days 1-6)**: *"Appear weak when you are strong"*
   - No bidding activity
   - Conceals your intent

2. **The Skirmish (Last Hour)**: *"Let your plans be dark and impenetrable"*
   - Single anchor bid if greediness > 40%
   - Minimal activity to avoid escalation

3. **The Battlefield (Last 60 Seconds)**: *"In the midst of chaos, there is opportunity"*
   - Active monitoring every 1-2 seconds
   - Strategic engagement when not leading

4. **The Dead Zone (Last 15 Seconds)**: *"Speed is the essence of war"*
   - Rapid counter-bidding
   - Jump bids to intimidate (if greediness > 70%)

### Key Features

- **Psychological Pricing**: Adds small offset to break round-number barriers
- **Adaptive Polling**: Faster checking as auction end approaches
- **Jump Bidding**: Skip an increment to demoralize opponents
- **Reinforcement Learning**: Improves strategy based on past auction results
- **Session Persistence**: Saves login state between runs
- **Real-time Monitoring**: Live auction state tracking

### Reinforcement Learning

The system learns from each auction:
- Tracks which tactics lead to wins
- Optimizes bid timing
- Adjusts aggression based on success rate
- Stores complete auction history for analysis

Learning data is saved in:
- `brain.json` - Q-table weights
- `auction_history.json` - Complete auction records

---

## 🔧 Troubleshooting

### Common Issues

#### "Browser not installed"
```bash
playwright install chromium
```

#### "Login failed" or "Session expired"
Delete the cookie file and log in again:
```bash
rm catawiki_cookies.json
python3 run_auction.py
```

#### "Bid button not found"
Catawiki may have changed their HTML structure. Check for updates or report an issue.

#### Program hangs during bidding
- Press `Ctrl+C` to stop gracefully
- Check your internet connection
- Ensure Catawiki website is accessible

#### Python version issues
Ensure Python 3.8 or higher:
```bash
python3 --version
```

### Debug Mode

Run with verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

If you encounter issues:
1. Check the [Issues](https://github.com/Ozymandias-vanMokum/son-dzai_the-war-on-art/issues) page
2. Review the troubleshooting section above
3. Enable debug logging and review output
4. Open a new issue with details about your problem

---

## ⚖️ Legal & Ethical Considerations

- **Terms of Service**: Ensure automated bidding complies with Catawiki's ToS
- **Responsible Use**: This tool is for personal use only
- **No Warranty**: Use at your own risk
- **Auction Integrity**: The system is designed for fair competition, not manipulation

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by Sun Tzu's *The Art of War*
- Built with [Playwright](https://playwright.dev/) for browser automation
- Reinforcement learning concepts from modern AI research

---

<p align="center">
  <strong>Happy Bidding! May you win with wisdom and restraint.</strong>
</p>
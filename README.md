# The War on Art - Catawiki Auction MCP Server

An MCP (Model Context Protocol) server for automated auction bidding on Catawiki, implementing "The War on Art" strategy - a Go-inspired approach to auction bidding that prioritizes maintaining **Sente** (initiative) over rigid chess-like algorithms.

## Philosophy

Traditional auction strategies are like Chess: rigid, deterministic, following strict rules. **The War on Art** is like Go: fluid, territory-focused, understanding the value of maintaining initiative.

### Key Concepts

- **Sente (先手)**: Maintaining the initiative in bidding. Being the current high bidder gives you control.
- **Territory Control**: Understanding the value landscape and controlling strategic price points.
- **Fluid Adaptation**: Responding dynamically to opponent moves rather than following fixed rules.
- **Strategic Timing**: Knowing when to fight, when to hold, and when to make the decisive move.

## Features

- 🎯 **Intelligent Bidding Strategy**: Go-inspired algorithm that adapts to auction dynamics
- 🤖 **Browser Automation**: Full Playwright-based automation for Catawiki
- 🎮 **MCP Server**: Standardized interface for AI assistants (Claude, etc.)
- 📊 **Real-time Monitoring**: Track auction state and competitor behavior
- ⚡ **Sniping Support**: Last-second bidding strategies
- 🔄 **Adaptive Learning**: Strategy improves based on auction outcomes

## Installation

```bash
npm install
npm run build
```

## Usage

### As MCP Server

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "war-on-art-auction": {
      "command": "node",
      "args": ["/path/to/son-dzai_the-war-on-art/dist/index.js"]
    }
  }
}
```

### Available Tools

#### 1. `initialize_auction`
Start a new auction session with strategy configuration.

```typescript
{
  auctionId: "unique-id",
  auctionUrl: "https://www.catawiki.com/l/...",
  maxBid: 1000,
  estimatedValue: 1200,
  aggressiveness: 0.7,  // 0-1
  sniping: false,
  snipeWindow: 10,      // seconds
  headless: true
}
```

#### 2. `check_auction_state`
Get current auction state and strategic recommendation.

```typescript
{
  auctionId: "unique-id"
}
```

Returns:
- Current price and time remaining
- Competitor count and bid history
- Strategic recommendation (should bid, amount, reasoning)
- Confidence level and strategy type

#### 3. `place_bid`
Execute a bid on the platform.

```typescript
{
  auctionId: "unique-id",
  amount: 500,          // optional, uses strategy recommendation if not provided
  force: false          // override strategy recommendation
}
```

#### 4. `auto_bid`
Automatically monitor and bid according to strategy.

```typescript
{
  auctionId: "unique-id",
  checkInterval: 30,    // seconds between checks
  duration: 3600        // optional, seconds to run
}
```

#### 5. `close_auction`
Clean up auction session.

```typescript
{
  auctionId: "unique-id",
  feedback: {           // optional, for strategy improvement
    won: true,
    finalPrice: 950,
    efficiency: 0.92
  }
}
```

#### 6. `screenshot`
Capture current auction page.

```typescript
{
  auctionId: "unique-id",
  path: "./screenshot.png"
}
```

## Strategy Explained

The War on Art strategy operates in three phases:

### Early Game (>5 min remaining)
- **Goal**: Establish presence without overcommitting
- **Action**: Only bid if price is very attractive (<60% of estimated value)
- **Logic**: Don't fight early, save resources for critical moments

### Mid Game (1-5 min remaining)
- **Goal**: Control Sente (initiative)
- **Action**: Fight for high bid position if strategically valuable
- **Logic**: Being the current winner discourages competitors and gives control

### End Game (<1 min remaining)
- **Goal**: Secure victory
- **Action**: Decisive bids up to maximum budget
- **Logic**: No holding back, commit fully if value is there

### Sniping Mode
- **Goal**: Win by surprising opponents at the last second
- **Action**: Place maximum strategic bid in final seconds
- **Logic**: Prevents counter-bids, maintains ultimate Sente

## Configuration

Strategy can be tuned via these parameters:

- **maxBid**: Absolute maximum you'll pay
- **estimatedValue**: Your valuation of the item
- **aggressiveness** (0-1): How hard to fight for Sente
  - 0.3: Passive, only bid when clearly valuable
  - 0.7: Balanced, normal competition
  - 1.0: Aggressive, fight hard for every position
- **sniping**: Enable last-second bidding
- **snipeWindow**: Seconds before end to place snipe

## Example Workflow

```javascript
// 1. Initialize auction
await call_tool('initialize_auction', {
  auctionId: 'vintage-watch-001',
  auctionUrl: 'https://www.catawiki.com/l/12345678',
  maxBid: 500,
  estimatedValue: 600,
  aggressiveness: 0.8,
  sniping: true,
  snipeWindow: 15
});

// 2. Check state and get recommendation
const state = await call_tool('check_auction_state', {
  auctionId: 'vintage-watch-001'
});
// Returns: shouldBid: true, amount: 350, reasoning: "Mid game - taking Sente"

// 3. Place recommended bid
await call_tool('place_bid', {
  auctionId: 'vintage-watch-001'
  // Uses strategy recommendation
});

// 4. Or run fully automated
await call_tool('auto_bid', {
  auctionId: 'vintage-watch-001',
  checkInterval: 20
});

// 5. Close when done
await call_tool('close_auction', {
  auctionId: 'vintage-watch-001',
  feedback: {
    won: true,
    finalPrice: 475,
    efficiency: 0.95  // (maxBid - finalPrice) / maxBid
  }
});
```

## Browser Setup

The system uses Playwright for browser automation. For persistent login:

1. First run with `headless: false`
2. Manually log in to Catawiki
3. Provide `userDataDir` to save session
4. Subsequent runs will use saved session

## Security Notes

- Never commit credentials to source code
- Use environment variables for sensitive data
- The browser automation respects Catawiki's terms of service
- Consider rate limiting to avoid detection

## Development

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Development mode (watch)
npm run dev

# Run server
npm start
```

## Architecture

```
src/
├── index.ts       # MCP server implementation
├── strategy.ts    # The War on Art bidding logic
└── catawiki.ts    # Browser automation for Catawiki
```

## License

MIT License - see LICENSE file

## Disclaimer

This tool is for educational purposes. Always comply with Catawiki's terms of service and applicable laws. Automated bidding may be against platform policies. Use responsibly.

---

*"In Go, the player who maintains Sente controls the game. In auctions, the bidder who maintains initiative controls the outcome."*
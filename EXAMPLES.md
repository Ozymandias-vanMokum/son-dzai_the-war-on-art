# Example Usage of War on Art MCP Server

This document provides practical examples of how to use the War on Art MCP server for auction bidding.

## Quick Start

### 1. Installation
```bash
cd /path/to/son-dzai_the-war-on-art
npm install
npm run build
```

### 2. Configure Your MCP Client

For **Claude Desktop**, edit your config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "war-on-art-auction": {
      "command": "node",
      "args": ["/absolute/path/to/son-dzai_the-war-on-art/dist/index.js"]
    }
  }
}
```

### 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop to load the MCP server.

## Example Conversations with Claude

### Example 1: Monitor and Manual Bid

**You**: "I'm interested in a vintage Rolex on Catawiki. Can you help me monitor the auction and suggest when to bid?"

**Claude**: "I'll help you set up auction monitoring with The War on Art strategy. Let me initialize the auction session."

Then Claude will use:
```
initialize_auction({
  auctionId: "rolex-vintage-2024",
  auctionUrl: "https://www.catawiki.com/l/12345678",
  maxBid: 5000,
  estimatedValue: 6000,
  aggressiveness: 0.7,
  headless: false
})
```

**You**: "What's the current state?"

**Claude**: "Let me check..."
```
check_auction_state({
  auctionId: "rolex-vintage-2024"
})
```

**Claude**: "Current price is €3,200 with 8 minutes remaining. The strategy recommends bidding €3,360 to maintain Sente (initiative). Confidence: 75%. Shall I place this bid?"

**You**: "Yes, go ahead"

**Claude**: 
```
place_bid({
  auctionId: "rolex-vintage-2024"
})
```

### Example 2: Fully Automated Bidding

**You**: "I found a painting I really want on Catawiki for up to €2,000. Can you handle the bidding automatically? Use a conservative strategy."

**Claude**: "I'll set up automated bidding with a conservative approach using sniping strategy..."

```
initialize_auction({
  auctionId: "painting-2024",
  auctionUrl: "https://www.catawiki.com/l/87654321",
  maxBid: 2000,
  estimatedValue: 2500,
  aggressiveness: 0.4,
  sniping: true,
  snipeWindow: 15
})

auto_bid({
  auctionId: "painting-2024",
  checkInterval: 30
})
```

**Claude**: "I'm now monitoring the auction and will bid automatically according to the strategy. The system will maintain Sente when valuable and execute a snipe bid in the final 15 seconds if needed."

### Example 3: Check Multiple Auctions

**You**: "I'm watching three different watches on Catawiki. Can you help me monitor all of them?"

**Claude**: "I'll set up monitoring for all three auctions with different IDs..."

```
// Watch 1
initialize_auction({
  auctionId: "watch-omega-001",
  auctionUrl: "https://www.catawiki.com/l/11111111",
  maxBid: 3000,
  estimatedValue: 3500,
  aggressiveness: 0.6
})

// Watch 2  
initialize_auction({
  auctionId: "watch-rolex-002",
  auctionUrl: "https://www.catawiki.com/l/22222222",
  maxBid: 8000,
  estimatedValue: 10000,
  aggressiveness: 0.8
})

// Watch 3
initialize_auction({
  auctionId: "watch-patek-003",
  auctionUrl: "https://www.catawiki.com/l/33333333",
  maxBid: 15000,
  estimatedValue: 18000,
  aggressiveness: 0.7
})
```

Then periodically:
```
check_auction_state({ auctionId: "watch-omega-001" })
check_auction_state({ auctionId: "watch-rolex-002" })
check_auction_state({ auctionId: "watch-patek-003" })
```

### Example 4: Aggressive Must-Win Strategy

**You**: "There's a rare book I absolutely must have. Maximum budget is €5,000. Be aggressive."

**Claude**: "I'll configure an aggressive strategy that fights hard for Sente..."

```
initialize_auction({
  auctionId: "rare-book-001",
  auctionUrl: "https://www.catawiki.com/l/99999999",
  maxBid: 5000,
  estimatedValue: 6000,
  aggressiveness: 0.95,
  sniping: false  // Don't risk losing with snipe
})

auto_bid({
  auctionId: "rare-book-001",
  checkInterval: 20  // Check frequently
})
```

### Example 5: Take Screenshot

**You**: "Can you show me what the auction looks like right now?"

**Claude**: "I'll take a screenshot..."

```
screenshot({
  auctionId: "watch-omega-001",
  path: "./auction_screenshot.png"
})
```

### Example 6: Close and Learn

**You**: "The auction ended. I won at €4,200 and my max was €5,000."

**Claude**: "Congratulations! Let me close the session and update the strategy with this result..."

```
close_auction({
  auctionId: "watch-omega-001",
  feedback: {
    won: true,
    finalPrice: 4200,
    efficiency: 0.84  // (5000-4200)/5000 = good efficiency
  }
})
```

**Claude**: "Session closed. The strategy learned from this auction and adjusted its aggressiveness for future auctions based on your efficient win."

## Advanced Usage Patterns

### Pattern 1: Morning Scout, Evening Snipe

**Morning (auction starts)**:
```javascript
// Just initialize and check once
initialize_auction({...})
check_auction_state({...})
close_auction({...})
```

**Evening (auction ending)**:
```javascript
// Re-initialize and auto-bid with sniping
initialize_auction({
  ...
  sniping: true,
  snipeWindow: 10
})
auto_bid({
  checkInterval: 20,
  duration: 600  // Monitor last 10 minutes only
})
```

### Pattern 2: Price Watching

Use for items you might want if price stays low:

```javascript
initialize_auction({
  maxBid: 500,
  estimatedValue: 1000,
  aggressiveness: 0.2  // Very passive
})

// Check periodically
// Strategy will only bid if price is excellent (<50% of value)
check_auction_state({...})
```

### Pattern 3: Competitive Adjustment

Start balanced, adjust if losing:

```javascript
// Initial setup
initialize_auction({
  aggressiveness: 0.6
})

// If losing repeatedly
close_auction({...})
initialize_auction({
  aggressiveness: 0.85  // More aggressive
})
```

## Tips for Working with Claude

1. **Be specific about your goals**: "I want to win this auction" vs "I'm casually interested"

2. **Provide your valuation**: Always tell Claude your maximum and your estimated value

3. **Set the right aggressiveness**:
   - 0.2-0.4: Bargain hunting, only interested if cheap
   - 0.5-0.7: Normal competitive bidding
   - 0.8-1.0: Must win, fight hard

4. **Trust the strategy**: The War on Art logic is designed to be smart about when to fight

5. **Use sniping wisely**: Great for avoiding bidding wars, but risky if you have network issues

6. **Monitor first time**: For your first auction, watch manually to see how it works

7. **Provide feedback**: After auctions, tell Claude the results so the strategy can learn

## Troubleshooting with Claude

**Issue**: "Claude says browser not initialized"
**Solution**: "Please initialize the auction first with initialize_auction"

**Issue**: "Bid wasn't placed"
**Solution**: "Can you take a screenshot so I can see what's happening?"

**Issue**: "Strategy is too passive"
**Solution**: "Close this session and reinitialize with higher aggressiveness (try 0.85)"

**Issue**: "Lost the auction in final seconds"
**Solution**: "Next time, let's use sniping with a 20-second window for more safety"

## Safety Checklist

Before running automated bidding:

- [ ] Verified auction URL is correct
- [ ] Set maxBid to absolute maximum you'll pay
- [ ] Estimated value reflects true worth to you
- [ ] Chosen appropriate aggressiveness level
- [ ] Decided on sniping strategy
- [ ] Have stable internet connection
- [ ] Logged into Catawiki (if headless: false on first run)
- [ ] Understood the strategy will bid real money

## Legal and Ethical Notes

- Comply with Catawiki's terms of service
- Automated bidding may violate platform policies
- Use responsibly and at your own risk
- This is an educational tool
- Always verify bids before placing

---

Happy bidding! May Sente be with you. 🎯

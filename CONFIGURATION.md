# Example MCP Configuration

## For Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "war-on-art-auction": {
      "command": "node",
      "args": [
        "/absolute/path/to/son-dzai_the-war-on-art/dist/index.js"
      ]
    }
  }
}
```

## For Other MCP Clients

The server uses stdio transport and follows MCP protocol. Connect via:

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: 'node',
  args: ['/path/to/dist/index.js']
});

const client = new Client({
  name: 'my-auction-client',
  version: '1.0.0'
}, {
  capabilities: {}
});

await client.connect(transport);
```

## Environment Variables

Create a `.env` file for configuration:

```bash
# Browser settings
HEADLESS=true
USER_DATA_DIR=/path/to/browser/profile

# Default strategy settings
DEFAULT_AGGRESSIVENESS=0.7
DEFAULT_SNIPE_WINDOW=10

# Logging
LOG_LEVEL=info
```

## Usage Examples

### Example 1: Manual Monitoring

```bash
# In Claude or your MCP client, use the tools:

1. initialize_auction
   - auctionId: "rolex-1960"
   - auctionUrl: "https://www.catawiki.com/l/12345678"
   - maxBid: 5000
   - estimatedValue: 6000
   - aggressiveness: 0.6
   - headless: false  # Watch what's happening

2. check_auction_state
   - auctionId: "rolex-1960"
   # Returns current state and recommendation

3. place_bid (if recommended)
   - auctionId: "rolex-1960"
   # Uses strategy recommendation

4. Repeat steps 2-3 periodically

5. close_auction
   - auctionId: "rolex-1960"
```

### Example 2: Fully Automated

```bash
1. initialize_auction
   - auctionId: "painting-abc"
   - auctionUrl: "https://www.catawiki.com/l/87654321"
   - maxBid: 2000
   - estimatedValue: 2500
   - aggressiveness: 0.8
   - sniping: true
   - snipeWindow: 15

2. auto_bid
   - auctionId: "painting-abc"
   - checkInterval: 30
   # Let it run automatically

3. close_auction when done
```

### Example 3: Conservative Sniping

```bash
# Good for high-value items where you want to avoid bidding wars

1. initialize_auction
   - maxBid: 10000
   - estimatedValue: 12000
   - aggressiveness: 0.3  # Very passive
   - sniping: true
   - snipeWindow: 10

2. auto_bid
   - checkInterval: 60  # Check every minute
   # Will mostly watch, then snipe at the end
```

## Strategy Tuning Guide

### Conservative Strategy
```json
{
  "aggressiveness": 0.3,
  "sniping": true,
  "snipeWindow": 10
}
```
- Best for: Items with many bidders
- Behavior: Waits and watches, strikes at the end
- Risk: Might lose if snipe fails

### Balanced Strategy
```json
{
  "aggressiveness": 0.7,
  "sniping": false,
  "snipeWindow": 0
}
```
- Best for: Normal competitive auctions
- Behavior: Actively maintains Sente, fights for position
- Risk: May reveal your interest early

### Aggressive Strategy
```json
{
  "aggressiveness": 0.95,
  "sniping": false,
  "snipeWindow": 0
}
```
- Best for: Must-have items
- Behavior: Fights hard for every position
- Risk: May drive up price

## Tips for Success

1. **Set Accurate Estimated Values**: The strategy works best when your valuation is realistic
2. **Choose Right Aggressiveness**: Match it to the competition level you expect
3. **Use Sniping Wisely**: Great for avoiding bidding wars, risky if network is slow
4. **Monitor First Few**: Watch manually first time to calibrate settings
5. **Adjust Based on Results**: Use the feedback parameter to improve over time

## Troubleshooting

### Browser Not Loading
```bash
# Install Playwright browsers
npx playwright install chromium
```

### Login Required
```bash
# First run with headless: false
# Manually log in
# Save session with userDataDir
```

### Bid Not Placed
- Check if you're logged in
- Verify sufficient balance
- Check Catawiki's bid increment rules
- Network issues?

### Strategy Too Passive/Aggressive
- Adjust aggressiveness parameter
- Check estimatedValue vs actual prices
- Consider using sniping mode

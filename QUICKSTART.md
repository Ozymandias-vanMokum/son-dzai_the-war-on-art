# Quick Reference Guide

## Setup in 60 Seconds

1. **Install**
   ```bash
   npm install && npm run build
   ```

2. **Configure Claude Desktop**
   Edit `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "war-on-art-auction": {
         "command": "node",
         "args": ["/absolute/path/to/dist/index.js"]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Use in Claude**
   ```
   "Set up auction monitoring for https://www.catawiki.com/l/12345678
    with max bid €1000, estimated value €1200, aggressive strategy"
   ```

## Tool Quick Reference

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `initialize_auction` | Start session | auctionUrl, maxBid, estimatedValue, aggressiveness |
| `check_auction_state` | Get status | auctionId |
| `place_bid` | Bid manually | auctionId, amount (optional) |
| `auto_bid` | Auto bidding | auctionId, checkInterval |
| `close_auction` | End session | auctionId, feedback (optional) |
| `screenshot` | Capture page | auctionId, path |

## Strategy Cheat Sheet

### Aggressiveness Levels
- **0.2-0.4**: Passive (bargain hunting)
- **0.5-0.7**: Balanced (normal bidding)
- **0.8-1.0**: Aggressive (must win)

### Sniping
- **Enabled**: Wait until final seconds, surprise bid
- **Disabled**: Active bidding, maintain Sente

### When to Use What

**Few competitors, long time**: Aggressiveness 0.7, no sniping
**Many competitors, high value**: Aggressiveness 0.4, enable sniping  
**Must-win item**: Aggressiveness 0.9, no sniping
**Casual interest**: Aggressiveness 0.3, enable sniping

## Common Commands

**Monitor auction**:
```
"Check the current state of auction rolex-001"
```

**Place recommended bid**:
```
"Place the recommended bid for auction rolex-001"
```

**Force a specific bid**:
```
"Bid €850 on auction rolex-001, force it"
```

**Auto-bid for 10 minutes**:
```
"Auto-bid on auction rolex-001, check every 20 seconds, run for 600 seconds"
```

**Take screenshot**:
```
"Take a screenshot of auction rolex-001"
```

**Close with feedback**:
```
"Close auction rolex-001, I won at €975 and my max was €1000"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Browser not opening | Run `npx playwright install chromium` |
| Not logged in | Set `headless: false`, manually log in |
| Bid rejected | Check balance, verify bid increment rules |
| Strategy too passive | Increase aggressiveness to 0.8+ |
| Lost in snipe | Increase snipeWindow to 20-30 seconds |

## The War on Art Philosophy

🎯 **Sente** = Initiative (being the current high bidder)
🏔️ **Territory** = Controlling valuable price ranges  
⚡ **Timing** = Knowing when to fight, when to wait
🌊 **Flow** = Adapting to the auction dynamics

Like Go, not Chess. Fluid, not rigid.

## Safety Reminders

✅ Set accurate maxBid (absolute limit)
✅ Estimate value realistically  
✅ Start with low aggressiveness first time
✅ Monitor manually initially
✅ Have stable internet for sniping
✅ Read Catawiki's terms of service

---

**Pro Tip**: The best strategy is patience. Let the algorithm work. Trust the Sente.

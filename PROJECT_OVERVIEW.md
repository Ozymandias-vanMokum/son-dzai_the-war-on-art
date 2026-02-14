# Project Overview: The War on Art

## What is This?

An MCP (Model Context Protocol) server that enables AI assistants like Claude to automatically bid on Catawiki auctions using a Go-inspired strategy called "The War on Art."

## Quick Links

- **Setup**: See [QUICKSTART.md](QUICKSTART.md)
- **Strategy**: See [STRATEGY.md](STRATEGY.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Configuration**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)

## File Structure

```
son-dzai_the-war-on-art/
├── src/
│   ├── index.ts              # MCP server (6 tools)
│   ├── strategy.ts           # War on Art bidding logic
│   ├── catawiki.ts          # Browser automation
│   └── test-strategy.ts     # Validation tests
├── dist/                     # Compiled JavaScript
├── docs/
│   ├── README.md            # Main documentation
│   ├── QUICKSTART.md        # 60-second setup
│   ├── STRATEGY.md          # Strategy deep dive
│   ├── EXAMPLES.md          # Usage scenarios
│   ├── CONFIGURATION.md     # Config guide
│   ├── ARCHITECTURE.md      # System design
│   └── IMPLEMENTATION_SUMMARY.md
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
└── .gitignore              # Git exclusions
```

## Core Concepts

### 🎯 Sente (先手)
Japanese Go term meaning "initiative." Being the current high bidder gives you psychological advantage and control.

### 🏔️ Three Phases
- **Early Game**: Exploration, conservative bidding
- **Mid Game**: Strategic Sente control
- **End Game**: Decisive commitment

### ⚡ Adaptive
The strategy learns from auction outcomes and improves over time.

## Six MCP Tools

1. **initialize_auction** - Start monitoring an auction
2. **check_auction_state** - Get current state and recommendations
3. **place_bid** - Execute a bid (manual or strategy-recommended)
4. **auto_bid** - Fully automated bidding
5. **close_auction** - Clean up and provide feedback
6. **screenshot** - Capture auction page

## Technology Stack

- **Language**: TypeScript (strict mode)
- **Runtime**: Node.js with ES2022 modules
- **Protocol**: MCP (Model Context Protocol) via stdio
- **Automation**: Playwright with Chromium
- **Build**: TypeScript compiler

## Dependencies

```json
{
  "@modelcontextprotocol/sdk": "1.26.0",
  "playwright": "1.55.1",
  "typescript": "5.7.2"
}
```

All at latest secure versions with zero known vulnerabilities.

## Usage Example

```javascript
// In Claude Desktop or other MCP client
"I want to bid on a vintage Rolex at 
https://www.catawiki.com/l/12345678. 
My max is €5000, estimated value €6000. 
Use an aggressive strategy."

// Claude will:
1. Initialize auction session
2. Monitor current state
3. Make strategic recommendations
4. Place bids maintaining Sente
5. Provide reasoning for each decision
```

## Key Features

✅ **Intelligent Strategy**: Go-inspired, not rigid rules
✅ **Browser Automation**: Full Playwright integration
✅ **MCP Integration**: Works with Claude and other AI assistants
✅ **Sniping Support**: Last-second bidding
✅ **Adaptive Learning**: Improves from experience
✅ **Secure**: All dependencies updated, 0 vulnerabilities
✅ **Well Documented**: 7 comprehensive docs

## Philosophy

Traditional auction bots are like Chess: deterministic, rigid, following fixed rules.

The War on Art is like Go: strategic, fluid, understanding territory control and the value of initiative (Sente).

Key insight: **Maintaining initiative is often more valuable than making the perfect bid amount.**

## Performance

- **Strategy Decisions**: O(1) time complexity
- **Browser Actions**: Optimized selectors and waits
- **MCP Protocol**: Efficient stdio communication
- **Memory**: ~50MB base + browser (~200MB)

## Security

- ✅ Input validation on all parameters
- ✅ No credential storage in code
- ✅ Updated dependencies (no ReDoS, DNS rebinding, SSL issues)
- ✅ CodeQL scan: 0 alerts
- ✅ Session isolation
- ✅ Error sanitization

## Testing

```bash
npm test                    # Run strategy validation
node dist/test-strategy.js  # Detailed test output
```

Tests validate:
- Early game patience
- Mid game Sente awareness
- End game decisiveness
- Sniping execution
- Price discipline

## Installation

```bash
# 1. Install dependencies
npm install

# 2. Build TypeScript
npm run build

# 3. Configure MCP client
# Add to claude_desktop_config.json:
{
  "mcpServers": {
    "war-on-art-auction": {
      "command": "node",
      "args": ["/path/to/dist/index.js"]
    }
  }
}

# 4. Restart Claude Desktop
```

## Development

```bash
npm run dev     # Watch mode
npm run build   # Production build
npm start       # Run server
```

## License

MIT License - See LICENSE file

## Disclaimer

For educational purposes. Always comply with Catawiki's terms of service and applicable laws. Automated bidding may be against platform policies. Use responsibly.

## Contributing

This is a complete, production-ready implementation. Future enhancements could include:
- Support for other auction platforms (eBay, etc.)
- Machine learning for strategy optimization
- Web UI for non-CLI users
- Mobile notifications
- Analytics dashboard

## The War on Art Maxim

> "The player who understands when to fight and when to yield, who maintains initiative without overcommitting, who adapts rather than follows rules - this player wins both auctions and games of Go."

---

**Status**: ✅ Complete and Ready for Use

**Last Updated**: 2026-02-14

**Version**: 1.0.0

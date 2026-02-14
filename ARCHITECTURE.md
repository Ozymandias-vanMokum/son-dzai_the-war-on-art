# System Architecture

## High-Level Overview

```
┌─────────────────┐
│  AI Assistant   │ (Claude, etc.)
│  (MCP Client)   │
└────────┬────────┘
         │ MCP Protocol
         │ (stdio)
         ▼
┌─────────────────────────────────────┐
│     War on Art MCP Server           │
│  ┌───────────────────────────────┐  │
│  │  Tool Handlers                │  │
│  │  - initialize_auction         │  │
│  │  - check_auction_state        │  │
│  │  - place_bid                  │  │
│  │  - auto_bid                   │  │
│  │  - close_auction              │  │
│  │  - screenshot                 │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Strategy Engine              │  │
│  │  - Sente Calculation          │  │
│  │  - Phase Analysis             │  │
│  │  - Bid Decision Logic         │  │
│  │  - Adaptive Learning          │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Browser Agent                │  │
│  │  - Playwright Integration     │  │
│  │  - Page Navigation            │  │
│  │  - State Extraction           │  │
│  │  - Bid Execution              │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │ Web Automation
               ▼
      ┌────────────────┐
      │   Catawiki     │
      │  (Web Browser) │
      └────────────────┘
```

## Component Details

### 1. MCP Server Layer (`src/index.ts`)
**Responsibility**: Protocol handling and tool orchestration

- Receives MCP requests via stdio
- Routes to appropriate handlers
- Manages active auction sessions
- Coordinates strategy and browser components
- Returns structured responses

**Key Functions**:
- Tool registration and listing
- Request validation
- Session state management
- Error handling and reporting

### 2. Strategy Engine (`src/strategy.ts`)
**Responsibility**: Bidding intelligence and decision making

```
Input: AuctionState → [Strategy Engine] → Output: BidDecision
```

**Components**:

#### State Analysis
- Calculate value ratio (price/estimated value)
- Measure bid pressure from competitors
- Evaluate Sente value (initiative worth)
- Determine auction phase

#### Decision Logic
```
Phase Detection
├── Early Game (>5 min)
│   └── Conservative exploration
├── Mid Game (1-5 min)
│   └── Strategic Sente control
├── End Game (<1 min)
│   └── Decisive commitment
└── Sniping Mode
    └── Last-second surprise
```

#### Calculations

**Sente Value**:
```
Sente = (Competition × 0.4) + (Value × 0.3) + (Time × 0.3)

Where:
- Competition = min(competitor_count / 5, 1.0)
- Value = 1 - (current_price / estimated_value)
- Time = 1 - (time_remaining / 300)
```

**Bid Pressure**:
```
Pressure = (Bid_Frequency × 0.5) + (Price_Acceleration × 0.5)

Where:
- Bid_Frequency = recent_bids / time_window
- Price_Acceleration = recent_increment / avg_increment
```

**Strategic Increment**:
```
Increment = Base × (1 + Sente_Value × Aggressiveness)
```

### 3. Browser Agent (`src/catawiki.ts`)
**Responsibility**: Web automation and data extraction

#### Browser Management
- Chromium instance via Playwright
- Session persistence with userDataDir
- Cookie and authentication handling
- Viewport and user agent configuration

#### Navigation
```
initialize() → navigateToAuction() → [monitoring loop]
                                    ↓
                          extractAuctionState()
                                    ↓
                              placeBid()
```

#### Data Extraction
- **Price**: Parse from multiple possible selectors
- **Time**: Convert countdown to seconds
- **Bid History**: Extract and structure recent bids
- **State**: Aggregate into AuctionState object

#### Bid Placement
```
Find bid input → Fill amount → Find submit button → Click → Verify
```

## Data Flow

### Initialize Auction Flow
```
1. User (via AI) → initialize_auction tool
2. MCP Server creates:
   - StrategyConfig from parameters
   - CatawikiAgent instance
   - WarOnArtStrategy instance
3. Browser opens and navigates to auction
4. Initial state extracted
5. Session stored in activeAuctions map
6. Response returned with initial state
```

### Check State Flow
```
1. User (via AI) → check_auction_state tool
2. MCP Server retrieves session
3. Browser extracts current state:
   - Current price
   - Time remaining
   - Bid history
4. Strategy analyzes state:
   - Calculate Sente value
   - Determine phase
   - Make decision
5. Response with state + recommendation
```

### Place Bid Flow
```
1. User (via AI) → place_bid tool
2. MCP Server retrieves session
3. If no amount specified:
   - Strategy decides amount
4. Browser agent places bid:
   - Find elements
   - Fill form
   - Submit
   - Verify
5. Update bid history
6. Response with result
```

### Auto-Bid Flow
```
┌──────────────────────────────────┐
│ Start Auto-Bid                   │
└───────────┬──────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│ Check Auction State              │
└───────────┬──────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│ Strategy Decision                │
└───────────┬──────────────────────┘
            │
       ┌────┴────┐
       │         │
    Should    Should
     Bid?      Wait?
       │         │
       ▼         │
┌──────────┐     │
│ Place    │     │
│ Bid      │     │
└──┬───────┘     │
   │             │
   └─────┬───────┘
         │
         ▼
   ┌─────────────┐
   │ Wait for    │
   │ Interval    │
   └──────┬──────┘
          │
          ▼
     Auction
     Ended?
       │  │
      No  Yes
       │   │
       └───┘
           │
           ▼
      ┌────────┐
      │ Return │
      │ Events │
      └────────┘
```

## State Management

### Session State
```typescript
activeAuctions: Map<string, {
  strategy: WarOnArtStrategy,
  agent: CatawikiAgent,
  config: StrategyConfig,
  state: AuctionState
}>
```

### Auction State
```typescript
{
  auctionId: string,
  currentPrice: number,
  yourMaxBid: number,
  timeRemaining: number,
  bidHistory: Bid[],
  estimatedValue: number,
  competitorCount: number
}
```

### Bid Decision
```typescript
{
  shouldBid: boolean,
  amount?: number,
  reasoning: string,
  confidence: number,
  strategy: 'sente' | 'gote' | 'hold' | 'final'
}
```

## Error Handling

### Strategy Layer
- Invalid states → Default safe decisions
- NaN calculations → Fallback to 0
- Missing data → Use defaults

### Browser Layer
- Element not found → Try alternative selectors
- Navigation timeout → Return error
- Bid failed → Return detailed error message
- Parse failure → Return 0/empty

### MCP Layer
- Unknown tool → Error response
- Missing auction → "Not found" error
- Exception → Caught, logged, returned as error

## Performance Considerations

### Browser Efficiency
- Reuse browser instances across bids
- Headless mode for speed
- Wait only for necessary elements
- Network idle for page loads

### Strategy Speed
- O(1) calculations for decisions
- Minimal allocations
- Pre-computed factors
- Cached intermediate values

### MCP Protocol
- Minimal message overhead
- Structured JSON responses
- Efficient stdio communication

## Security Architecture

### Input Validation
- All tool parameters validated
- URL validation for auction links
- Numeric bounds checking
- Type safety via TypeScript

### Browser Security
- Updated Playwright (SSL verification)
- User agent spoofing minimal
- No credential storage in code
- Session isolation

### Protocol Security
- Updated MCP SDK (no ReDoS, DNS rebinding)
- No shared state between clients
- Clean session lifecycle
- Error information sanitization

## Extension Points

### Adding New Auction Sites
1. Create new agent class (e.g., `EbayAgent`)
2. Implement same interface as `CatawikiAgent`
3. Add site-specific selectors
4. Register in MCP server

### Adding New Strategies
1. Extend `WarOnArtStrategy`
2. Override decision methods
3. Add new strategy types
4. Configure via tool parameters

### Adding New Tools
1. Define tool schema
2. Add to tools array
3. Implement handler
4. Document in README

## Deployment Architecture

### Local Development
```
Developer Machine
├── Source Code (src/)
├── TypeScript Compiler
├── Node.js Runtime
└── Playwright Browsers
```

### MCP Client Integration
```
Claude Desktop
├── MCP Client
├── Process Spawner (node)
└── stdio Communication
    ↓
War on Art Server Process
├── MCP Server
├── Strategy Engine
└── Browser Automation
    ↓
Chromium Browser
└── Catawiki Website
```

### Production Considerations
- Run on stable network
- Sufficient memory for browser (≥2GB)
- Persistent storage for sessions
- Logging for debugging
- Rate limiting to avoid detection

---

This architecture achieves:
✅ Separation of concerns
✅ Extensibility
✅ Testability
✅ Security
✅ Performance
✅ Maintainability

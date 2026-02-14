#!/usr/bin/env node
/**
 * War on Art MCP Server
 * 
 * MCP Server for Catawiki auction bidding with The War on Art strategy
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';

import { WarOnArtStrategy, StrategyConfig, AuctionState } from './strategy.js';
import { CatawikiAgent, CatawikiConfig } from './catawiki.js';

// Global state for active auctions
const activeAuctions = new Map<string, {
  strategy: WarOnArtStrategy;
  agent: CatawikiAgent;
  config: StrategyConfig;
  state: AuctionState;
}>();

// MCP Server setup
const server = new Server(
  {
    name: 'war-on-art-auction-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
const tools: Tool[] = [
  {
    name: 'initialize_auction',
    description: 'Initialize a new auction session with The War on Art strategy. Sets up browser automation and strategy configuration.',
    inputSchema: {
      type: 'object',
      properties: {
        auctionId: {
          type: 'string',
          description: 'Unique identifier for this auction session',
        },
        auctionUrl: {
          type: 'string',
          description: 'URL of the Catawiki auction',
        },
        maxBid: {
          type: 'number',
          description: 'Maximum amount you are willing to bid',
        },
        estimatedValue: {
          type: 'number',
          description: 'Your estimated value of the item',
        },
        aggressiveness: {
          type: 'number',
          description: 'Bidding aggressiveness (0-1, default 0.7)',
          default: 0.7,
        },
        sniping: {
          type: 'boolean',
          description: 'Enable sniping strategy (last-second bidding)',
          default: false,
        },
        snipeWindow: {
          type: 'number',
          description: 'Seconds before end to place snipe bid (default 10)',
          default: 10,
        },
        headless: {
          type: 'boolean',
          description: 'Run browser in headless mode (default true)',
          default: true,
        },
      },
      required: ['auctionId', 'auctionUrl', 'maxBid', 'estimatedValue'],
    },
  },
  {
    name: 'check_auction_state',
    description: 'Check current state of an auction and get bidding recommendation from The War on Art strategy.',
    inputSchema: {
      type: 'object',
      properties: {
        auctionId: {
          type: 'string',
          description: 'ID of the auction session',
        },
      },
      required: ['auctionId'],
    },
  },
  {
    name: 'place_bid',
    description: 'Execute a bid on the auction platform. Use the recommended amount from check_auction_state or provide a custom amount.',
    inputSchema: {
      type: 'object',
      properties: {
        auctionId: {
          type: 'string',
          description: 'ID of the auction session',
        },
        amount: {
          type: 'number',
          description: 'Bid amount (optional, uses strategy recommendation if not provided)',
        },
        force: {
          type: 'boolean',
          description: 'Force bid even if strategy recommends against it',
          default: false,
        },
      },
      required: ['auctionId'],
    },
  },
  {
    name: 'auto_bid',
    description: 'Automatically monitor auction and place bids according to The War on Art strategy. Maintains Sente (initiative) while pursuing victory.',
    inputSchema: {
      type: 'object',
      properties: {
        auctionId: {
          type: 'string',
          description: 'ID of the auction session',
        },
        checkInterval: {
          type: 'number',
          description: 'Seconds between auction state checks (default 30)',
          default: 30,
        },
        duration: {
          type: 'number',
          description: 'Duration to run auto-bidding in seconds (default: until auction ends)',
        },
      },
      required: ['auctionId'],
    },
  },
  {
    name: 'close_auction',
    description: 'Close an auction session and clean up resources.',
    inputSchema: {
      type: 'object',
      properties: {
        auctionId: {
          type: 'string',
          description: 'ID of the auction session',
        },
        feedback: {
          type: 'object',
          description: 'Optional feedback to improve strategy',
          properties: {
            won: { type: 'boolean' },
            finalPrice: { type: 'number' },
            efficiency: { type: 'number' },
          },
        },
      },
      required: ['auctionId'],
    },
  },
  {
    name: 'screenshot',
    description: 'Take a screenshot of the current auction page.',
    inputSchema: {
      type: 'object',
      properties: {
        auctionId: {
          type: 'string',
          description: 'ID of the auction session',
        },
        path: {
          type: 'string',
          description: 'Path to save screenshot (default: ./auction_screenshot.png)',
          default: './auction_screenshot.png',
        },
      },
      required: ['auctionId'],
    },
  },
];

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Tool execution handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'initialize_auction': {
        const {
          auctionId,
          auctionUrl,
          maxBid,
          estimatedValue,
          aggressiveness = 0.7,
          sniping = false,
          snipeWindow = 10,
          headless = true,
        } = args as any;

        // Create strategy config
        const config: StrategyConfig = {
          maxBid,
          targetValue: estimatedValue,
          aggressiveness,
          sniping,
          snipeWindow,
        };

        // Initialize browser agent
        const agent = new CatawikiAgent({ headless });
        await agent.initialize();
        await agent.navigateToAuction(auctionUrl);

        // Get initial state
        const state = await agent.getAuctionState(auctionId, estimatedValue);
        state.yourMaxBid = maxBid;

        // Create strategy
        const strategy = new WarOnArtStrategy(config);

        // Store auction session
        activeAuctions.set(auctionId, { strategy, agent, config, state });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: true,
                message: 'Auction session initialized',
                auctionId,
                initialState: {
                  currentPrice: state.currentPrice,
                  timeRemaining: state.timeRemaining,
                  competitorCount: state.competitorCount,
                },
              }, null, 2),
            },
          ],
        };
      }

      case 'check_auction_state': {
        const { auctionId } = args as any;
        const auction = activeAuctions.get(auctionId);

        if (!auction) {
          throw new Error(`Auction ${auctionId} not found. Initialize first.`);
        }

        // Update state from browser
        const newState = await auction.agent.getAuctionState(
          auctionId,
          auction.config.targetValue
        );
        newState.yourMaxBid = auction.config.maxBid;
        auction.state = newState;

        // Get strategy decision
        const decision = auction.strategy.decideBid(newState);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                state: {
                  currentPrice: newState.currentPrice,
                  timeRemaining: newState.timeRemaining,
                  competitorCount: newState.competitorCount,
                  bidCount: newState.bidHistory.length,
                },
                decision: {
                  shouldBid: decision.shouldBid,
                  recommendedAmount: decision.amount,
                  reasoning: decision.reasoning,
                  confidence: decision.confidence,
                  strategy: decision.strategy,
                },
              }, null, 2),
            },
          ],
        };
      }

      case 'place_bid': {
        const { auctionId, amount, force = false } = args as any;
        const auction = activeAuctions.get(auctionId);

        if (!auction) {
          throw new Error(`Auction ${auctionId} not found. Initialize first.`);
        }

        // Get strategy recommendation if amount not provided
        let bidAmount = amount;
        if (!bidAmount) {
          const decision = auction.strategy.decideBid(auction.state);
          
          if (!decision.shouldBid && !force) {
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: false,
                    message: 'Strategy recommends not bidding',
                    reasoning: decision.reasoning,
                    hint: 'Use force: true to override',
                  }, null, 2),
                },
              ],
            };
          }

          bidAmount = decision.amount;
        }

        if (!bidAmount) {
          throw new Error('No bid amount specified or recommended');
        }

        // Execute bid
        const result = await auction.agent.placeBid(bidAmount);

        // Update state after bid
        if (result.success) {
          auction.state.bidHistory.push({
            timestamp: Date.now(),
            amount: bidAmount,
            bidder: 'self',
          });
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: result.success,
                amount: bidAmount,
                error: result.error,
                timestamp: new Date().toISOString(),
              }, null, 2),
            },
          ],
        };
      }

      case 'auto_bid': {
        const { auctionId, checkInterval = 30, duration } = args as any;
        const auction = activeAuctions.get(auctionId);

        if (!auction) {
          throw new Error(`Auction ${auctionId} not found. Initialize first.`);
        }

        const startTime = Date.now();
        const events: any[] = [];

        // Run auto-bidding loop
        const runAutoBid = async () => {
          // Update state
          const newState = await auction.agent.getAuctionState(
            auctionId,
            auction.config.targetValue
          );
          newState.yourMaxBid = auction.config.maxBid;
          auction.state = newState;

          events.push({
            time: new Date().toISOString(),
            timeRemaining: newState.timeRemaining,
            currentPrice: newState.currentPrice,
          });

          // Check if auction ended
          if (newState.timeRemaining <= 0) {
            return { ended: true };
          }

          // Get strategy decision
          const decision = auction.strategy.decideBid(newState);

          if (decision.shouldBid && decision.amount) {
            // Place bid
            const result = await auction.agent.placeBid(decision.amount);
            
            events.push({
              action: 'bid_placed',
              amount: decision.amount,
              success: result.success,
              reasoning: decision.reasoning,
              strategy: decision.strategy,
            });

            if (result.success) {
              auction.state.bidHistory.push({
                timestamp: Date.now(),
                amount: decision.amount,
                bidder: 'self',
              });
            }
          } else {
            events.push({
              action: 'no_bid',
              reasoning: decision.reasoning,
              strategy: decision.strategy,
            });
          }

          // Check if should continue
          if (duration && (Date.now() - startTime) / 1000 >= duration) {
            return { ended: false, timeout: true };
          }

          // Continue monitoring
          await new Promise(resolve => setTimeout(resolve, checkInterval * 1000));
          return await runAutoBid();
        };

        const result = await runAutoBid();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                auctionId,
                completed: result.ended,
                timeout: result.timeout,
                events,
                summary: {
                  totalChecks: events.filter(e => e.currentPrice).length,
                  totalBids: events.filter(e => e.action === 'bid_placed').length,
                },
              }, null, 2),
            },
          ],
        };
      }

      case 'close_auction': {
        const { auctionId, feedback } = args as any;
        const auction = activeAuctions.get(auctionId);

        if (!auction) {
          throw new Error(`Auction ${auctionId} not found.`);
        }

        // Update strategy with feedback if provided
        if (feedback) {
          auction.strategy.updateStrategy(feedback);
        }

        // Close browser
        await auction.agent.close();

        // Remove from active auctions
        activeAuctions.delete(auctionId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: true,
                message: `Auction ${auctionId} closed`,
              }, null, 2),
            },
          ],
        };
      }

      case 'screenshot': {
        const { auctionId, path = './auction_screenshot.png' } = args as any;
        const auction = activeAuctions.get(auctionId);

        if (!auction) {
          throw new Error(`Auction ${auctionId} not found.`);
        }

        await auction.agent.screenshot(path);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: true,
                path,
              }, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('War on Art MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});

/**
 * The War on Art - Auction Strategy Logic
 *
 * This module implements a Go-inspired auction bidding strategy that focuses on:
 * - Sente (先手): Maintaining the initiative in bidding
 * - Territory Control: Understanding the value landscape of the auction
 * - Fluid Adaptation: Responding to opponent moves dynamically
 *
 * Unlike rigid Chess-like strategies, this system views each auction as a board
 * where bids are moves that control territory (price ranges and timing).
 */
export interface AuctionState {
    auctionId: string;
    currentPrice: number;
    yourMaxBid: number;
    timeRemaining: number;
    bidHistory: Bid[];
    estimatedValue: number;
    competitorCount: number;
}
export interface Bid {
    timestamp: number;
    amount: number;
    bidder: string;
}
export interface BidDecision {
    shouldBid: boolean;
    amount?: number;
    reasoning: string;
    confidence: number;
    strategy: 'sente' | 'gote' | 'hold' | 'final';
}
export interface StrategyConfig {
    maxBid: number;
    targetValue: number;
    aggressiveness: number;
    sniping: boolean;
    snipeWindow: number;
}
export declare class WarOnArtStrategy {
    private config;
    constructor(config: StrategyConfig);
    /**
     * Analyze the auction state and decide on the next move
     * Core principle: Maintain Sente (initiative) while controlling valuable territory
     */
    decideBid(state: AuctionState): BidDecision;
    private calculateBidPressure;
    private calculatePriceAcceleration;
    private calculateSenteValue;
    private earlyGameStrategy;
    private midGameStrategy;
    private endGameStrategy;
    private executeSnipeStrategy;
    private calculateStrategicIncrement;
    /**
     * Update strategy based on auction progress
     */
    updateStrategy(feedback: {
        won: boolean;
        finalPrice: number;
        efficiency: number;
    }): void;
}
//# sourceMappingURL=strategy.d.ts.map
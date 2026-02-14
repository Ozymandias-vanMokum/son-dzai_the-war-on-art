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
export class WarOnArtStrategy {
    config;
    constructor(config) {
        this.config = config;
    }
    /**
     * Analyze the auction state and decide on the next move
     * Core principle: Maintain Sente (initiative) while controlling valuable territory
     */
    decideBid(state) {
        // Check if we're already winning
        const lastBid = state.bidHistory[state.bidHistory.length - 1];
        const weAreWinning = lastBid?.bidder === 'self';
        // Calculate key strategic values
        const valueRatio = state.currentPrice / state.estimatedValue;
        const timeRatio = state.timeRemaining / 60; // normalize to minutes
        const bidPressure = this.calculateBidPressure(state);
        const senteValue = this.calculateSenteValue(state);
        // Determine if we should use sniping strategy
        if (this.config.sniping && state.timeRemaining <= this.config.snipeWindow) {
            return this.executeSnipeStrategy(state, valueRatio);
        }
        // Early game: Establish territory without overcommitting
        if (timeRatio > 5) {
            return this.earlyGameStrategy(state, valueRatio, weAreWinning);
        }
        // Mid game: Control the initiative (Sente)
        if (timeRatio > 1) {
            return this.midGameStrategy(state, valueRatio, senteValue, weAreWinning);
        }
        // End game: Decisive moves
        return this.endGameStrategy(state, valueRatio, bidPressure, weAreWinning);
    }
    calculateBidPressure(state) {
        // Analyze recent bidding activity to gauge opponent aggression
        const recentBids = state.bidHistory.slice(-5);
        const opponentBids = recentBids.filter(b => b.bidder !== 'self');
        if (opponentBids.length === 0)
            return 0;
        const bidFrequency = opponentBids.length / Math.max(1, state.timeRemaining / 60);
        const priceAcceleration = this.calculatePriceAcceleration(recentBids);
        return Math.min(1, (bidFrequency * 0.5 + priceAcceleration * 0.5));
    }
    calculatePriceAcceleration(bids) {
        if (bids.length < 2)
            return 0;
        const increments = [];
        for (let i = 1; i < bids.length; i++) {
            increments.push(bids[i].amount - bids[i - 1].amount);
        }
        const avgIncrement = increments.reduce((a, b) => a + b, 0) / increments.length;
        const recentIncrement = increments[increments.length - 1];
        return Math.min(1, recentIncrement / Math.max(1, avgIncrement));
    }
    calculateSenteValue(state) {
        // Value of having the initiative (being the current high bidder)
        // Higher value when:
        // - Competition is high
        // - Price is still reasonable
        // - Time is running out
        const competitionFactor = Math.min(1, state.competitorCount / 5);
        const valueFactor = 1 - (state.currentPrice / state.estimatedValue);
        const timeFactor = 1 - (state.timeRemaining / 300); // 5 min normalized
        return (competitionFactor * 0.4 + valueFactor * 0.3 + timeFactor * 0.3);
    }
    earlyGameStrategy(state, valueRatio, weAreWinning) {
        // Early game: Don't fight, just establish presence
        if (weAreWinning) {
            return {
                shouldBid: false,
                reasoning: 'Early game - holding Sente, no need to bid',
                confidence: 0.9,
                strategy: 'sente',
            };
        }
        // Only bid if price is very reasonable
        if (valueRatio < 0.6) {
            const minIncrement = state.currentPrice * 0.05; // 5% increment
            return {
                shouldBid: true,
                amount: state.currentPrice + minIncrement,
                reasoning: 'Early game - establishing territory at good value',
                confidence: 0.7,
                strategy: 'sente',
            };
        }
        return {
            shouldBid: false,
            reasoning: 'Early game - price not attractive enough',
            confidence: 0.8,
            strategy: 'hold',
        };
    }
    midGameStrategy(state, valueRatio, senteValue, weAreWinning) {
        // Mid game: Fight for Sente if it's valuable
        const shouldFightForSente = senteValue > 0.6 && this.config.aggressiveness > 0.5;
        if (weAreWinning && !shouldFightForSente) {
            return {
                shouldBid: false,
                reasoning: 'Mid game - maintaining Sente',
                confidence: 0.85,
                strategy: 'sente',
            };
        }
        // Calculate strategic bid amount
        if (valueRatio < 0.85) {
            const increment = this.calculateStrategicIncrement(state, senteValue);
            const bidAmount = state.currentPrice + increment;
            if (bidAmount <= this.config.maxBid) {
                return {
                    shouldBid: true,
                    amount: bidAmount,
                    reasoning: `Mid game - taking Sente (value: ${senteValue.toFixed(2)})`,
                    confidence: 0.75,
                    strategy: 'sente',
                };
            }
        }
        return {
            shouldBid: false,
            reasoning: 'Mid game - price too high or max bid reached',
            confidence: 0.7,
            strategy: 'gote',
        };
    }
    endGameStrategy(state, valueRatio, bidPressure, weAreWinning) {
        // End game: Decisive action required
        if (weAreWinning) {
            // We have Sente - hold unless heavily pressured
            if (bidPressure < 0.7) {
                return {
                    shouldBid: false,
                    reasoning: 'End game - holding winning position',
                    confidence: 0.95,
                    strategy: 'sente',
                };
            }
        }
        // Final push - bid up to max if value is there
        if (valueRatio < 1.0) {
            const finalBid = Math.min(this.config.maxBid, state.currentPrice + state.currentPrice * 0.1);
            if (finalBid > state.currentPrice) {
                return {
                    shouldBid: true,
                    amount: finalBid,
                    reasoning: 'End game - final push for victory',
                    confidence: 0.8,
                    strategy: 'final',
                };
            }
        }
        return {
            shouldBid: false,
            reasoning: 'End game - price exceeded value threshold',
            confidence: 0.9,
            strategy: 'gote',
        };
    }
    executeSnipeStrategy(state, valueRatio) {
        // Sniping: Place maximum strategic bid in final seconds
        if (valueRatio < 1.0) {
            const lastBid = state.bidHistory[state.bidHistory.length - 1];
            const weAreWinning = lastBid?.bidder === 'self';
            if (!weAreWinning) {
                const snipeBid = Math.min(this.config.maxBid, state.estimatedValue);
                return {
                    shouldBid: true,
                    amount: snipeBid,
                    reasoning: 'Snipe strategy - taking initiative in final seconds',
                    confidence: 0.85,
                    strategy: 'final',
                };
            }
        }
        return {
            shouldBid: false,
            reasoning: 'Snipe window - holding winning position',
            confidence: 0.95,
            strategy: 'sente',
        };
    }
    calculateStrategicIncrement(state, senteValue) {
        // Calculate how much to increment based on strategic value of Sente
        const baseIncrement = state.currentPrice * 0.05; // 5% base
        const senteMultiplier = 1 + (senteValue * this.config.aggressiveness);
        return baseIncrement * senteMultiplier;
    }
    /**
     * Update strategy based on auction progress
     */
    updateStrategy(feedback) {
        // Adapt aggressiveness based on results
        if (feedback.won && feedback.efficiency > 0.9) {
            // Won efficiently, can be slightly less aggressive
            this.config.aggressiveness = Math.max(0.3, this.config.aggressiveness - 0.05);
        }
        else if (!feedback.won && feedback.finalPrice < this.config.maxBid) {
            // Lost but could have bid more, be more aggressive
            this.config.aggressiveness = Math.min(1.0, this.config.aggressiveness + 0.1);
        }
    }
}
//# sourceMappingURL=strategy.js.map
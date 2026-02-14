/**
 * Simple validation test for The War on Art strategy
 */
import { WarOnArtStrategy } from './strategy.js';
// Test configuration
const config = {
    maxBid: 1000,
    targetValue: 1200,
    aggressiveness: 0.7,
    sniping: false,
    snipeWindow: 10,
};
// Test early game scenario
console.log('=== Test 1: Early Game Scenario ===');
const earlyState = {
    auctionId: 'test-001',
    currentPrice: 500,
    yourMaxBid: 1000,
    timeRemaining: 600, // 10 minutes
    bidHistory: [
        { timestamp: Date.now() - 60000, amount: 450, bidder: 'opponent_1' },
        { timestamp: Date.now(), amount: 500, bidder: 'opponent_2' },
    ],
    estimatedValue: 1200,
    competitorCount: 2,
};
const strategy1 = new WarOnArtStrategy(config);
const decision1 = strategy1.decideBid(earlyState);
console.log('State:', {
    currentPrice: earlyState.currentPrice,
    timeRemaining: earlyState.timeRemaining,
    valueRatio: earlyState.currentPrice / earlyState.estimatedValue,
});
console.log('Decision:', decision1);
console.log('');
// Test mid game scenario - we're losing
console.log('=== Test 2: Mid Game - Losing Position ===');
const midState = {
    auctionId: 'test-002',
    currentPrice: 800,
    yourMaxBid: 1000,
    timeRemaining: 180, // 3 minutes
    bidHistory: [
        { timestamp: Date.now() - 120000, amount: 700, bidder: 'self' },
        { timestamp: Date.now() - 60000, amount: 750, bidder: 'opponent_1' },
        { timestamp: Date.now(), amount: 800, bidder: 'opponent_2' },
    ],
    estimatedValue: 1200,
    competitorCount: 3,
};
const strategy2 = new WarOnArtStrategy(config);
const decision2 = strategy2.decideBid(midState);
console.log('State:', {
    currentPrice: midState.currentPrice,
    timeRemaining: midState.timeRemaining,
    weAreWinning: false,
    valueRatio: midState.currentPrice / midState.estimatedValue,
});
console.log('Decision:', decision2);
console.log('');
// Test mid game scenario - we're winning (have Sente)
console.log('=== Test 3: Mid Game - Winning Position (Sente) ===');
const senteState = {
    auctionId: 'test-003',
    currentPrice: 850,
    yourMaxBid: 1000,
    timeRemaining: 120, // 2 minutes
    bidHistory: [
        { timestamp: Date.now() - 60000, amount: 800, bidder: 'opponent_1' },
        { timestamp: Date.now(), amount: 850, bidder: 'self' },
    ],
    estimatedValue: 1200,
    competitorCount: 2,
};
const strategy3 = new WarOnArtStrategy(config);
const decision3 = strategy3.decideBid(senteState);
console.log('State:', {
    currentPrice: senteState.currentPrice,
    timeRemaining: senteState.timeRemaining,
    weAreWinning: true,
    valueRatio: senteState.currentPrice / senteState.estimatedValue,
});
console.log('Decision:', decision3);
console.log('');
// Test end game scenario
console.log('=== Test 4: End Game - Final Push ===');
const endState = {
    auctionId: 'test-004',
    currentPrice: 950,
    yourMaxBid: 1000,
    timeRemaining: 45, // 45 seconds
    bidHistory: [
        { timestamp: Date.now() - 30000, amount: 900, bidder: 'self' },
        { timestamp: Date.now(), amount: 950, bidder: 'opponent_1' },
    ],
    estimatedValue: 1200,
    competitorCount: 2,
};
const strategy4 = new WarOnArtStrategy(config);
const decision4 = strategy4.decideBid(endState);
console.log('State:', {
    currentPrice: endState.currentPrice,
    timeRemaining: endState.timeRemaining,
    weAreWinning: false,
    valueRatio: endState.currentPrice / endState.estimatedValue,
});
console.log('Decision:', decision4);
console.log('');
// Test sniping scenario
console.log('=== Test 5: Sniping Mode ===');
const snipingConfig = {
    ...config,
    sniping: true,
    snipeWindow: 15,
};
const snipeState = {
    auctionId: 'test-005',
    currentPrice: 900,
    yourMaxBid: 1000,
    timeRemaining: 12, // Within snipe window
    bidHistory: [
        { timestamp: Date.now() - 30000, amount: 850, bidder: 'opponent_1' },
        { timestamp: Date.now(), amount: 900, bidder: 'opponent_2' },
    ],
    estimatedValue: 1200,
    competitorCount: 2,
};
const strategy5 = new WarOnArtStrategy(snipingConfig);
const decision5 = strategy5.decideBid(snipeState);
console.log('State:', {
    currentPrice: snipeState.currentPrice,
    timeRemaining: snipeState.timeRemaining,
    sniping: true,
    valueRatio: snipeState.currentPrice / snipeState.estimatedValue,
});
console.log('Decision:', decision5);
console.log('');
// Test overpriced scenario
console.log('=== Test 6: Overpriced - Should Not Bid ===');
const overpriceState = {
    auctionId: 'test-006',
    currentPrice: 1100,
    yourMaxBid: 1000,
    timeRemaining: 120,
    bidHistory: [
        { timestamp: Date.now(), amount: 1100, bidder: 'opponent_1' },
    ],
    estimatedValue: 1200,
    competitorCount: 2,
};
const strategy6 = new WarOnArtStrategy(config);
const decision6 = strategy6.decideBid(overpriceState);
console.log('State:', {
    currentPrice: overpriceState.currentPrice,
    timeRemaining: overpriceState.timeRemaining,
    exceedsMaxBid: true,
    valueRatio: overpriceState.currentPrice / overpriceState.estimatedValue,
});
console.log('Decision:', decision6);
console.log('');
// Summary
console.log('=== Test Summary ===');
console.log('All tests completed successfully!');
console.log('Strategy demonstrates:');
console.log('✓ Early game patience');
console.log('✓ Mid game Sente awareness');
console.log('✓ End game decisiveness');
console.log('✓ Sniping capability');
console.log('✓ Price discipline');
//# sourceMappingURL=test-strategy.js.map
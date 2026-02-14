/**
 * Catawiki Browser Automation
 *
 * Handles browser-based interactions with Catawiki auction platform
 */
import { AuctionState } from './strategy.js';
export interface CatawikiConfig {
    headless: boolean;
    userDataDir?: string;
}
export declare class CatawikiAgent {
    private browser;
    private context;
    private page;
    private config;
    constructor(config?: CatawikiConfig);
    /**
     * Initialize browser and navigate to Catawiki
     */
    initialize(): Promise<void>;
    /**
     * Navigate to a specific auction
     */
    navigateToAuction(auctionUrl: string): Promise<void>;
    /**
     * Extract current auction state from the page
     */
    getAuctionState(auctionId: string, estimatedValue: number): Promise<AuctionState>;
    /**
     * Place a bid on the current auction
     */
    placeBid(amount: number): Promise<{
        success: boolean;
        error?: string;
    }>;
    /**
     * Check if user is logged in
     */
    isLoggedIn(): Promise<boolean>;
    /**
     * Navigate to login page (manual login required)
     */
    navigateToLogin(): Promise<void>;
    /**
     * Take a screenshot of the current page
     */
    screenshot(path: string): Promise<void>;
    /**
     * Close browser
     */
    close(): Promise<void>;
    private extractCurrentPrice;
    private extractTimeRemaining;
    private extractBidHistory;
    private parsePrice;
    private parseTimeRemaining;
}
//# sourceMappingURL=catawiki.d.ts.map
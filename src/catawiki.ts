/**
 * Catawiki Browser Automation
 * 
 * Handles browser-based interactions with Catawiki auction platform
 */

import { chromium, Browser, Page, BrowserContext } from 'playwright';
import { AuctionState, Bid } from './strategy.js';

export interface CatawikiConfig {
  headless: boolean;
  userDataDir?: string; // For persistent sessions/cookies
}

export class CatawikiAgent {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;
  private config: CatawikiConfig;

  constructor(config: CatawikiConfig = { headless: true }) {
    this.config = config;
  }

  /**
   * Initialize browser and navigate to Catawiki
   */
  async initialize(): Promise<void> {
    const launchOptions: any = {
      headless: this.config.headless,
    };

    if (this.config.userDataDir) {
      launchOptions.userDataDir = this.config.userDataDir;
    }

    this.browser = await chromium.launch(launchOptions);
    this.context = await this.browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 },
    });
    this.page = await this.context.newPage();
  }

  /**
   * Navigate to a specific auction
   */
  async navigateToAuction(auctionUrl: string): Promise<void> {
    if (!this.page) throw new Error('Browser not initialized');
    
    await this.page.goto(auctionUrl, { waitUntil: 'networkidle' });
    
    // Wait for auction page to load
    await this.page.waitForSelector('.auction-detail, .lot-detail', { timeout: 10000 });
  }

  /**
   * Extract current auction state from the page
   */
  async getAuctionState(auctionId: string, estimatedValue: number): Promise<AuctionState> {
    if (!this.page) throw new Error('Browser not initialized');

    // Extract current price
    const currentPrice = await this.extractCurrentPrice();
    
    // Extract time remaining
    const timeRemaining = await this.extractTimeRemaining();
    
    // Extract bid history
    const bidHistory = await this.extractBidHistory();
    
    // Estimate competitor count from bid history
    const uniqueBidders = new Set(bidHistory.map(b => b.bidder)).size;

    return {
      auctionId,
      currentPrice,
      yourMaxBid: 0, // Will be set by strategy
      timeRemaining,
      bidHistory,
      estimatedValue,
      competitorCount: uniqueBidders,
    };
  }

  /**
   * Place a bid on the current auction
   */
  async placeBid(amount: number): Promise<{ success: boolean; error?: string }> {
    if (!this.page) throw new Error('Browser not initialized');

    try {
      // Find bid input field
      const bidInput = await this.page.waitForSelector(
        'input[name="bid"], input#bid-amount, input.bid-input',
        { timeout: 5000 }
      );

      if (!bidInput) {
        return { success: false, error: 'Could not find bid input field' };
      }

      // Clear and enter bid amount
      await bidInput.fill('');
      await bidInput.fill(amount.toString());

      // Find and click submit button
      const submitButton = await this.page.waitForSelector(
        'button[type="submit"].bid-button, button.place-bid, button:has-text("Place bid")',
        { timeout: 5000 }
      );

      if (!submitButton) {
        return { success: false, error: 'Could not find submit button' };
      }

      // Click the bid button
      await submitButton.click();

      // Wait for confirmation or error
      await this.page.waitForTimeout(1000);

      // Check for success confirmation
      const successIndicator = await this.page.$(
        '.bid-success, .success-message, [class*="success"]'
      );

      if (successIndicator) {
        return { success: true };
      }

      // Check for error messages
      const errorElement = await this.page.$(
        '.bid-error, .error-message, [class*="error"]'
      );

      if (errorElement) {
        const errorText = await errorElement.textContent();
        return { success: false, error: errorText || 'Unknown error occurred' };
      }

      // Assume success if no error found
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Check if user is logged in
   */
  async isLoggedIn(): Promise<boolean> {
    if (!this.page) throw new Error('Browser not initialized');

    try {
      // Check for login indicators
      const loginButton = await this.page.$('a[href*="login"], button:has-text("Log in")');
      return loginButton === null;
    } catch {
      return false;
    }
  }

  /**
   * Navigate to login page (manual login required)
   */
  async navigateToLogin(): Promise<void> {
    if (!this.page) throw new Error('Browser not initialized');
    
    await this.page.goto('https://www.catawiki.com/login', { waitUntil: 'networkidle' });
  }

  /**
   * Take a screenshot of the current page
   */
  async screenshot(path: string): Promise<void> {
    if (!this.page) throw new Error('Browser not initialized');
    await this.page.screenshot({ path, fullPage: true });
  }

  /**
   * Close browser
   */
  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.context = null;
      this.page = null;
    }
  }

  // Private helper methods

  private async extractCurrentPrice(): Promise<number> {
    if (!this.page) throw new Error('Browser not initialized');

    try {
      // Try various selectors for price
      const priceSelectors = [
        '.current-bid .price',
        '.current-price',
        '[data-test="current-bid"]',
        '.lot-detail__current-bid',
      ];

      for (const selector of priceSelectors) {
        const element = await this.page.$(selector);
        if (element) {
          const text = await element.textContent();
          const price = this.parsePrice(text || '');
          if (price > 0) return price;
        }
      }

      // Fallback: try to find any price-like text
      const pageText = await this.page.textContent('body');
      const priceMatch = pageText?.match(/€\s*([\d,]+\.?\d*)/);
      if (priceMatch) {
        return this.parsePrice(priceMatch[1]);
      }

      return 0;
    } catch {
      return 0;
    }
  }

  private async extractTimeRemaining(): Promise<number> {
    if (!this.page) throw new Error('Browser not initialized');

    try {
      // Look for countdown timer
      const timerSelectors = [
        '[data-test="countdown"]',
        '.countdown',
        '.time-remaining',
        '[class*="timer"]',
      ];

      for (const selector of timerSelectors) {
        const element = await this.page.$(selector);
        if (element) {
          const text = await element.textContent();
          const seconds = this.parseTimeRemaining(text || '');
          if (seconds > 0) return seconds;
        }
      }

      // Default to 1 hour if can't find
      return 3600;
    } catch {
      return 3600;
    }
  }

  private async extractBidHistory(): Promise<Bid[]> {
    if (!this.page) throw new Error('Browser not initialized');

    const bids: Bid[] = [];

    try {
      // Try to find bid history section
      const bidHistorySelectors = [
        '.bid-history',
        '[data-test="bid-history"]',
        '.lot-detail__bid-history',
      ];

      for (const selector of bidHistorySelectors) {
        const historyContainer = await this.page.$(selector);
        if (historyContainer) {
          // Extract individual bid rows
          const bidRows = await historyContainer.$$('.bid-row, .bid-item, li');
          
          for (let i = 0; i < bidRows.length; i++) {
            const row = bidRows[i];
            const text = await row.textContent();
            const amount = this.parsePrice(text || '');
            
            if (amount > 0) {
              bids.push({
                timestamp: Date.now() - (i * 60000), // Approximate
                amount,
                bidder: `opponent_${i}`,
              });
            }
          }
          
          break;
        }
      }

      // Return in chronological order
      return bids.reverse();
    } catch {
      return [];
    }
  }

  private parsePrice(text: string): number {
    // Handle European format (1.234,56) and US format (1,234.56)
    // Remove currency symbols and spaces first
    let cleaned = text.replace(/[€$£\s]/g, '');
    
    // Determine if comma or period is the decimal separator
    const lastComma = cleaned.lastIndexOf(',');
    const lastPeriod = cleaned.lastIndexOf('.');
    
    if (lastComma > lastPeriod) {
      // European format: 1.234,56 -> remove periods, replace comma with period
      cleaned = cleaned.replace(/\./g, '').replace(',', '.');
    } else {
      // US format: 1,234.56 -> just remove commas
      cleaned = cleaned.replace(/,/g, '');
    }
    
    const price = parseFloat(cleaned);
    return isNaN(price) ? 0 : price;
  }

  private parseTimeRemaining(text: string): number {
    // Parse formats like "1h 23m 45s" or "23:45" or "45s"
    let seconds = 0;

    const hourMatch = text.match(/(\d+)\s*h/i);
    if (hourMatch) seconds += parseInt(hourMatch[1]) * 3600;

    const minuteMatch = text.match(/(\d+)\s*m/i);
    if (minuteMatch) seconds += parseInt(minuteMatch[1]) * 60;

    const secondMatch = text.match(/(\d+)\s*s/i);
    if (secondMatch) seconds += parseInt(secondMatch[1]);

    // Try time format HH:MM:SS or MM:SS
    const timeMatch = text.match(/(\d+):(\d+)(?::(\d+))?/);
    if (timeMatch) {
      if (timeMatch[3]) {
        // HH:MM:SS
        seconds = parseInt(timeMatch[1]) * 3600 + parseInt(timeMatch[2]) * 60 + parseInt(timeMatch[3]);
      } else {
        // MM:SS
        seconds = parseInt(timeMatch[1]) * 60 + parseInt(timeMatch[2]);
      }
    }

    return seconds;
  }
}

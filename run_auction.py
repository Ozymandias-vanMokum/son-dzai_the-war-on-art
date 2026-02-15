#!/usr/bin/env python3
"""
The War On Art - Main Entry Point

Interactive script to run the Catawiki auction bidding system.
Prompts for all required parameters and manages the complete auction lifecycle.
"""

import asyncio
import sys
from catawiki.browser import CatawikiBrowser
from catawiki.monitor import AuctionMonitor
from strategy.inputs import AuctionParams
from strategy.learner import ReinforcementLearner


async def main():
    print("=" * 60)
    print("THE WAR ON ART - Catawiki Auction Bidding System")
    print("=" * 60)
    print()
    print("This program will help you bid strategically on Catawiki auctions.")
    print("You'll be asked to provide auction details and your bidding parameters.")
    print()
    
    # Prompt for auction parameters
    print("Step 1: Auction Details")
    print("-" * 60)
    lot_url = input("Enter the Catawiki lot URL: ").strip()
    
    if not lot_url or "catawiki.com" not in lot_url:
        print("❌ Error: Please provide a valid Catawiki URL")
        return
    
    lot_id = lot_url.rstrip("/").split("/")[-1]
    print()
    
    print("Step 2: Budget Configuration")
    print("-" * 60)
    try:
        max_budget = float(input("Enter your maximum budget (EUR): "))
        if max_budget <= 0:
            print("❌ Error: Budget must be positive")
            return
    except ValueError:
        print("❌ Error: Please enter a valid number")
        return
    
    print()
    print("Step 3: Bidding Strategy")
    print("-" * 60)
    print("Greediness Level (0-100):")
    print("  • 0-30:   Conservative (patient, minimal early activity)")
    print("  • 30-70:  Moderate (balanced approach)")
    print("  • 70-100: Aggressive (jump bids, intimidation tactics)")
    print()
    
    try:
        greediness = int(input("Enter greediness level (0-100): "))
        if not (0 <= greediness <= 100):
            print("❌ Error: Greediness must be between 0 and 100")
            return
    except ValueError:
        print("❌ Error: Please enter a valid number")
        return
    
    # Create auction parameters
    params = AuctionParams(
        lot_id=lot_id,
        lot_url=lot_url,
        max_budget=max_budget,
        greediness=greediness
    )
    
    # Display configuration summary
    print()
    print("=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Lot ID:           {lot_id}")
    print(f"Lot URL:          {lot_url}")
    print(f"Maximum Budget:   €{max_budget:.2f}")
    print(f"Greediness Level: {greediness}% ", end="")
    
    if greediness <= 30:
        print("(Conservative)")
    elif greediness <= 70:
        print("(Moderate)")
    else:
        print("(Aggressive)")
    
    true_ceiling = params.true_ceiling
    print(f"True Ceiling:     €{true_ceiling:.2f} (includes Ozymandias offset)")
    
    total_at_budget = params.calculate_total_acquisition_cost(max_budget)
    print(f"\nCost Breakdown at max budget:")
    print(f"  Base bid:        €{max_budget:.2f}")
    print(f"  + 9% fee:        €{max_budget * 0.09:.2f}")
    print(f"  + Protection:    €3.00")
    print(f"  = Total:         €{total_at_budget:.2f}")
    print("=" * 60)
    print()
    
    confirm = input("Proceed with these settings? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\n❌ Aborted by user.")
        return
    
    # Initialize components
    print()
    print("=" * 60)
    print("INITIALIZATION")
    print("=" * 60)
    
    browser = CatawikiBrowser(headless=False)  # Visible browser for first run
    learner = ReinforcementLearner()
    
    try:
        # Launch browser
        print("🚀 Launching browser...")
        await browser.launch()
        print("✅ Browser launched successfully")
        
        # Check authentication status
        print("🔐 Checking login status...")
        is_logged_in = await browser.is_logged_in()
        
        if not is_logged_in:
            print("\n⚠️  You need to log in to Catawiki")
            print("📋 A browser window will open. Please:")
            print("   1. Log in with your Catawiki credentials")
            print("   2. Complete any 2FA if required")
            print("   3. Wait for the redirect to complete")
            print("\n⏳ Opening login page...")
            await browser.login_interactive()
            print("✅ Login successful! Session saved for future use.")
        else:
            print("✅ Already logged in (using saved session)")
        
        # Start the auction monitor
        print()
        print("=" * 60)
        print("AUCTION MONITORING ACTIVE")
        print("=" * 60)
        print("⚔️  The War On Art engine is now monitoring the auction")
        print("📊 Bidding will be executed according to strategic principles")
        print("⏰ Faster polling as auction end approaches")
        print()
        print("💡 To stop at any time, press Ctrl+C")
        print("   (This will NOT cancel bids already placed)")
        print()
        print("Monitoring begins...")
        print("-" * 60)
        
        monitor = AuctionMonitor(params, browser, learner, poll_interval=2.0)
        battle_log = await monitor.run()
        
        # Display results
        print()
        print("=" * 60)
        print("BATTLE REPORT")
        print("=" * 60)
        for entry in battle_log:
            print(entry)
        print("=" * 60)
        print()
        
        # Show learner statistics
        stats = learner.get_stats()
        print("LEARNING STATISTICS")
        print("-" * 60)
        print(f"Total auctions:     {stats['total_auctions']}")
        print(f"Win rate:           {stats['win_rate']:.1%}")
        print(f"Avg savings:        {stats['avg_savings']:.1%}")
        print(f"Preferred action:   {stats['preferred_action']}")
        print(f"Exploration rate:   {stats['epsilon']:.2%}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        print("🛑 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔒 Closing browser...")
        await browser.close()
        print("✅ Browser closed. Session complete.")
        print("\n" + "=" * 60)
        print("Thank you for using The War On Art!")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nProgram terminated.")
        sys.exit(0)

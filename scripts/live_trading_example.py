"""
Live Trading Example - Demonstrates Phase 1 Critical Features

Shows how to use:
1. Stop-Loss Automation
2. Live Trade Execution (MOO/Limit orders)
3. Data Fetching with Stooq Fallback

Usage:
    python live_trading_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import PortfolioMemoryManager, TradeExecutor


def example_1_stop_loss_automation():
    """Example: Automatic stop-loss monitoring and execution."""
    print("\n" + "="*80)
    print("EXAMPLE 1: STOP-LOSS AUTOMATION")
    print("="*80 + "\n")
    
    # Initialize portfolio
    portfolio = PortfolioMemoryManager(initial_cash=100.0)
    
    # Add position with stop-loss
    print("Adding position with stop-loss...")
    portfolio.add_position(
        ticker="AAPL",
        shares=2.0,
        buy_price=180.00,
        reason="Example buy",
        stop_loss=170.00  # 5.5% stop-loss
    )
    
    print("\nPortfolio Summary:")
    summary = portfolio.get_portfolio_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Check stop-losses (will fetch market data)
    print("\nChecking stop-losses...")
    triggered = portfolio.check_stop_losses()
    
    if triggered:
        print(f"\n{len(triggered)} stop-loss(es) triggered!")
        for ticker, shares, price, pnl in triggered:
            print(f"  {ticker}: Sold {shares} @ ${price:.2f}, P&L: ${pnl:+.2f}")
    else:
        print("\nNo stop-losses triggered")


def example_2_market_data_fallback():
    """Example: Data fetching with Yahoo → Stooq fallback."""
    print("\n" + "="*80)
    print("EXAMPLE 2: DATA FETCHING WITH FALLBACK")
    print("="*80 + "\n")
    
    portfolio = PortfolioMemoryManager(initial_cash=100.0)
    
    # Add some positions
    portfolio.add_position("AAPL", 1.0, 180.00, "Test position 1")
    portfolio.add_position("MSFT", 1.0, 400.00, "Test position 2")
    
    # Update prices from market with fallback
    print("\nUpdating prices from market...")
    sources = portfolio.update_prices_from_market()
    
    print("\nData sources used:")
    for ticker, source in sources.items():
        print(f"  {ticker}: {source}")
    
    print("\nUpdated portfolio:")
    print(portfolio.holdings[['ticker', 'buy_price', 'current_price', 'pnl', 'pnl_pct']])


def example_3_live_moo_order():
    """Example: Market-on-Open buy order."""
    print("\n" + "="*80)
    print("EXAMPLE 3: MARKET-ON-OPEN BUY ORDER")
    print("="*80 + "\n")
    
    portfolio = PortfolioMemoryManager(initial_cash=100.0)
    executor = TradeExecutor()
    
    # Fetch market data
    ticker = "AAPL"
    print(f"Fetching market data for {ticker}...")
    market_data, source = portfolio.fetch_market_data(ticker, days=1)
    
    if not market_data.empty:
        print(f"Data source: {source}")
        print(f"Open: ${float(market_data['Open'].iloc[-1]):.2f}")
        print(f"High: ${float(market_data['High'].iloc[-1]):.2f}")
        print(f"Low: ${float(market_data['Low'].iloc[-1]):.2f}")
        print(f"Close: ${float(market_data['Close'].iloc[-1]):.2f}")
        
        # Execute MOO order (non-interactive for demo)
        success, msg = executor.execute_buy_moo(
            ticker=ticker,
            shares=0.5,
            stop_loss=170.00,
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False  # Set True for confirmation prompt
        )
        
        print(f"\nResult: {msg}")
        
        if success:
            print("\nPortfolio after MOO buy:")
            print(portfolio.holdings[['ticker', 'shares', 'buy_price', 'stop_loss']])


def example_4_live_limit_order():
    """Example: Limit buy and sell orders."""
    print("\n" + "="*80)
    print("EXAMPLE 4: LIMIT ORDERS")
    print("="*80 + "\n")
    
    portfolio = PortfolioMemoryManager(initial_cash=100.0)
    executor = TradeExecutor()
    
    ticker = "AAPL"
    
    # Fetch market data
    print(f"Fetching market data for {ticker}...")
    market_data, source = portfolio.fetch_market_data(ticker, days=1)
    
    if not market_data.empty:
        current_price = float(market_data['Close'].iloc[-1])
        print(f"Current price: ${current_price:.2f}")
        
        # Try a limit buy at current price (should fill)
        limit_price = current_price
        print(f"\nAttempting limit buy at ${limit_price:.2f}...")
        
        success, msg = executor.execute_buy_limit(
            ticker=ticker,
            shares=0.5,
            limit_price=limit_price,
            stop_loss=current_price * 0.95,
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False
        )
        
        print(f"Buy result: {msg}")
        
        if success:
            # Now try a limit sell
            sell_limit = current_price * 1.02  # 2% above current
            print(f"\nAttempting limit sell at ${sell_limit:.2f}...")
            
            success, msg = executor.execute_sell_limit(
                ticker=ticker,
                shares=0.5,
                limit_price=sell_limit,
                portfolio_manager=portfolio,
                market_data=market_data,
                interactive=False,
                reason="Take profit at 2%"
            )
            
            print(f"Sell result: {msg}")


def example_5_complete_workflow():
    """Example: Complete workflow with all features."""
    print("\n" + "="*80)
    print("EXAMPLE 5: COMPLETE TRADING WORKFLOW")
    print("="*80 + "\n")
    
    # 1. Initialize
    portfolio = PortfolioMemoryManager(initial_cash=100.0)
    executor = TradeExecutor()
    
    print("Initial cash: $100.00\n")
    
    # 2. Buy with stop-loss
    ticker = "MSFT"
    market_data, source = portfolio.fetch_market_data(ticker, days=1)
    
    if not market_data.empty:
        current_price = float(market_data['Close'].iloc[-1])
        
        print(f"Buying {ticker} at market...")
        success, msg = executor.execute_buy_moo(
            ticker=ticker,
            shares=0.2,
            stop_loss=current_price * 0.94,  # 6% stop-loss
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False
        )
        print(msg)
        
        # 3. Update prices from market
        print("\nUpdating market prices...")
        sources = portfolio.update_prices_from_market()
        
        # 4. Check stop-losses
        print("\nChecking stop-losses...")
        triggered = portfolio.check_stop_losses()
        
        # 5. Show summary
        print("\n" + "-"*60)
        summary = portfolio.get_portfolio_summary()
        print(f"Cash: ${summary['cash']:.2f}")
        print(f"Holdings Value: ${summary['holdings_value']:.2f}")
        print(f"Total Equity: ${summary['total_equity']:.2f}")
        print(f"ROI: {summary['roi']:.2f}%")
        print(f"Positions: {summary['num_positions']}")
        
        # 6. Save snapshot
        print("\nSaving daily snapshot...")
        portfolio.save_daily_snapshot()
        print(f"Snapshot saved to: {portfolio.daily_summary_file}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("LIVE TRADING EXAMPLES - PHASE 1 CRITICAL FEATURES")
    print("="*80)
    print("\nFeatures demonstrated:")
    print("  1. Stop-Loss Automation")
    print("  2. Data Fetching with Yahoo → Stooq Fallback")
    print("  3. Market-on-Open (MOO) Orders")
    print("  4. Limit Orders (Buy/Sell)")
    print("  5. Complete Trading Workflow")
    print("\n" + "="*80)
    
    # Run examples
    try:
        example_1_stop_loss_automation()
    except Exception as e:
        print(f"\nExample 1 error: {e}")
    
    try:
        example_2_market_data_fallback()
    except Exception as e:
        print(f"\nExample 2 error: {e}")
    
    try:
        example_3_live_moo_order()
    except Exception as e:
        print(f"\nExample 3 error: {e}")
    
    try:
        example_4_live_limit_order()
    except Exception as e:
        print(f"\nExample 4 error: {e}")
    
    try:
        example_5_complete_workflow()
    except Exception as e:
        print(f"\nExample 5 error: {e}")
    
    print("\n" + "="*80)
    print("EXAMPLES COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

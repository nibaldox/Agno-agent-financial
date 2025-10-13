"""
Test Suite para FASE 1: Funcionalidades Críticas

Tests para:
- Stop-Loss Automation
- Data Fetching con Fallback
- Live Trade Execution
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import PortfolioMemoryManager, TradeExecutor
import pandas as pd


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, str(error)))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")
        
        if self.errors:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        print("="*80 + "\n")


def test_portfolio_initialization(results: TestResults):
    """Test 1: Portfolio initialization."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        
        assert portfolio.cash == 100.0
        assert portfolio.initial_cash == 100.0
        assert portfolio.holdings.empty
        assert portfolio.trades.empty
        
        results.add_pass("Portfolio Initialization")
    except Exception as e:
        results.add_fail("Portfolio Initialization", e)


def test_add_position_with_stoploss(results: TestResults):
    """Test 2: Add position with stop-loss."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        
        portfolio.add_position(
            ticker="TEST",
            shares=10.0,
            buy_price=5.00,
            stop_loss=4.50,
            reason="Test buy"
        )
        
        assert len(portfolio.holdings) == 1
        assert portfolio.holdings.iloc[0]['ticker'] == "TEST"
        assert portfolio.holdings.iloc[0]['shares'] == 10.0
        assert portfolio.holdings.iloc[0]['stop_loss'] == 4.50
        assert portfolio.cash == 50.0  # 100 - (10 * 5)
        
        results.add_pass("Add Position with Stop-Loss")
    except Exception as e:
        results.add_fail("Add Position with Stop-Loss", e)


def test_remove_position(results: TestResults):
    """Test 3: Remove position."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        portfolio.add_position("TEST", 10.0, 5.00, "Buy")
        
        portfolio.remove_position(
            ticker="TEST",
            shares=10.0,
            sell_price=5.50,
            reason="Sell"
        )
        
        assert portfolio.holdings.empty
        assert portfolio.cash == 105.0  # 50 + (10 * 5.5)
        assert len(portfolio.trades) == 2  # Buy + Sell
        
        results.add_pass("Remove Position")
    except Exception as e:
        results.add_fail("Remove Position", e)


def test_data_fetching(results: TestResults):
    """Test 4: Market data fetching."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        
        # Try fetching AAPL data
        df, source = portfolio.fetch_market_data("AAPL", days=5)
        
        assert not df.empty, "DataFrame should not be empty"
        assert source in ["yahoo", "stooq"], f"Invalid source: {source}"
        assert "Close" in df.columns, "Close column missing"
        assert "Open" in df.columns, "Open column missing"
        
        results.add_pass("Market Data Fetching")
    except Exception as e:
        results.add_fail("Market Data Fetching", e)


def test_update_prices_from_market(results: TestResults):
    """Test 5: Update prices from market."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        portfolio.add_position("AAPL", 1.0, 150.00, "Test")
        
        sources = portfolio.update_prices_from_market()
        
        assert "AAPL" in sources
        assert sources["AAPL"] in ["yahoo", "stooq", "failed"]
        
        if sources["AAPL"] != "failed":
            assert portfolio.holdings.iloc[0]['current_price'] > 0
        
        results.add_pass("Update Prices from Market")
    except Exception as e:
        results.add_fail("Update Prices from Market", e)


def test_portfolio_summary(results: TestResults):
    """Test 6: Portfolio summary."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        portfolio.add_position("TEST", 10.0, 5.00, "Buy")
        
        # Update price
        portfolio.update_prices({"TEST": 5.50})
        
        summary = portfolio.get_portfolio_summary()
        
        assert summary['cash'] == 50.0
        assert summary['holdings_value'] == 55.0  # 10 * 5.5
        assert summary['total_equity'] == 105.0
        assert summary['roi'] == 5.0  # 5% gain
        assert summary['num_positions'] == 1
        
        results.add_pass("Portfolio Summary")
    except Exception as e:
        results.add_fail("Portfolio Summary", e)


def test_trade_executor_initialization(results: TestResults):
    """Test 7: TradeExecutor initialization."""
    try:
        executor = TradeExecutor()
        
        assert executor.last_execution is None
        
        results.add_pass("TradeExecutor Initialization")
    except Exception as e:
        results.add_fail("TradeExecutor Initialization", e)


def test_moo_order_validation(results: TestResults):
    """Test 8: MOO order validation (simulated)."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        executor = TradeExecutor()
        
        # Create simulated market data
        market_data = pd.DataFrame({
            'Open': [180.00],
            'High': [182.00],
            'Low': [179.00],
            'Close': [181.00],
            'Volume': [1000000]
        })
        
        # Test MOO order
        success, msg = executor.execute_buy_moo(
            ticker="AAPL",
            shares=0.5,
            stop_loss=170.00,
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False
        )
        
        assert success == True
        assert "MOO BUY executed" in msg
        assert len(portfolio.holdings) == 1
        assert portfolio.holdings.iloc[0]['ticker'] == "AAPL"
        
        results.add_pass("MOO Order Validation")
    except Exception as e:
        results.add_fail("MOO Order Validation", e)


def test_limit_buy_order(results: TestResults):
    """Test 9: Limit buy order."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        executor = TradeExecutor()
        
        # Market data where limit will be hit
        market_data = pd.DataFrame({
            'Open': [180.00],
            'High': [182.00],
            'Low': [179.00],
            'Close': [181.00],
            'Volume': [1000000]
        })
        
        # Limit order at 180 (should fill at open)
        success, msg = executor.execute_buy_limit(
            ticker="AAPL",
            shares=0.5,
            limit_price=180.00,
            stop_loss=170.00,
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False
        )
        
        assert success == True
        assert "LIMIT BUY executed" in msg
        
        results.add_pass("Limit Buy Order")
    except Exception as e:
        results.add_fail("Limit Buy Order", e)


def test_limit_buy_not_filled(results: TestResults):
    """Test 10: Limit buy order not filled."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        executor = TradeExecutor()
        
        # Market data where limit won't be hit
        market_data = pd.DataFrame({
            'Open': [185.00],
            'High': [187.00],
            'Low': [184.00],
            'Close': [186.00],
            'Volume': [1000000]
        })
        
        # Limit order at 180 (too low)
        success, msg = executor.execute_buy_limit(
            ticker="AAPL",
            shares=0.5,
            limit_price=180.00,
            stop_loss=170.00,
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False
        )
        
        assert success == False
        assert "not reached" in msg.lower()
        
        results.add_pass("Limit Buy Not Filled")
    except Exception as e:
        results.add_fail("Limit Buy Not Filled", e)


def test_limit_sell_order(results: TestResults):
    """Test 11: Limit sell order."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=100.0)
        executor = TradeExecutor()
        
        # Add position first
        portfolio.add_position("AAPL", 1.0, 180.00, "Initial buy")
        
        # Market data where sell limit will be hit
        market_data = pd.DataFrame({
            'Open': [185.00],
            'High': [187.00],
            'Low': [184.00],
            'Close': [186.00],
            'Volume': [1000000]
        })
        
        # Sell limit at 185 (should fill)
        success, msg = executor.execute_sell_limit(
            ticker="AAPL",
            shares=1.0,
            limit_price=185.00,
            portfolio_manager=portfolio,
            market_data=market_data,
            interactive=False,
            reason="Take profit"
        )
        
        assert success == True
        assert "LIMIT SELL executed" in msg
        assert portfolio.holdings.empty
        
        results.add_pass("Limit Sell Order")
    except Exception as e:
        results.add_fail("Limit Sell Order", e)


def test_insufficient_cash(results: TestResults):
    """Test 12: Insufficient cash validation."""
    try:
        portfolio = PortfolioMemoryManager(initial_cash=10.0)
        
        # Try to buy more than available cash
        try:
            portfolio.add_position("AAPL", 10.0, 180.00, "Test")
            # Should raise ValueError
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "insuficiente" in str(e).lower()
        
        results.add_pass("Insufficient Cash Validation")
    except Exception as e:
        results.add_fail("Insufficient Cash Validation", e)


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FASE 1 TEST SUITE")
    print("="*80 + "\n")
    
    results = TestResults()
    
    # Run tests
    print("Running tests...\n")
    
    test_portfolio_initialization(results)
    test_add_position_with_stoploss(results)
    test_remove_position(results)
    test_data_fetching(results)
    test_update_prices_from_market(results)
    test_portfolio_summary(results)
    test_trade_executor_initialization(results)
    test_moo_order_validation(results)
    test_limit_buy_order(results)
    test_limit_buy_not_filled(results)
    test_limit_sell_order(results)
    test_insufficient_cash(results)
    
    # Print summary
    results.summary()
    
    return results.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

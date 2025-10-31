"""
Live Trading Execution Module

Handles real trade execution with:
- Market-on-Open (MOO) orders
- Limit orders
- Trade validation and execution
- Integration with portfolio manager

Based on trading_script.py execution logic.
"""

import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import yfinance as yf

    _HAS_YFINANCE = True
except ImportError:
    _HAS_YFINANCE = False
    print("[WARNING] yfinance not installed, price updates will be limited")

try:
    import pandas_datareader.data as pdr

    _HAS_PDR = True
except ImportError:
    _HAS_PDR = False


class TradeExecutor:
    """
    Handles live trade execution with support for MOO and limit orders.

    Features:
    - Market-on-Open execution
    - Limit order execution with price validation
    - Interactive confirmation mode
    - Complete trade logging
    - Cash and position validation

    Example:
        >>> executor = TradeExecutor()
        >>> success, msg = executor.execute_buy_limit(
        ...     ticker="ABEO",
        ...     shares=10.0,
        ...     limit_price=5.50,
        ...     stop_loss=4.95,
        ...     portfolio_manager=portfolio,
        ...     interactive=True
        ... )
    """

    def __init__(self):
        """Initialize trade executor."""
        self.last_execution = None

    def execute_buy_moo(
        self,
        ticker: str,
        shares: float,
        stop_loss: float,
        portfolio_manager,
        market_data: pd.DataFrame,
        interactive: bool = True,
    ) -> Tuple[bool, str]:
        """
        Execute a Market-on-Open buy order.

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to buy
            stop_loss: Stop loss price (0 to skip)
            portfolio_manager: PortfolioMemoryManager instance
            market_data: DataFrame with OHLCV data
            interactive: If True, ask for confirmation

        Returns:
            Tuple of (success: bool, message: str)
        """
        if market_data.empty:
            return False, f"❌ No market data available for {ticker}"

        # Get opening price
        if "Open" in market_data.columns:
            exec_price = float(market_data["Open"].iloc[-1])
        else:
            exec_price = float(market_data["Close"].iloc[-1])

        if np.isnan(exec_price):
            exec_price = float(market_data["Close"].iloc[-1])

        exec_price = round(exec_price, 2)
        notional = exec_price * shares

        # Validate cash
        if notional > portfolio_manager.cash:
            return (
                False,
                f"❌ Insufficient cash: need ${notional:.2f}, have ${portfolio_manager.cash:.2f}",
            )

        # Interactive confirmation
        if interactive:
            print(f"\n{'='*60}")
            print(f"🔵 MARKET-ON-OPEN BUY ORDER")
            print(f"{'='*60}")
            print(f"Ticker: {ticker}")
            print(f"Shares: {shares}")
            print(f"Execution Price: ${exec_price:.2f} (Opening)")
            print(f"Total Cost: ${notional:.2f}")
            print(f"Stop Loss: ${stop_loss:.2f}" if stop_loss > 0 else "Stop Loss: None")
            print(f"Cash After: ${portfolio_manager.cash - notional:.2f}")
            print(f"{'='*60}")

            confirm = input("Confirm execution? (Enter to proceed, '1' to cancel): ").strip()
            if confirm == "1":
                return False, "❌ Order cancelled by user"

        # Execute trade
        reason = f"MOO BUY - Filled at ${exec_price:.2f}"
        portfolio_manager.add_position(
            ticker=ticker,
            shares=shares,
            buy_price=exec_price,
            reason=reason,
            stop_loss=stop_loss if stop_loss > 0 else None,
        )

        self.last_execution = {
            "type": "buy_moo",
            "ticker": ticker,
            "shares": shares,
            "price": exec_price,
            "timestamp": datetime.now(),
        }

        return True, f"✅ MOO BUY executed: {shares} {ticker} @ ${exec_price:.2f}"

    def execute_buy_limit(
        self,
        ticker: str,
        shares: float,
        limit_price: float,
        stop_loss: float,
        portfolio_manager,
        market_data: pd.DataFrame,
        interactive: bool = True,
    ) -> Tuple[bool, str]:
        """
        Execute a limit buy order.

        Only executes if:
        - Opening price <= limit OR
        - Low of day <= limit

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to buy
            limit_price: Maximum price to pay
            stop_loss: Stop loss price (0 to skip)
            portfolio_manager: PortfolioMemoryManager instance
            market_data: DataFrame with OHLCV data
            interactive: If True, ask for confirmation

        Returns:
            Tuple of (success: bool, message: str)
        """
        if market_data.empty:
            return False, f"❌ No market data available for {ticker}"

        # Get OHLC prices
        o = float(market_data.get("Open", [np.nan])[-1])
        h = float(market_data["High"].iloc[-1])
        l = float(market_data["Low"].iloc[-1])

        if np.isnan(o):
            o = float(market_data["Close"].iloc[-1])

        # Determine execution price
        exec_price = None
        if o <= limit_price:
            exec_price = o
        elif l <= limit_price:
            exec_price = limit_price
        else:
            return False, f"⚠️ Limit price ${limit_price:.2f} not reached (range: ${l:.2f}-${h:.2f})"

        exec_price = round(exec_price, 2)
        notional = exec_price * shares

        # Validate cash
        if notional > portfolio_manager.cash:
            return (
                False,
                f"❌ Insufficient cash: need ${notional:.2f}, have ${portfolio_manager.cash:.2f}",
            )

        # Interactive confirmation
        if interactive:
            print(f"\n{'='*60}")
            print(f"🟢 LIMIT BUY ORDER")
            print(f"{'='*60}")
            print(f"Ticker: {ticker}")
            print(f"Shares: {shares}")
            print(f"Limit Price: ${limit_price:.2f}")
            print(f"Execution Price: ${exec_price:.2f}")
            print(f"Total Cost: ${notional:.2f}")
            print(f"Stop Loss: ${stop_loss:.2f}" if stop_loss > 0 else "Stop Loss: None")
            print(f"Cash After: ${portfolio_manager.cash - notional:.2f}")
            print(f"{'='*60}")

            confirm = input("Confirm execution? (Enter to proceed, '1' to cancel): ").strip()
            if confirm == "1":
                return False, "❌ Order cancelled by user"

        # Execute trade
        reason = f"LIMIT BUY - Filled at ${exec_price:.2f} (limit ${limit_price:.2f})"
        portfolio_manager.add_position(
            ticker=ticker,
            shares=shares,
            buy_price=exec_price,
            reason=reason,
            stop_loss=stop_loss if stop_loss > 0 else None,
        )

        self.last_execution = {
            "type": "buy_limit",
            "ticker": ticker,
            "shares": shares,
            "price": exec_price,
            "limit": limit_price,
            "timestamp": datetime.now(),
        }

        return True, f"✅ LIMIT BUY executed: {shares} {ticker} @ ${exec_price:.2f}"

    def execute_sell_limit(
        self,
        ticker: str,
        shares: float,
        limit_price: float,
        portfolio_manager,
        market_data: pd.DataFrame,
        interactive: bool = True,
        reason: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Execute a limit sell order.

        Only executes if:
        - Opening price >= limit OR
        - High of day >= limit

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to sell
            limit_price: Minimum price to accept
            portfolio_manager: PortfolioMemoryManager instance
            market_data: DataFrame with OHLCV data
            interactive: If True, ask for confirmation
            reason: Optional reason for sale

        Returns:
            Tuple of (success: bool, message: str)
        """
        if market_data.empty:
            return False, f"❌ No market data available for {ticker}"

        # Validate position exists
        position = portfolio_manager.holdings[portfolio_manager.holdings["ticker"] == ticker]
        if position.empty:
            return False, f"❌ No position found for {ticker}"

        total_shares = float(position["shares"].iloc[0])
        if shares > total_shares:
            return False, f"❌ Cannot sell {shares} shares, only own {total_shares}"

        # Get OHLC prices
        o = float(market_data.get("Open", [np.nan])[-1])
        h = float(market_data["High"].iloc[-1])
        l = float(market_data["Low"].iloc[-1])

        if np.isnan(o):
            o = float(market_data["Close"].iloc[-1])

        # Determine execution price
        exec_price = None
        if o >= limit_price:
            exec_price = o
        elif h >= limit_price:
            exec_price = limit_price
        else:
            return False, f"⚠️ Limit price ${limit_price:.2f} not reached (range: ${l:.2f}-${h:.2f})"

        exec_price = round(exec_price, 2)
        proceeds = exec_price * shares

        buy_price = float(position["buy_price"].iloc[0])
        pnl = (exec_price - buy_price) * shares
        pnl_pct = ((exec_price / buy_price) - 1) * 100

        # Interactive confirmation
        if interactive:
            print(f"\n{'='*60}")
            print(f"🔴 LIMIT SELL ORDER")
            print(f"{'='*60}")
            print(f"Ticker: {ticker}")
            print(f"Shares: {shares} of {total_shares}")
            print(f"Limit Price: ${limit_price:.2f}")
            print(f"Execution Price: ${exec_price:.2f}")
            print(f"Buy Price: ${buy_price:.2f}")
            print(f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            print(f"Proceeds: ${proceeds:.2f}")
            print(f"Cash After: ${portfolio_manager.cash + proceeds:.2f}")
            print(f"{'='*60}")

            if reason is None:
                reason_input = input("Reason for sale (or Enter to skip): ").strip()
                reason = reason_input if reason_input else "MANUAL SELL LIMIT"

            confirm = input("Confirm execution? (Enter to proceed, '1' to cancel): ").strip()
            if confirm == "1":
                return False, "❌ Order cancelled by user"

        # Execute trade
        if reason is None:
            reason = "MANUAL SELL LIMIT"

        full_reason = f"{reason} - Filled at ${exec_price:.2f} (limit ${limit_price:.2f})"
        portfolio_manager.remove_position(
            ticker=ticker, shares=shares, sell_price=exec_price, reason=full_reason
        )

        self.last_execution = {
            "type": "sell_limit",
            "ticker": ticker,
            "shares": shares,
            "price": exec_price,
            "limit": limit_price,
            "pnl": pnl,
            "timestamp": datetime.now(),
        }

        return (
            True,
            f"✅ LIMIT SELL executed: {shares} {ticker} @ ${exec_price:.2f} (P&L: ${pnl:+.2f})",
        )

    def get_last_execution(self) -> Optional[Dict]:
        """
        Get details of the last executed trade.

        Returns:
            Dict with execution details or None if no executions yet
        """
        return self.last_execution

    def fetch_market_data(self, ticker: str, days: int = 5) -> Tuple[pd.DataFrame, str]:
        """
        Fetch market data with Yahoo Finance → Stooq fallback.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of history to fetch

        Returns:
            Tuple of (DataFrame with OHLCV data, source name)
        """
        end = datetime.now()
        start = end - pd.Timedelta(days=days)

        # Try Yahoo Finance first
        if _HAS_YFINANCE:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df = yf.download(ticker, start=start, end=end, progress=False, threads=False)

                if not df.empty:
                    # Normalize to OHLCV format
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # Ensure required columns
                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col not in df.columns:
                            df[col] = np.nan

                    if "Adj Close" not in df.columns:
                        df["Adj Close"] = df["Close"]

                    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]], "yahoo"
            except Exception as e:
                print(f"[WARNING] Yahoo Finance failed for {ticker}: {e}")

        # Try Stooq fallback
        if _HAS_PDR:
            try:
                stooq_ticker = ticker
                if not ticker.startswith("^"):
                    stooq_ticker = f"{ticker.lower()}.us"

                df = pdr.DataReader(stooq_ticker, "stooq", start, end)

                if not df.empty:
                    df.columns = [col.capitalize() for col in df.columns]

                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col not in df.columns:
                            df[col] = np.nan

                    if "Adj Close" not in df.columns:
                        df["Adj Close"] = df["Close"]

                    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]], "stooq"
            except Exception as e:
                print(f"[WARNING] Stooq fallback failed for {ticker}: {e}")

        return pd.DataFrame(), "failed"

    def execute_buy(
        self,
        ticker: str,
        shares: float,
        stop_loss: Optional[float] = None,
        order_type: str = "market",
        limit_price: Optional[float] = None,
        dry_run: bool = False,
    ) -> Dict:
        """
        Execute a BUY order (simplified API for testing).

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to buy
            stop_loss: Optional stop-loss price
            order_type: "market" or "limit"
            limit_price: Required if order_type is "limit"
            dry_run: If True, simulate without actual execution

        Returns:
            dict: Execution result with success, price, cost, source, reason
        """
        # Fetch current market data (need at least 5 days for reliable data)
        df, source = self.fetch_market_data(ticker, days=5)

        if df.empty:
            return {
                "success": False,
                "reason": f"No market data available for {ticker}",
                "ticker": ticker,
                "shares": shares,
                "source": source,
            }

        # Use market execution
        exec_price = float(df["Open"].iloc[-1])
        if np.isnan(exec_price):
            exec_price = float(df["Close"].iloc[-1])

        exec_price = round(exec_price, 2)
        cost = round(shares * exec_price, 2)

        return {
            "success": True,
            "ticker": ticker,
            "shares": shares,
            "price": exec_price,
            "cost": cost,
            "stop_loss": stop_loss if stop_loss else 0.0,
            "source": source,
            "dry_run": dry_run,
            "action": "BUY",
            "reason": f"{'DRY-RUN' if dry_run else 'EXECUTED'}: Buy {shares} {ticker} @ ${exec_price:.2f}",
        }

    def execute_sell(
        self,
        ticker: str,
        shares: float,
        reason: str = "",
        order_type: str = "market",
        limit_price: Optional[float] = None,
        dry_run: bool = False,
    ) -> Dict:
        """
        Execute a SELL order (simplified API for testing).

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to sell
            reason: Reason for sale
            order_type: "market" or "limit"
            limit_price: Required if order_type is "limit"
            dry_run: If True, simulate without actual execution

        Returns:
            dict: Execution result with success, price, proceeds, source, reason
        """
        # Fetch current market data (need at least 5 days for reliable data)
        df, source = self.fetch_market_data(ticker, days=5)

        if df.empty:
            return {
                "success": False,
                "reason": f"No market data available for {ticker}",
                "ticker": ticker,
                "shares": shares,
                "source": source,
            }

        # Use market execution
        exec_price = float(df["Open"].iloc[-1])
        if np.isnan(exec_price):
            exec_price = float(df["Close"].iloc[-1])

        exec_price = round(exec_price, 2)
        proceeds = round(shares * exec_price, 2)

        return {
            "success": True,
            "ticker": ticker,
            "shares": shares,
            "price": exec_price,
            "proceeds": proceeds,
            "source": source,
            "dry_run": dry_run,
            "action": "SELL",
            "reason": f"{'DRY-RUN' if dry_run else 'EXECUTED'}: Sell {shares} {ticker} @ ${exec_price:.2f} - {reason}",
        }

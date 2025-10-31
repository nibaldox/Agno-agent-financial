"""
Portfolio Memory Manager - In-memory portfolio with CSV persistence

Handles:
- Cash management
- Position tracking
- Trade recording
- Historical snapshots
- Performance metrics
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
    print("[INFO] pandas_datareader not installed, Stooq fallback disabled")


class PortfolioMemoryManager:
    """
    In-memory portfolio manager with CSV persistence for historical tracking.

    Features:
    - Real-time position tracking
    - Automatic trade logging
    - Daily snapshot persistence
    - Historical performance analysis

    Example:
        >>> portfolio = PortfolioMemoryManager(initial_cash=100.0)
        >>> portfolio.add_position("ABEO", 10.0, 5.50, "Initial buy")
        >>> summary = portfolio.get_portfolio_summary()
        >>> print(f"ROI: {summary['roi']:.2f}%")
    """

    def __init__(self, initial_cash: float = 100.0, history_file: str | None = None):
        """
        Initialize portfolio manager.

        Args:
            initial_cash: Starting cash balance (default: $100)
            history_file: Optional custom history file path
        """
        self.cash = initial_cash
        self.initial_cash = initial_cash

        # Determine history file paths
        if history_file is None:
            # Use default location
            from pathlib import Path

            history_dir = Path(__file__).parent.parent / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = history_dir / "portfolio_history.csv"
            self.trades_file = history_dir / "trades_history.csv"
            self.daily_summary_file = history_dir / "daily_summary.csv"
        else:
            self.history_file = Path(history_file)
            self.trades_file = self.history_file.parent / "trades_history.csv"
            self.daily_summary_file = self.history_file.parent / "daily_summary.csv"

        # Portfolio holdings (in-memory DataFrame)
        self.holdings = pd.DataFrame(
            columns=[
                "ticker",
                "shares",
                "buy_price",
                "buy_date",
                "stop_loss",
                "current_price",
                "current_value",
                "pnl",
                "pnl_pct",
            ]
        )

        # Trade history (in-memory DataFrame)
        self.trades = pd.DataFrame(
            columns=["date", "ticker", "action", "shares", "price", "cost", "cash_after", "reason"]
        )

        self.last_update = datetime.now()

        # Load existing history if available
        self._load_history()

    def _load_history(self):
        """Load historical data from CSV files."""
        try:
            if self.history_file.exists():
                history_df = pd.read_csv(self.history_file)
                if not history_df.empty:
                    last_row = history_df.iloc[-1]
                    self.cash = last_row["cash"]
                    self.initial_cash = last_row["initial_cash"]
                    print(
                        f"[INFO] Historial cargado: Cash ${self.cash:.2f}, ROI {last_row['roi']:.2f}%"
                    )

            if self.trades_file.exists():
                self.trades = pd.read_csv(self.trades_file)
                print(f"[INFO] {len(self.trades)} operaciones históricas cargadas")

            if self.daily_summary_file.exists():
                daily_df = pd.read_csv(self.daily_summary_file)
                if not daily_df.empty:
                    print(f"[INFO] {len(daily_df)} días de historial cargados")
        except Exception as e:
            print(f"[WARNING] Error cargando historial: {e}")

    def update_prices(self, price_dict: Dict[str, float]):
        """
        Update current prices for all holdings.

        Args:
            price_dict: Dictionary mapping tickers to current prices
        """
        if self.holdings.empty:
            return

        for ticker, price in price_dict.items():
            if ticker in self.holdings["ticker"].values:
                idx = self.holdings[self.holdings["ticker"] == ticker].index[0]
                self.holdings.loc[idx, "current_price"] = price
                shares = self.holdings.loc[idx, "shares"]
                buy_price = self.holdings.loc[idx, "buy_price"]

                current_value = shares * price
                pnl = current_value - (shares * buy_price)
                pnl_pct = (pnl / (shares * buy_price)) * 100 if shares > 0 else 0

                self.holdings.loc[idx, "current_value"] = current_value
                self.holdings.loc[idx, "pnl"] = pnl
                self.holdings.loc[idx, "pnl_pct"] = pnl_pct

        self.last_update = datetime.now()

    def add_position(
        self,
        ticker: str,
        shares: float,
        buy_price: float,
        reason: str = "",
        stop_loss: Optional[float] = None,
    ):
        """
        Add new position to portfolio.

        Args:
            ticker: Stock symbol
            shares: Number of shares
            buy_price: Purchase price per share
            reason: Trade rationale
            stop_loss: Optional stop-loss price

        Raises:
            ValueError: If insufficient cash available
        """
        price = buy_price  # Alias for compatibility
        cost = shares * price

        if cost > self.cash:
            raise ValueError(
                f"Fondos insuficientes: ${cost:.2f} requerido, ${self.cash:.2f} disponible"
            )

        # Deduct cash
        self.cash -= cost

        # Add position
        new_position = pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "shares": shares,
                    "buy_price": price,
                    "buy_date": datetime.now().strftime("%Y-%m-%d"),
                    "stop_loss": stop_loss if stop_loss else 0.0,
                    "current_price": price,
                    "current_value": cost,
                    "pnl": 0.0,
                    "pnl_pct": 0.0,
                }
            ]
        )

        self.holdings = pd.concat([self.holdings, new_position], ignore_index=True)

        # Record trade
        self._record_trade("BUY", ticker, shares, price, cost, reason)

        print(f"[TRADE] COMPRA {shares} acciones de {ticker} @ ${price:.2f}")
        print(f"        Costo: ${cost:.2f}, Efectivo restante: ${self.cash:.2f}")

    def remove_position(self, ticker: str, shares: float, sell_price: float, reason: str = ""):
        """
        Sell position from portfolio.

        Args:
            ticker: Stock symbol
            shares: Number of shares to sell
            sell_price: Sell price per share
            reason: Trade rationale

        Raises:
            ValueError: If ticker not found or shares exceed position
        """
        price = sell_price  # Alias for compatibility
        if ticker not in self.holdings["ticker"].values:
            raise ValueError(f"Ticker {ticker} no encontrado en portfolio")

        idx = self.holdings[self.holdings["ticker"] == ticker].index[0]
        current_shares = self.holdings.loc[idx, "shares"]

        if shares > current_shares:
            raise ValueError(f"Venta excede posición: {shares} > {current_shares}")

        proceeds = shares * price
        self.cash += proceeds

        # Update or remove position
        if shares == current_shares:
            self.holdings = self.holdings[self.holdings["ticker"] != ticker].reset_index(drop=True)
        else:
            self.holdings.loc[idx, "shares"] -= shares
            self.holdings.loc[idx, "current_value"] = self.holdings.loc[idx, "shares"] * price

        # Record trade
        self._record_trade("SELL", ticker, shares, price, proceeds, reason)

        print(f"[TRADE] VENTA {shares} acciones de {ticker} @ ${price:.2f}")
        print(f"        Ingresos: ${proceeds:.2f}, Efectivo total: ${self.cash:.2f}")

    def _record_trade(
        self, action: str, ticker: str, shares: float, price: float, amount: float, reason: str
    ):
        """Record trade in history."""
        trade = pd.DataFrame(
            [
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ticker": ticker,
                    "action": action,
                    "shares": shares,
                    "price": price,
                    "cost": amount,
                    "cash_after": self.cash,
                    "reason": reason,
                }
            ]
        )

        self.trades = pd.concat([self.trades, trade], ignore_index=True)

    def get_portfolio_summary(self) -> Dict:
        """
        Get current portfolio summary.

        Returns:
            dict: Portfolio metrics including equity, ROI, positions, etc.
        """
        holdings_value = self.holdings["current_value"].sum() if not self.holdings.empty else 0
        total_equity = self.cash + holdings_value
        roi = ((total_equity - self.initial_cash) / self.initial_cash) * 100

        return {
            "cash": self.cash,
            "holdings_value": holdings_value,
            "total_equity": total_equity,
            "roi": roi,
            "num_positions": len(self.holdings),
            "initial_cash": self.initial_cash,
            "last_update": self.last_update.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def save_daily_snapshot(self):
        """Save daily portfolio snapshot to CSV files."""
        summary = self.get_portfolio_summary()

        snapshot = pd.DataFrame(
            [
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "cash": summary["cash"],
                    "holdings_value": summary["holdings_value"],
                    "total_equity": summary["total_equity"],
                    "roi": summary["roi"],
                    "num_positions": summary["num_positions"],
                    "initial_cash": summary["initial_cash"],
                }
            ]
        )

        # Save to daily summary
        if self.daily_summary_file.exists():
            existing = pd.read_csv(self.daily_summary_file)
            combined = pd.concat([existing, snapshot], ignore_index=True)
            combined.to_csv(self.daily_summary_file, index=False)
        else:
            snapshot.to_csv(self.daily_summary_file, index=False)

        # Save to history file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        snapshot.to_csv(
            self.history_file, mode="a", header=not self.history_file.exists(), index=False
        )

        # Save trades
        if not self.trades.empty:
            self.trades.to_csv(self.trades_file, index=False)

        print(f"[INFO] Snapshot diario guardado: ROI {summary['roi']:.2f}%")

    def get_historical_performance(self) -> Dict:
        """
        Get historical performance metrics.

        Returns:
            dict: Historical metrics including drawdown, best/worst days, etc.
        """
        if not self.daily_summary_file.exists():
            return {
                "total_days": 0,
                "peak_equity": self.initial_cash,
                "max_drawdown": 0.0,
                "total_trades": 0,
                "best_day": None,
                "worst_day": None,
            }

        daily_df = pd.read_csv(self.daily_summary_file)

        if daily_df.empty:
            return {
                "total_days": 0,
                "peak_equity": self.initial_cash,
                "max_drawdown": 0.0,
                "total_trades": 0,
                "best_day": None,
                "worst_day": None,
            }

        # Calculate metrics
        peak_equity = daily_df["total_equity"].max()
        daily_df["drawdown"] = ((daily_df["total_equity"] - peak_equity) / peak_equity) * 100
        max_drawdown = daily_df["drawdown"].min()

        best_day_idx = daily_df["roi"].idxmax()
        worst_day_idx = daily_df["roi"].idxmin()

        return {
            "total_days": len(daily_df),
            "peak_equity": peak_equity,
            "max_drawdown": max_drawdown,
            "total_trades": len(self.trades),
            "best_day": (
                {
                    "date": daily_df.loc[best_day_idx, "date"],
                    "roi": daily_df.loc[best_day_idx, "roi"],
                }
                if not daily_df.empty
                else None
            ),
            "worst_day": (
                {
                    "date": daily_df.loc[worst_day_idx, "date"],
                    "roi": daily_df.loc[worst_day_idx, "roi"],
                }
                if not daily_df.empty
                else None
            ),
        }

    def fetch_price_data(self, ticker: str, days: int = 5) -> pd.DataFrame:
        """
        Fetch price data with Yahoo Finance → Stooq fallback.
        Public alias for fetch_market_data() that returns just the DataFrame.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of history to fetch

        Returns:
            DataFrame with OHLCV data
        """
        df, _ = self.fetch_market_data(ticker, days)
        return df

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
                # Map ticker to Stooq format
                stooq_ticker = ticker
                if not ticker.startswith("^"):
                    stooq_ticker = f"{ticker.lower()}.us"

                df = pdr.DataReader(stooq_ticker, "stooq", start, end)

                if not df.empty:
                    # Normalize column names (Stooq uses lowercase)
                    df.columns = [col.capitalize() for col in df.columns]

                    # Ensure required columns
                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col not in df.columns:
                            df[col] = np.nan

                    if "Adj Close" not in df.columns:
                        df["Adj Close"] = df["Close"]

                    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]], "stooq"
            except Exception as e:
                print(f"[WARNING] Stooq fallback failed for {ticker}: {e}")

        # Return empty DataFrame if both fail
        print(f"[ERROR] Could not fetch data for {ticker}")
        return pd.DataFrame(), "empty"

    def update_prices_from_market(self) -> Dict[str, str]:
        """
        Update all positions with current market prices using data fetching with fallback.

        Returns:
            Dict mapping tickers to data sources
        """
        sources = {}

        if self.holdings.empty:
            return sources

        for ticker in self.holdings["ticker"].unique():
            df, source = self.fetch_market_data(ticker, days=5)

            if not df.empty and "Close" in df.columns:
                current_price = float(df["Close"].iloc[-1])
                self.update_prices({ticker: current_price})
                sources[ticker] = source
                print(f"[INFO] {ticker}: ${current_price:.2f} (source: {source})")
            else:
                sources[ticker] = "failed"
                print(f"[WARNING] Could not update price for {ticker}")

        return sources

    def check_stop_losses(self) -> list:
        """
        Check all positions for stop-loss triggers and execute sales.
        Uses current_price from holdings if available (for testing),
        otherwise fetches live market data.

        Returns:
            List of dicts with triggered stop-loss details
        """
        triggered_stops = []

        if self.holdings.empty:
            return triggered_stops

        for idx, position in self.holdings.iterrows():
            ticker = position["ticker"]
            shares = float(position["shares"])
            buy_price = float(position["buy_price"])
            stop_loss = float(position["stop_loss"])
            current_price = float(position["current_price"])

            # Skip if no stop-loss set
            if stop_loss <= 0:
                continue

            # For testing: use current_price if set
            if current_price > 0 and current_price != buy_price:
                low = current_price
                open_price = current_price
                source = "manual"
            else:
                # Fetch current market data
                df, source = self.fetch_market_data(ticker, days=1)

                if df.empty:
                    print(f"[WARNING] No data for {ticker}, cannot check stop-loss")
                    continue

                # Check if low of day hit stop-loss
                low = float(df["Low"].iloc[-1])
                open_price = (
                    float(df["Open"].iloc[-1])
                    if "Open" in df.columns
                    else float(df["Close"].iloc[-1])
                )

                if np.isnan(open_price):
                    open_price = float(df["Close"].iloc[-1])

            if low <= stop_loss:
                # Determine execution price
                exec_price = open_price if open_price <= stop_loss else stop_loss
                exec_price = round(exec_price, 2)

                pnl = (exec_price - buy_price) * shares
                pnl_pct = ((exec_price / buy_price) - 1) * 100

                print(f"\n{'='*60}")
                print(f"🔴 STOP-LOSS TRIGGERED")
                print(f"{'='*60}")
                print(f"Ticker: {ticker}")
                print(f"Shares: {shares}")
                print(f"Stop-Loss: ${stop_loss:.2f}")
                print(f"Low of Day: ${low:.2f}")
                print(f"Execution Price: ${exec_price:.2f}")
                print(f"Buy Price: ${buy_price:.2f}")
                print(f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
                print(f"Data Source: {source}")
                print(f"{'='*60}\n")

                # Execute automatic sale
                reason = f"STOP-LOSS TRIGGERED - Filled at ${exec_price:.2f} (stop ${stop_loss:.2f}, low ${low:.2f})"
                self.remove_position(ticker, shares, exec_price, reason)

                triggered_stops.append(
                    {
                        "ticker": ticker,
                        "shares": shares,
                        "price": exec_price,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "reason": reason,
                    }
                )

        return triggered_stops

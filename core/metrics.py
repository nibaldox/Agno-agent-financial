"""
Advanced Metrics Calculator

Calculates professional financial metrics:
- Sharpe Ratio (period & annualized)
- Sortino Ratio (downside risk adjusted)
- CAPM Analysis (Beta, Alpha vs benchmark)
- Maximum Drawdown
- Volatility Metrics
- Win/Loss Statistics
- Consecutive Performance Tracking

Based on trading_script.py metrics calculations.
"""

import warnings
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import yfinance as yf

    _HAS_YFINANCE = True
except ImportError:
    _HAS_YFINANCE = False


class MetricsCalculator:
    """
    Calculate advanced financial metrics for portfolio analysis.

    Features:
    - Risk-adjusted returns (Sharpe, Sortino)
    - CAPM analysis vs benchmark
    - Drawdown analysis
    - Volatility metrics
    - Win/loss statistics

    Example:
        >>> calculator = MetricsCalculator()
        >>> metrics = calculator.calculate_all_metrics(portfolio_df, benchmark="^GSPC")
        >>> print(f"Sharpe: {metrics['sharpe_ratio']:.2f}")
    """

    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize metrics calculator.

        Args:
            risk_free_rate: Annual risk-free rate (default: 5% = 0.05)
        """
        self.risk_free_rate = risk_free_rate
        self.rf_daily = (1 + risk_free_rate) ** (1 / 252) - 1  # Daily risk-free rate

    def calculate_sharpe_ratio(self, returns: pd.Series, period: str = "daily") -> Dict[str, float]:
        """
        Calculate Sharpe Ratio (risk-adjusted return).

        Sharpe = (Return - RiskFreeRate) / Volatility

        Args:
            returns: Series of returns
            period: "daily" or "annual"

        Returns:
            dict: {'sharpe_period': float, 'sharpe_annual': float}
        """
        if len(returns) < 2:
            return {"sharpe_period": np.nan, "sharpe_annual": np.nan}

        mean_return = returns.mean()
        std_return = returns.std()

        if std_return == 0:
            return {"sharpe_period": np.nan, "sharpe_annual": np.nan}

        # Period Sharpe
        sharpe_period = (mean_return - self.rf_daily) / std_return

        # Annualized Sharpe
        sharpe_annual = ((mean_return - self.rf_daily) / std_return) * np.sqrt(252)

        return {"sharpe_period": sharpe_period, "sharpe_annual": sharpe_annual}

    def calculate_sortino_ratio(
        self, returns: pd.Series, period: str = "daily"
    ) -> Dict[str, float]:
        """
        Calculate Sortino Ratio (downside risk-adjusted return).

        Sortino = (Return - RiskFreeRate) / DownsideDeviation
        Only considers negative returns in volatility calculation.

        Args:
            returns: Series of returns
            period: "daily" or "annual"

        Returns:
            dict: {'sortino_period': float, 'sortino_annual': float}
        """
        if len(returns) < 2:
            return {"sortino_period": np.nan, "sortino_annual": np.nan}

        mean_return = returns.mean()

        # Downside deviation (only negative returns)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0

        if downside_std == 0:
            return {"sortino_period": np.nan, "sortino_annual": np.nan}

        # Period Sortino
        n_days = len(returns)
        period_return = returns.sum()
        sortino_period = (period_return - self.rf_daily * n_days) / (downside_std * np.sqrt(n_days))

        # Annualized Sortino
        sortino_annual = ((mean_return - self.rf_daily) / downside_std) * np.sqrt(252)

        return {
            "sortino_period": sortino_period,
            "sortino_annual": sortino_annual,
            "downside_std": downside_std,
        }

    def calculate_capm_metrics(
        self, portfolio_returns: pd.Series, benchmark_ticker: str = "^GSPC"
    ) -> Dict[str, float]:
        """
        Calculate CAPM metrics (Beta, Alpha) vs benchmark.

        Beta = Covariance(Portfolio, Benchmark) / Variance(Benchmark)
        Alpha = Portfolio Return - (RiskFreeRate + Beta * (Benchmark Return - RiskFreeRate))

        Args:
            portfolio_returns: Series of portfolio returns
            benchmark_ticker: Benchmark ticker (default: S&P 500)

        Returns:
            dict: {'beta': float, 'alpha': float, 'alpha_annual': float}
        """
        if len(portfolio_returns) < 2 or not _HAS_YFINANCE:
            return {"beta": np.nan, "alpha": np.nan, "alpha_annual": np.nan}

        try:
            # Fetch benchmark data
            start_date = portfolio_returns.index.min() - pd.Timedelta(days=1)
            end_date = portfolio_returns.index.max() + pd.Timedelta(days=1)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                benchmark_data = yf.download(
                    benchmark_ticker, start=start_date, end=end_date, progress=False
                )

            if benchmark_data.empty:
                return {"beta": np.nan, "alpha": np.nan, "alpha_annual": np.nan}

            # Calculate benchmark returns
            if isinstance(benchmark_data.columns, pd.MultiIndex):
                benchmark_data.columns = benchmark_data.columns.get_level_values(0)

            benchmark_prices = benchmark_data["Close"]
            benchmark_returns = benchmark_prices.pct_change().dropna()

            # Align returns
            aligned_portfolio = portfolio_returns.reindex(benchmark_returns.index).dropna()
            aligned_benchmark = benchmark_returns.reindex(aligned_portfolio.index).dropna()

            if len(aligned_portfolio) < 2 or len(aligned_benchmark) < 2:
                return {"beta": np.nan, "alpha": np.nan, "alpha_annual": np.nan}

            # Calculate Beta
            cov_matrix = np.cov(aligned_portfolio, aligned_benchmark)
            beta = cov_matrix[0, 1] / cov_matrix[1, 1] if cov_matrix[1, 1] != 0 else np.nan

            # Calculate Alpha
            avg_portfolio_ret = aligned_portfolio.mean()
            avg_benchmark_ret = aligned_benchmark.mean()

            alpha = (avg_portfolio_ret - self.rf_daily) - beta * (avg_benchmark_ret - self.rf_daily)
            alpha_annual = alpha * 252  # Annualized

            return {"beta": beta, "alpha": alpha, "alpha_annual": alpha_annual}

        except Exception as e:
            print(f"[WARNING] CAPM calculation failed: {e}")
            return {"beta": np.nan, "alpha": np.nan, "alpha_annual": np.nan}

    def calculate_max_drawdown(self, equity_series: pd.Series) -> Dict[str, any]:
        """
        Calculate maximum drawdown.

        Drawdown = (Current Value - Peak Value) / Peak Value

        Args:
            equity_series: Series of equity values over time

        Returns:
            dict: {
                'max_drawdown': float (as percentage),
                'max_drawdown_date': datetime,
                'peak_value': float,
                'trough_value': float
            }
        """
        if len(equity_series) < 2:
            return {
                "max_drawdown": 0.0,
                "max_drawdown_date": None,
                "peak_value": 0.0,
                "trough_value": 0.0,
            }

        # Calculate running maximum
        running_max = equity_series.expanding().max()

        # Calculate drawdown
        drawdown = (equity_series - running_max) / running_max * 100

        # Find maximum drawdown
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()

        peak_idx = equity_series[:max_dd_date].idxmax()
        peak_value = equity_series[peak_idx]
        trough_value = equity_series[max_dd_date]

        return {
            "max_drawdown": max_dd,
            "max_drawdown_date": max_dd_date,
            "peak_value": peak_value,
            "trough_value": trough_value,
        }

    def calculate_volatility_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """
        Calculate volatility metrics.

        Args:
            returns: Series of returns

        Returns:
            dict: {
                'daily_volatility': float,
                'annual_volatility': float,
                'mean_return': float,
                'std_return': float
            }
        """
        if len(returns) < 2:
            return {
                "daily_volatility": 0.0,
                "annual_volatility": 0.0,
                "mean_return": 0.0,
                "std_return": 0.0,
            }

        mean_return = returns.mean()
        std_return = returns.std()

        # Annualized volatility
        annual_vol = std_return * np.sqrt(252) * 100  # As percentage

        return {
            "daily_volatility": std_return,
            "annual_volatility": annual_vol,
            "mean_return": mean_return,
            "std_return": std_return,
        }

    def calculate_win_loss_stats(self, trades_df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate win/loss statistics from trade history.

        Args:
            trades_df: DataFrame with 'PnL' column

        Returns:
            dict: {
                'total_trades': int,
                'winning_trades': int,
                'losing_trades': int,
                'win_rate': float (percentage),
                'avg_win': float,
                'avg_loss': float,
                'largest_win': float,
                'largest_loss': float,
                'profit_factor': float
            }
        """
        if trades_df.empty or "PnL" not in trades_df.columns:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
                "profit_factor": 0.0,
            }

        # Filter completed trades (with PnL)
        completed = trades_df[trades_df["PnL"].notna() & (trades_df["PnL"] != 0)]

        if completed.empty:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
                "profit_factor": 0.0,
            }

        wins = completed[completed["PnL"] > 0]
        losses = completed[completed["PnL"] < 0]

        total_trades = len(completed)
        winning_trades = len(wins)
        losing_trades = len(losses)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        avg_win = wins["PnL"].mean() if not wins.empty else 0.0
        avg_loss = losses["PnL"].mean() if not losses.empty else 0.0

        largest_win = wins["PnL"].max() if not wins.empty else 0.0
        largest_loss = losses["PnL"].min() if not losses.empty else 0.0

        total_wins = wins["PnL"].sum() if not wins.empty else 0.0
        total_losses = abs(losses["PnL"].sum()) if not losses.empty else 0.0
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0.0

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "profit_factor": profit_factor,
        }

    def calculate_consecutive_performance(self, trades_df: pd.DataFrame) -> Dict[str, int]:
        """
        Calculate consecutive wins/losses.

        Args:
            trades_df: DataFrame with 'PnL' column

        Returns:
            dict: {
                'max_consecutive_wins': int,
                'max_consecutive_losses': int,
                'current_streak': int (positive=wins, negative=losses)
            }
        """
        if trades_df.empty or "PnL" not in trades_df.columns:
            return {"max_consecutive_wins": 0, "max_consecutive_losses": 0, "current_streak": 0}

        completed = trades_df[trades_df["PnL"].notna() & (trades_df["PnL"] != 0)]

        if completed.empty:
            return {"max_consecutive_wins": 0, "max_consecutive_losses": 0, "current_streak": 0}

        # Determine win/loss for each trade
        results = (completed["PnL"] > 0).astype(int)  # 1 = win, 0 = loss

        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0

        for result in results:
            if result == 1:  # Win
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:  # Loss
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)

        # Current streak
        if len(results) > 0:
            current_streak = current_wins if results.iloc[-1] == 1 else -current_losses
        else:
            current_streak = 0

        return {
            "max_consecutive_wins": max_wins,
            "max_consecutive_losses": max_losses,
            "current_streak": current_streak,
        }

    def calculate_all_metrics(
        self,
        equity_series: pd.Series,
        trades_df: Optional[pd.DataFrame] = None,
        benchmark_ticker: str = "^GSPC",
    ) -> Dict[str, any]:
        """
        Calculate all metrics at once.

        Args:
            equity_series: Series of equity values over time
            trades_df: Optional DataFrame of completed trades
            benchmark_ticker: Benchmark ticker for CAPM

        Returns:
            dict: Complete metrics dictionary
        """
        # Calculate returns
        returns = equity_series.pct_change().dropna()

        # Calculate all metrics
        sharpe = self.calculate_sharpe_ratio(returns)
        sortino = self.calculate_sortino_ratio(returns)
        capm = self.calculate_capm_metrics(returns, benchmark_ticker)
        drawdown = self.calculate_max_drawdown(equity_series)
        volatility = self.calculate_volatility_metrics(returns)

        metrics = {**sharpe, **sortino, **capm, **drawdown, **volatility}

        # Add trade statistics if available
        if trades_df is not None:
            win_loss = self.calculate_win_loss_stats(trades_df)
            consecutive = self.calculate_consecutive_performance(trades_df)
            metrics.update(win_loss)
            metrics.update(consecutive)

        return metrics

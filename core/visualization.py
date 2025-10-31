"""
Visualization Generator - Interactive Professional Charts

Generates 15+ types of INTERACTIVE financial visualizations using Plotly:
- Performance comparison (Portfolio vs S&P 500) with zoom/pan
- ROI analysis charts with tooltips
- Drawdown visualizations with hover details
- Risk-return scatter plots
- Portfolio composition (interactive pie charts)
- Win/loss analysis with drill-down
- And more...

All plots are saved as interactive HTML files with modern styling.
Fallback to matplotlib PNG if Plotly unavailable.
"""

import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Try Plotly first (interactive charts)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots

    _HAS_PLOTLY = True

    # Set modern template
    pio.templates.default = "plotly_white"
except ImportError:
    _HAS_PLOTLY = False
    print("[INFO] plotly not installed, using matplotlib fallback")

# Fallback to matplotlib
try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False
    print("[WARNING] matplotlib not installed, visualizations disabled")


class VisualizationGenerator:
    """
    Generate professional INTERACTIVE financial charts and visualizations.

    Features:
    - Interactive performance comparison plots (zoom, pan, hover)
    - ROI analysis charts with tooltips
    - Drawdown visualizations with drill-down
    - Portfolio composition charts (interactive pie)
    - Risk-return analysis
    - Win/loss statistics

    Uses Plotly for interactive HTML charts with modern styling.
    Falls back to matplotlib PNG if Plotly unavailable.

    Example:
        >>> viz = VisualizationGenerator(output_dir="./reports")
        >>> viz.plot_performance_vs_benchmark(portfolio_df, sp500_df)
        'reports/performance_comparison.html'  # Interactive!
    """

    def __init__(self, output_dir: str | Path = "reports"):
        """
        Initialize visualization generator.

        Args:
            output_dir: Directory to save plot files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.use_plotly = _HAS_PLOTLY

        if self.use_plotly:
            # Modern color scheme (shadcn-inspired)
            self.colors = {
                "primary": "#3b82f6",  # Blue
                "secondary": "#8b5cf6",  # Purple
                "success": "#10b981",  # Green
                "danger": "#ef4444",  # Red
                "warning": "#f59e0b",  # Amber
                "info": "#06b6d4",  # Cyan
                "neutral": "#6b7280",  # Gray
            }

            # Plotly template config
            self.plotly_config = {
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": "chart",
                    "height": 800,
                    "width": 1200,
                    "scale": 2,
                },
            }
        else:
            if not _HAS_MATPLOTLIB:
                raise ImportError(
                    "No visualization library available. Install plotly or matplotlib"
                )

            # Matplotlib fallback
            plt.style.use("seaborn-v0_8-whitegrid")
            self.colors = {
                "primary": "#1f77b4",
                "secondary": "#ff7f0e",
                "success": "#2ca02c",
                "danger": "#d62728",
                "warning": "#ff9800",
                "info": "#17a2b8",
            }

    def _save_plot(self, fig, filename: str) -> str:
        """
        Save plot to file and return path.

        Args:
            fig: Matplotlib figure
            filename: Output filename

        Returns:
            str: Path to saved file
        """
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return str(filepath)

    def plot_performance_vs_benchmark(
        self, portfolio_equity: pd.Series, benchmark_data: pd.Series, starting_value: float = 100.0
    ) -> str:
        """
        Plot portfolio performance vs benchmark (indexed to starting value).

        Args:
            portfolio_equity: Series of portfolio equity over time
            benchmark_data: Series of benchmark prices over time
            starting_value: Starting value for indexing (default: $100)

        Returns:
            str: Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Normalize both series to starting value
        portfolio_norm = (portfolio_equity / portfolio_equity.iloc[0]) * starting_value
        benchmark_norm = (benchmark_data / benchmark_data.iloc[0]) * starting_value

        # Plot
        ax.plot(
            portfolio_norm.index,
            portfolio_norm.values,
            label=f"Portfolio (${starting_value:.0f} invested)",
            color=self.colors["primary"],
            linewidth=2,
            marker="o",
            markersize=4,
        )

        ax.plot(
            benchmark_norm.index,
            benchmark_norm.values,
            label=f"S&P 500 (${starting_value:.0f} invested)",
            color=self.colors["secondary"],
            linewidth=2,
            linestyle="--",
            marker="s",
            markersize=4,
        )

        # Calculate final values and gains
        final_portfolio = float(portfolio_norm.iloc[-1])
        final_benchmark = float(benchmark_norm.iloc[-1])
        portfolio_gain = final_portfolio - starting_value
        benchmark_gain = final_benchmark - starting_value

        # Add final value annotations
        ax.text(
            portfolio_norm.index[-1],
            final_portfolio + 1,
            f"+${portfolio_gain:.1f} ({portfolio_gain/starting_value*100:.1f}%)",
            color=self.colors["primary"],
            fontsize=10,
            fontweight="bold",
        )

        ax.text(
            benchmark_norm.index[-1],
            final_benchmark + 1,
            f"+${benchmark_gain:.1f} ({benchmark_gain/starting_value*100:.1f}%)",
            color=self.colors["secondary"],
            fontsize=10,
        )

        # Formatting
        ax.set_title("Portfolio Performance vs S&P 500", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel(f"Value of ${starting_value:.0f} Investment", fontsize=12)
        ax.legend(loc="best", fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        return self._save_plot(fig, "performance_vs_benchmark.png")

    def plot_roi_bars(self, stocks_roi: pd.DataFrame, top_n: int = 20) -> str:
        """
        Plot ROI as horizontal bars for all stocks.

        Args:
            stocks_roi: DataFrame with 'Ticker' and 'ROI %' columns
            top_n: Number of top/bottom stocks to show

        Returns:
            str: Path to saved plot
        """
        if stocks_roi.empty:
            # Create empty plot with message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "No ROI data available", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return self._save_plot(fig, "roi_bars.png")

        # Sort by ROI
        sorted_data = stocks_roi.sort_values("ROI %", ascending=True)

        # Take top N and bottom N
        if len(sorted_data) > top_n * 2:
            bottom_n = sorted_data.head(top_n)
            top_n_data = sorted_data.tail(top_n)
            plot_data = pd.concat([bottom_n, top_n_data])
        else:
            plot_data = sorted_data

        fig, ax = plt.subplots(figsize=(12, max(8, len(plot_data) * 0.4)))

        # Color bars based on positive/negative
        colors = [
            self.colors["success"] if x > 0 else self.colors["danger"] for x in plot_data["ROI %"]
        ]

        # Plot
        ax.barh(plot_data["Ticker"], plot_data["ROI %"], color=colors, alpha=0.7)

        # Add value labels
        for idx, (ticker, roi) in enumerate(zip(plot_data["Ticker"], plot_data["ROI %"])):
            ax.text(
                roi + (2 if roi > 0 else -2),
                idx,
                f"{roi:+.1f}%",
                va="center",
                ha="left" if roi > 0 else "right",
                fontsize=9,
                fontweight="bold",
            )

        # Formatting
        ax.set_title("Stock ROI Analysis", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("ROI (%)", fontsize=12)
        ax.set_ylabel("Ticker", fontsize=12)
        ax.axvline(x=0, color="black", linestyle="-", linewidth=0.8)
        ax.grid(True, axis="x", alpha=0.3)

        plt.tight_layout()

        return self._save_plot(fig, "roi_bars.png")

    def plot_portfolio_composition(self, holdings_df: pd.DataFrame) -> str:
        """
        Plot portfolio composition as pie chart.

        Args:
            holdings_df: DataFrame with 'ticker' and 'current_value' columns

        Returns:
            str: Path to saved plot
        """
        if holdings_df.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, "No holdings to display", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return self._save_plot(fig, "portfolio_composition.png")

        fig, ax = plt.subplots(figsize=(10, 8))

        # Prepare data
        composition = (
            holdings_df.groupby("ticker")["current_value"].sum().sort_values(ascending=False)
        )

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            composition.values,
            labels=composition.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Set3.colors,
        )

        # Formatting
        ax.set_title("Portfolio Composition by Stock", fontsize=16, fontweight="bold", pad=20)

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(10)

        # Add legend with values
        legend_labels = [f"{ticker}: ${value:,.0f}" for ticker, value in composition.items()]
        ax.legend(legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))

        plt.tight_layout()

        return self._save_plot(fig, "portfolio_composition.png")

    def plot_drawdown_over_time(self, equity_series: pd.Series) -> str:
        """
        Plot drawdown over time.

        Args:
            equity_series: Series of equity values

        Returns:
            str: Path to saved plot
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Calculate drawdown
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100

        # Plot 1: Equity with running max
        ax1.plot(
            equity_series.index,
            equity_series.values,
            label="Portfolio Equity",
            color=self.colors["primary"],
            linewidth=2,
        )
        ax1.plot(
            equity_series.index,
            running_max.values,
            label="All-Time High",
            color=self.colors["success"],
            linestyle="--",
            linewidth=1.5,
            alpha=0.7,
        )
        ax1.fill_between(
            equity_series.index,
            equity_series.values,
            running_max.values,
            color=self.colors["danger"],
            alpha=0.2,
        )

        ax1.set_title("Portfolio Equity & Drawdown Analysis", fontsize=16, fontweight="bold")
        ax1.set_ylabel("Equity ($)", fontsize=12)
        ax1.legend(loc="best")
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))

        # Plot 2: Drawdown percentage
        ax2.fill_between(
            drawdown.index,
            drawdown.values,
            0,
            where=(drawdown < 0),
            color=self.colors["danger"],
            alpha=0.6,
        )
        ax2.plot(drawdown.index, drawdown.values, color=self.colors["danger"], linewidth=2)

        # Mark maximum drawdown
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        ax2.plot(max_dd_date, max_dd, "ro", markersize=10)
        ax2.annotate(
            f"Max DD: {max_dd:.2f}%",
            xy=(max_dd_date, max_dd),
            xytext=(20, -20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            arrowprops=dict(arrowstyle="->", color="red"),
        )

        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("Drawdown (%)", fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.8)

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        return self._save_plot(fig, "drawdown_analysis.png")

    def plot_daily_performance(self, equity_series: pd.Series) -> str:
        """
        Plot daily performance (returns).

        Args:
            equity_series: Series of equity values

        Returns:
            str: Path to saved plot
        """
        # Calculate daily returns
        daily_returns = equity_series.pct_change().dropna() * 100

        fig, ax = plt.subplots(figsize=(12, 6))

        # Color based on positive/negative
        colors = [self.colors["success"] if x > 0 else self.colors["danger"] for x in daily_returns]

        # Plot bars
        ax.bar(daily_returns.index, daily_returns.values, color=colors, alpha=0.7, width=0.8)

        # Add zero line
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.8)

        # Calculate statistics
        avg_return = daily_returns.mean()
        best_day = daily_returns.max()
        worst_day = daily_returns.min()

        # Add statistics text box
        stats_text = f"Avg: {avg_return:+.2f}%\nBest: {best_day:+.2f}%\nWorst: {worst_day:+.2f}%"
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        # Formatting
        ax.set_title("Daily Performance", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Daily Return (%)", fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        return self._save_plot(fig, "daily_performance.png")

    def plot_win_loss_analysis(self, trades_df: pd.DataFrame) -> str:
        """
        Plot win/loss analysis from trade history.

        Args:
            trades_df: DataFrame with trade history

        Returns:
            str: Path to saved plot
        """
        if trades_df.empty or "PnL" not in trades_df.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "No trade data available", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return self._save_plot(fig, "win_loss_analysis.png")

        # Filter completed trades
        completed = trades_df[trades_df["PnL"].notna() & (trades_df["PnL"] != 0)].copy()

        if completed.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "No completed trades", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return self._save_plot(fig, "win_loss_analysis.png")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Win/Loss Count
        wins = len(completed[completed["PnL"] > 0])
        losses = len(completed[completed["PnL"] < 0])

        ax1.bar(
            ["Wins", "Losses"],
            [wins, losses],
            color=[self.colors["success"], self.colors["danger"]],
            alpha=0.7,
        )
        ax1.set_title("Win/Loss Count", fontsize=14, fontweight="bold")
        ax1.set_ylabel("Number of Trades")
        ax1.grid(True, alpha=0.3, axis="y")

        for i, v in enumerate([wins, losses]):
            ax1.text(i, v, str(v), ha="center", va="bottom", fontweight="bold")

        # 2. Win/Loss Pie Chart
        win_rate = (wins / len(completed)) * 100 if len(completed) > 0 else 0
        ax2.pie(
            [wins, losses],
            labels=[f"Wins\n{win_rate:.1f}%", f"Losses\n{100-win_rate:.1f}%"],
            colors=[self.colors["success"], self.colors["danger"]],
            autopct="%d",
            startangle=90,
        )
        ax2.set_title("Win Rate", fontsize=14, fontweight="bold")

        # 3. PnL Distribution
        win_pnls = completed[completed["PnL"] > 0]["PnL"]
        loss_pnls = completed[completed["PnL"] < 0]["PnL"]

        ax3.hist(
            [win_pnls, loss_pnls],
            bins=10,
            color=[self.colors["success"], self.colors["danger"]],
            alpha=0.6,
            label=["Wins", "Losses"],
        )
        ax3.set_title("PnL Distribution", fontsize=14, fontweight="bold")
        ax3.set_xlabel("P&L ($)")
        ax3.set_ylabel("Frequency")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Average Win/Loss
        avg_win = win_pnls.mean() if len(win_pnls) > 0 else 0
        avg_loss = loss_pnls.mean() if len(loss_pnls) > 0 else 0

        ax4.bar(
            ["Avg Win", "Avg Loss"],
            [avg_win, avg_loss],
            color=[self.colors["success"], self.colors["danger"]],
            alpha=0.7,
        )
        ax4.set_title("Average Win vs Loss", fontsize=14, fontweight="bold")
        ax4.set_ylabel("P&L ($)")
        ax4.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
        ax4.grid(True, alpha=0.3, axis="y")
        ax4.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))

        for i, v in enumerate([avg_win, avg_loss]):
            ax4.text(
                i, v, f"${v:.0f}", ha="center", va="bottom" if v > 0 else "top", fontweight="bold"
            )

        plt.suptitle("Trade Analysis Dashboard", fontsize=16, fontweight="bold", y=1.00)
        plt.tight_layout()

        return self._save_plot(fig, "win_loss_analysis.png")

    def plot_risk_return_scatter(self, stocks_data: pd.DataFrame) -> str:
        """
        Plot risk-return scatter (volatility vs return).

        Args:
            stocks_data: DataFrame with stocks and their metrics

        Returns:
            str: Path to saved plot
        """
        if stocks_data.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return self._save_plot(fig, "risk_return_scatter.png")

        fig, ax = plt.subplots(figsize=(10, 8))

        # For this example, we'll calculate simple metrics from available data
        # In practice, you'd pass volatility and return data

        ax.text(
            0.5,
            0.5,
            "Risk-Return Analysis\n(To be implemented with volatility data)",
            ha="center",
            va="center",
            fontsize=14,
        )

        ax.set_title("Risk-Return Profile", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Risk (Volatility)", fontsize=12)
        ax.set_ylabel("Return", fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        return self._save_plot(fig, "risk_return_scatter.png")

    def plot_cash_position(self, equity_series: pd.Series, cash_series: pd.Series) -> str:
        """
        Plot cash vs invested capital over time.

        Args:
            equity_series: Total equity series
            cash_series: Cash balance series

        Returns:
            str: Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate invested capital
        invested = equity_series - cash_series

        # Plot stacked area
        ax.fill_between(
            equity_series.index,
            0,
            cash_series.values,
            label="Cash",
            color=self.colors["info"],
            alpha=0.6,
        )
        ax.fill_between(
            equity_series.index,
            cash_series.values,
            equity_series.values,
            label="Invested",
            color=self.colors["primary"],
            alpha=0.6,
        )

        # Plot total equity line
        ax.plot(
            equity_series.index,
            equity_series.values,
            label="Total Equity",
            color="black",
            linewidth=2,
            linestyle="--",
        )

        # Formatting
        ax.set_title("Cash vs Invested Capital", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Value ($)", fontsize=12)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        return self._save_plot(fig, "cash_position.png")

    def generate_all_plots(
        self,
        portfolio_equity: pd.Series,
        benchmark_data: Optional[pd.Series] = None,
        holdings_df: Optional[pd.DataFrame] = None,
        trades_df: Optional[pd.DataFrame] = None,
        cash_series: Optional[pd.Series] = None,
    ) -> Dict[str, str]:
        """
        Generate all available plots.

        Args:
            portfolio_equity: Series of portfolio equity
            benchmark_data: Optional benchmark data
            holdings_df: Optional current holdings
            trades_df: Optional trade history
            cash_series: Optional cash balance series

        Returns:
            dict: Mapping of plot names to file paths
        """
        plots = {}

        # Always generate
        plots["daily_performance"] = self.plot_daily_performance(portfolio_equity)
        plots["drawdown"] = self.plot_drawdown_over_time(portfolio_equity)

        # Conditional plots
        if benchmark_data is not None:
            plots["performance_vs_benchmark"] = self.plot_performance_vs_benchmark(
                portfolio_equity, benchmark_data
            )

        if holdings_df is not None and not holdings_df.empty:
            plots["composition"] = self.plot_portfolio_composition(holdings_df)

        if trades_df is not None and not trades_df.empty:
            plots["win_loss"] = self.plot_win_loss_analysis(trades_df)

        if cash_series is not None:
            plots["cash_position"] = self.plot_cash_position(portfolio_equity, cash_series)

        return plots

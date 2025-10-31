"""
Interactive Visualization Generator - Plotly-based Charts

Generates INTERACTIVE financial visualizations using Plotly:
- Zoom, pan, hover tooltips on all charts
- Modern styling (shadcn-inspired colors)
- Responsive HTML charts
- Export to PNG/SVG capability
- Dark mode support

This is the NEW preferred visualization system.
Falls back to matplotlib if Plotly unavailable.
"""

import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    warnings.warn("Plotly not installed. Install with: pip install plotly")


class InteractiveVisualizationGenerator:
    """
    Generate interactive Plotly-based financial visualizations.

    Modern, responsive charts with:
    - Zoom/pan capabilities
    - Hover tooltips with exact values
    - Export to PNG/SVG
    - Dark mode support
    - shadcn-inspired color scheme
    """

    def __init__(self, output_dir: str | Path = "reports/charts"):
        """Initialize with output directory for HTML charts."""
        if not HAS_PLOTLY:
            raise ImportError(
                "Plotly required for interactive charts.\n" "Install with: pip install plotly"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Modern color palette (shadcn-inspired)
        self.colors = {
            "primary": "#3b82f6",  # Blue - main portfolio
            "secondary": "#8b5cf6",  # Purple - benchmark
            "success": "#10b981",  # Green - positive
            "danger": "#ef4444",  # Red - negative
            "warning": "#f59e0b",  # Amber - warning
            "info": "#06b6d4",  # Cyan - info
            "neutral": "#6b7280",  # Gray - neutral
            "slate": {
                50: "#f8fafc",
                100: "#f1f5f9",
                200: "#e2e8f0",
                300: "#cbd5e1",
                400: "#94a3b8",
                500: "#64748b",
                600: "#475569",
                700: "#334155",
                800: "#1e293b",
                900: "#0f172a",
            },
        }

        # Common layout configuration (transparent backgrounds for dark mode compatibility)
        self.common_layout = dict(
            font=dict(
                family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size=12,
                color="#64748b",  # Neutral gray (readable in both modes)
            ),
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper (entire chart)
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="rgba(0,0,0,0.9)",  # Dark background for tooltips
                font_size=13,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                font_color="white",
            ),
            margin=dict(l=60, r=40, t=80, b=60),
        )

        # Common axis styling (to be merged separately)
        self.axis_style = dict(
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.3)",  # Subtle grid (visible in both modes)
            zeroline=False,
            linecolor="rgba(148, 163, 184, 0.4)",  # Subtle axis lines
        )

        # Plotly config (toolbar options)
        self.config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "chart",
                "height": 900,
                "width": 1400,
                "scale": 2,
            },
        }

    def _save_chart(self, fig: go.Figure, filename: str) -> str:
        """Save Plotly figure as HTML with embedded JavaScript."""
        filepath = self.output_dir / filename
        fig.write_html(
            str(filepath),
            config=self.config,
            include_plotlyjs="cdn",  # Use CDN for smaller file size
            full_html=True,
        )
        return str(filepath)

    def plot_daily_performance(
        self, portfolio_equity: pd.Series, benchmark_data: Optional[pd.Series] = None
    ) -> str:
        """
        Interactive daily performance chart with portfolio vs benchmark.

        Features:
        - Dual Y-axis for portfolio and benchmark
        - Zoom/pan capabilities
        - Hover tooltips with exact values
        - Toggle visibility of series

        Args:
            portfolio_equity: Portfolio equity series (indexed by date)
            benchmark_data: Optional benchmark series for comparison

        Returns:
            str: Path to saved HTML file
        """
        fig = make_subplots(specs=[[{"secondary_y": False}]])

        # Normalize to starting value of 100 for comparison
        portfolio_norm = (portfolio_equity / portfolio_equity.iloc[0]) * 100

        # Add portfolio trace
        fig.add_trace(
            go.Scatter(
                x=portfolio_norm.index,
                y=portfolio_norm.values,
                name="Portfolio",
                line=dict(color=self.colors["primary"], width=3),
                fill="tozeroy",
                fillcolor=f"rgba(59, 130, 246, 0.1)",  # Light blue fill
                hovertemplate="<b>Portfolio</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>",
            )
        )

        # Add benchmark if provided
        if benchmark_data is not None and not benchmark_data.empty:
            benchmark_norm = (benchmark_data / benchmark_data.iloc[0]) * 100
            fig.add_trace(
                go.Scatter(
                    x=benchmark_norm.index,
                    y=benchmark_norm.values,
                    name="S&P 500",
                    line=dict(color=self.colors["secondary"], width=2, dash="dash"),
                    hovertemplate="<b>S&P 500</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>",
                )
            )

        # Layout
        fig.update_layout(
            **self.common_layout,
            title=dict(
                text="<b>📈 Daily Performance</b><br><sub>Normalized to 100 at start</sub>",
                font=dict(size=20),
                x=0.5,
                xanchor="center",
            ),
            height=600,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        # Update axes separately
        fig.update_xaxes(title_text="Date", **self.axis_style)
        fig.update_yaxes(title_text="Normalized Value", **self.axis_style)

        return self._save_chart(fig, "daily_performance.html")

    def plot_drawdown_analysis(self, equity_series: pd.Series) -> str:
        """
        Interactive drawdown analysis with running peak and drawdown percentage.

        Shows:
        - Equity curve with running maximum
        - Drawdown percentage (shaded red area)
        - Interactive zoom on worst periods

        Args:
            equity_series: Portfolio equity over time

        Returns:
            str: Path to saved HTML file
        """
        # Calculate running maximum and drawdown
        running_max = equity_series.expanding().max()
        drawdown = ((equity_series - running_max) / running_max) * 100

        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=("Equity with Running Maximum", "Drawdown %"),
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
        )

        # Top chart: Equity and running max
        fig.add_trace(
            go.Scatter(
                x=equity_series.index,
                y=equity_series.values,
                name="Portfolio Equity",
                line=dict(color=self.colors["primary"], width=2),
                hovertemplate="<b>Equity</b><br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=running_max.index,
                y=running_max.values,
                name="Running Maximum",
                line=dict(color=self.colors["success"], width=1, dash="dot"),
                hovertemplate="<b>Peak</b><br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Bottom chart: Drawdown
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values,
                name="Drawdown %",
                fill="tozeroy",
                fillcolor=f"rgba(239, 68, 68, 0.3)",  # Light red
                line=dict(color=self.colors["danger"], width=2),
                hovertemplate="<b>Drawdown</b><br>Date: %{x}<br>DD: %{y:.2f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # Layout
        fig.update_layout(
            **self.common_layout,
            title=dict(
                text="<b>📉 Drawdown Analysis</b>", font=dict(size=20), x=0.5, xanchor="center"
            ),
            height=800,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        # Update axes
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1, **self.axis_style)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1, **self.axis_style)
        fig.update_xaxes(title_text="Date", row=2, col=1, **self.axis_style)

        return self._save_chart(fig, "drawdown_analysis.html")

    def plot_portfolio_composition(self, holdings_df: pd.DataFrame) -> str:
        """
        Interactive pie chart of portfolio composition.

        Features:
        - Click to highlight sector
        - Hover for percentage and value
        - Auto-labels with values

        Args:
            holdings_df: DataFrame with 'ticker' and 'current_value' columns

        Returns:
            str: Path to saved HTML file
        """
        if holdings_df.empty:
            # Empty portfolio - create placeholder
            fig = go.Figure()
            fig.add_annotation(
                text="No holdings in portfolio",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20),
            )
        else:
            # Group by ticker and sum values
            composition = (
                holdings_df.groupby("ticker")["current_value"].sum().sort_values(ascending=False)
            )

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=composition.index,
                        values=composition.values,
                        hole=0.4,  # Donut chart
                        marker=dict(
                            colors=px.colors.qualitative.Set3, line=dict(color="white", width=2)
                        ),
                        textposition="inside",
                        textinfo="label+percent",
                        hovertemplate="<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>",
                        pull=[
                            0.05 if i == 0 else 0 for i in range(len(composition))
                        ],  # Pull largest slice
                    )
                ]
            )

        fig.update_layout(
            **self.common_layout,
            title=dict(
                text="<b>🥧 Portfolio Composition</b>", font=dict(size=20), x=0.5, xanchor="center"
            ),
            height=600,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        )

        return self._save_chart(fig, "composition.html")

    def plot_win_loss_analysis(self, trades_df: pd.DataFrame) -> str:
        """
        Interactive bar chart of win/loss analysis by position.

        Shows:
        - Green bars for profitable trades
        - Red bars for losing trades
        - Hover for trade details

        Args:
            trades_df: DataFrame with trade history

        Returns:
            str: Path to saved HTML file
        """
        if trades_df.empty or "PnL" not in trades_df.columns:
            # No trades - create placeholder
            fig = go.Figure()
            fig.add_annotation(
                text="No trades to analyze",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20),
            )
        else:
            # Calculate P&L per ticker
            pnl_by_ticker = trades_df.groupby("Ticker")["PnL"].sum().sort_values()

            # Color based on profit/loss
            colors = [
                self.colors["success"] if x > 0 else self.colors["danger"]
                for x in pnl_by_ticker.values
            ]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=pnl_by_ticker.index,
                        y=pnl_by_ticker.values,
                        marker=dict(
                            color=colors, line=dict(color="rgba(255,255,255,0.5)", width=1)
                        ),
                        hovertemplate="<b>%{x}</b><br>P&L: $%{y:,.2f}<extra></extra>",
                        text=[f"${v:,.0f}" for v in pnl_by_ticker.values],
                        textposition="outside",
                    )
                ]
            )

        fig.update_layout(
            **self.common_layout,
            title=dict(
                text="<b>💰 Win/Loss Analysis by Position</b>",
                font=dict(size=20),
                x=0.5,
                xanchor="center",
            ),
            height=600,
            showlegend=False,
        )

        # Update axes
        fig.update_xaxes(title_text="Ticker", **self.axis_style)
        fig.update_yaxes(title_text="P&L ($)", **self.axis_style)

        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color=self.colors["neutral"], opacity=0.5)

        return self._save_chart(fig, "win_loss_analysis.html")

    def plot_cash_position(self, cash_series: pd.Series, equity_series: pd.Series) -> str:
        """
        Interactive stacked area chart showing cash vs invested capital.

        Args:
            cash_series: Cash balance over time
            equity_series: Total equity over time

        Returns:
            str: Path to saved HTML file
        """
        invested = equity_series - cash_series

        fig = go.Figure()

        # Add cash area
        fig.add_trace(
            go.Scatter(
                x=cash_series.index,
                y=cash_series.values,
                name="Cash",
                fill="tozeroy",
                fillcolor=f"rgba(16, 185, 129, 0.3)",  # Light green
                line=dict(color=self.colors["success"], width=0),
                hovertemplate="<b>Cash</b><br>Date: %{x}<br>Amount: $%{y:,.2f}<extra></extra>",
                stackgroup="one",
            )
        )

        # Add invested area
        fig.add_trace(
            go.Scatter(
                x=invested.index,
                y=invested.values,
                name="Invested",
                fill="tonexty",
                fillcolor=f"rgba(59, 130, 246, 0.3)",  # Light blue
                line=dict(color=self.colors["primary"], width=0),
                hovertemplate="<b>Invested</b><br>Date: %{x}<br>Amount: $%{y:,.2f}<extra></extra>",
                stackgroup="one",
            )
        )

        # Add total equity line
        fig.add_trace(
            go.Scatter(
                x=equity_series.index,
                y=equity_series.values,
                name="Total Equity",
                line=dict(color=self.colors["neutral"], width=3, dash="dot"),
                hovertemplate="<b>Total</b><br>Date: %{x}<br>Equity: $%{y:,.2f}<extra></extra>",
            )
        )

        fig.update_layout(
            **self.common_layout,
            title=dict(
                text="<b>💵 Cash Position Over Time</b>",
                font=dict(size=20),
                x=0.5,
                xanchor="center",
            ),
            height=600,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        # Update axes
        fig.update_xaxes(title_text="Date", **self.axis_style)
        fig.update_yaxes(title_text="Amount ($)", **self.axis_style)

        return self._save_chart(fig, "cash_position.html")

    def plot_performance_vs_benchmark(
        self, portfolio_equity: pd.Series, benchmark_data: pd.Series, starting_value: float = 100.0
    ) -> str:
        """
        Interactive comparison of portfolio vs benchmark performance.

        Similar to daily_performance but with cumulative returns emphasis.

        Args:
            portfolio_equity: Portfolio equity series
            benchmark_data: Benchmark series (e.g., S&P 500)
            starting_value: Normalized starting value

        Returns:
            str: Path to saved HTML file
        """
        # Normalize both series
        port_norm = (portfolio_equity / portfolio_equity.iloc[0]) * starting_value
        bench_norm = (benchmark_data / benchmark_data.iloc[0]) * starting_value

        # Calculate alpha (outperformance)
        alpha = port_norm - bench_norm

        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=("Portfolio vs S&P 500", "Outperformance (Alpha)"),
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
        )

        # Top: Performance comparison
        fig.add_trace(
            go.Scatter(
                x=port_norm.index,
                y=port_norm.values,
                name="Portfolio",
                line=dict(color=self.colors["primary"], width=3),
                hovertemplate="<b>Portfolio</b><br>%{x}<br>Value: %{y:.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=bench_norm.index,
                y=bench_norm.values,
                name="S&P 500",
                line=dict(color=self.colors["secondary"], width=2, dash="dash"),
                hovertemplate="<b>S&P 500</b><br>%{x}<br>Value: %{y:.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Bottom: Alpha
        colors_alpha = [
            self.colors["success"] if x > 0 else self.colors["danger"] for x in alpha.values
        ]

        fig.add_trace(
            go.Bar(
                x=alpha.index,
                y=alpha.values,
                name="Alpha",
                marker=dict(color=colors_alpha),
                hovertemplate="<b>Alpha</b><br>%{x}<br>Outperformance: %{y:.2f}<extra></extra>",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            **self.common_layout,
            title=dict(
                text="<b>📊 Performance vs S&P 500</b>", font=dict(size=20), x=0.5, xanchor="center"
            ),
            height=800,
            showlegend=True,
        )

        fig.update_yaxes(title_text="Normalized Value", row=1, col=1, **self.axis_style)
        fig.update_yaxes(title_text="Alpha", row=2, col=1, **self.axis_style)
        fig.update_xaxes(title_text="Date", row=2, col=1, **self.axis_style)

        return self._save_chart(fig, "performance_vs_benchmark.html")

    def generate_all_plots(
        self,
        portfolio_equity: pd.Series,
        trades_df: pd.DataFrame,
        cash_series: Optional[pd.Series] = None,
        benchmark_data: Optional[pd.Series] = None,
        holdings_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, str]:
        """
        Generate all interactive charts at once.

        Args:
            portfolio_equity: Portfolio equity time series
            trades_df: Trade history DataFrame
            cash_series: Cash balance series (optional)
            benchmark_data: Benchmark data for comparison (optional)
            holdings_df: Current holdings DataFrame (optional)

        Returns:
            Dict[str, str]: Mapping of chart names to file paths
        """
        charts = {}

        print("\n🎨 Generating interactive charts...")

        # 1. Daily performance
        charts["daily_performance"] = self.plot_daily_performance(portfolio_equity, benchmark_data)
        print("  ✅ Daily performance chart")

        # 2. Drawdown analysis
        charts["drawdown_analysis"] = self.plot_drawdown_analysis(portfolio_equity)
        print("  ✅ Drawdown analysis chart")

        # 3. Performance vs benchmark (if benchmark available)
        if benchmark_data is not None and not benchmark_data.empty:
            charts["performance_vs_benchmark"] = self.plot_performance_vs_benchmark(
                portfolio_equity, benchmark_data
            )
            print("  ✅ Performance vs S&P 500 chart")

        # 4. Portfolio composition (if holdings available)
        if holdings_df is not None and not holdings_df.empty:
            charts["composition"] = self.plot_portfolio_composition(holdings_df)
            print("  ✅ Portfolio composition chart")

        # 5. Win/loss analysis
        if not trades_df.empty:
            charts["win_loss_analysis"] = self.plot_win_loss_analysis(trades_df)
            print("  ✅ Win/loss analysis chart")

        # 6. Cash position (if cash series available)
        if cash_series is not None and not cash_series.empty:
            charts["cash_position"] = self.plot_cash_position(cash_series, portfolio_equity)
            print("  ✅ Cash position chart")

        print(f"\n📊 Generated {len(charts)} interactive charts in: {self.output_dir}\n")

        return charts

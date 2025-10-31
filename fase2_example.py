"""
FASE 2: Complete Example - Metrics, Visualizations & HTML Reports

This script demonstrates the full Phase 2 functionality:
1. Calculate advanced metrics (Sharpe, Sortino, CAPM, etc.)
2. Generate professional visualizations (15+ chart types)
3. Create comprehensive HTML reports with embedded charts

Usage:
    python fase2_example.py --data-dir "Start Your Own"
    python fase2_example.py --data-dir "Scripts and CSV Files" --output reports/
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add agente-agno to path
sys.path.insert(0, str(Path(__file__).parent))

from core.html_reports import HTMLReportGenerator
from core.metrics import MetricsCalculator
from core.visualization import VisualizationGenerator

try:
    import yfinance as yf
except ImportError:
    print("[ERROR] yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)


def load_portfolio_data(data_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load portfolio and trade data from CSV files.

    Args:
        data_dir: Directory containing CSV files

    Returns:
        tuple: (portfolio_df, trades_df)
    """
    portfolio_path = Path(data_dir) / "chatgpt_portfolio_update.csv"
    trades_path = Path(data_dir) / "chatgpt_trade_log.csv"

    if not portfolio_path.exists():
        print(f"[ERROR] Portfolio file not found: {portfolio_path}")
        sys.exit(1)

    # Load portfolio
    portfolio_df = pd.read_csv(portfolio_path)
    portfolio_df["Date"] = pd.to_datetime(portfolio_df["Date"])

    # Load trades (if exists)
    if trades_path.exists():
        trades_df = pd.read_csv(trades_path)
        trades_df["Date"] = pd.to_datetime(trades_df["Date"])
    else:
        trades_df = pd.DataFrame()

    return portfolio_df, trades_df


def calculate_equity_series(portfolio_df: pd.DataFrame) -> pd.Series:
    """
    Calculate equity series from portfolio data.

    Args:
        portfolio_df: Portfolio DataFrame

    Returns:
        pd.Series: Equity over time
    """
    # Group by date and get total equity
    equity = portfolio_df.groupby("Date")["Total Equity"].last()
    equity = equity.sort_index()

    # Convert to numeric (in case it's stored as string)
    equity = pd.to_numeric(equity, errors="coerce")

    return equity


def calculate_cash_series(portfolio_df: pd.DataFrame) -> pd.Series:
    """
    Calculate cash series from portfolio data.

    Args:
        portfolio_df: Portfolio DataFrame

    Returns:
        pd.Series: Cash balance over time
    """
    cash = portfolio_df.groupby("Date")["Cash Balance"].last()
    cash = cash.sort_index()

    # Convert to numeric (in case it's stored as string)
    cash = pd.to_numeric(cash, errors="coerce")

    return cash


def get_benchmark_data(equity_series: pd.Series) -> pd.Series:
    """
    Fetch S&P 500 benchmark data.

    Args:
        equity_series: Portfolio equity series (for date range)

    Returns:
        pd.Series: S&P 500 price series
    """
    start_date = equity_series.index.min()
    end_date = equity_series.index.max()

    print(f"[INFO] Fetching S&P 500 data from {start_date.date()} to {end_date.date()}...")

    try:
        sp500 = yf.download("^GSPC", start=start_date, end=end_date, progress=False)
        if sp500.empty:
            print("[WARNING] No S&P 500 data retrieved")
            return pd.Series()

        # Get close prices
        benchmark = sp500["Close"]
        benchmark.index = pd.to_datetime(benchmark.index)

        return benchmark

    except Exception as e:
        print(f"[ERROR] Failed to fetch benchmark data: {e}")
        return pd.Series()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate Phase 2 reports with metrics and visualizations"
    )
    parser.add_argument(
        "--data-dir", type=str, default="Start Your Own", help="Directory containing CSV files"
    )
    parser.add_argument(
        "--output", type=str, default="reports", help="Output directory for reports"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("FASE 2: ADVANCED ANALYTICS & REPORTING")
    print("=" * 70)
    print()

    # 1. Load data
    print("[STEP 1] Loading portfolio data...")
    portfolio_df, trades_df = load_portfolio_data(args.data_dir)
    print(f"  ✅ Portfolio: {len(portfolio_df)} records")
    print(f"  ✅ Trades: {len(trades_df)} records")
    print()

    # 2. Calculate series
    print("[STEP 2] Calculating equity series...")
    equity_series = calculate_equity_series(portfolio_df)
    cash_series = calculate_cash_series(portfolio_df)

    if equity_series.empty:
        print("  ⚠️  No equity data available (empty portfolio)")
        print("  ℹ️  This is a template file. Use 'Scripts and CSV Files' for real data.")
        print()
        print("=" * 70)
        print("❌ CANNOT GENERATE REPORT WITH EMPTY DATA")
        print("=" * 70)
        print()
        print("Try instead:")
        print('  python agente-agno/fase2_example.py --data-dir "Scripts and CSV Files"')
        print()
        sys.exit(0)

    print(f"  ✅ Equity range: ${equity_series.min():.2f} - ${equity_series.max():.2f}")
    print(f"  ✅ Current equity: ${equity_series.iloc[-1]:.2f}")
    print()

    # 3. Get benchmark data
    print("[STEP 3] Fetching S&P 500 benchmark...")
    benchmark_data = get_benchmark_data(equity_series)
    if not benchmark_data.empty:
        print(f"  ✅ Benchmark data: {len(benchmark_data)} days")
    else:
        print("  ⚠️  Benchmark data unavailable (will skip CAPM)")
    print()

    # 4. Calculate metrics
    print("[STEP 4] Calculating advanced metrics...")
    calculator = MetricsCalculator(risk_free_rate=0.05)

    metrics = calculator.calculate_all_metrics(
        equity_series=equity_series, trades_df=trades_df, benchmark_ticker="^GSPC"
    )

    print(f"  ✅ Sharpe Ratio (annual): {metrics.get('sharpe_annual', 0):.2f}")
    print(f"  ✅ Sortino Ratio (annual): {metrics.get('sortino_annual', 0):.2f}")
    print(f"  ✅ Beta: {metrics.get('beta', 0):.2f}")
    print(f"  ✅ Alpha (annual): {metrics.get('alpha_annual', 0):.2%}")
    print(f"  ✅ Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
    print(f"  ✅ Win Rate: {metrics.get('win_rate', 0):.1f}%")
    print()

    # 5. Generate visualizations
    print("[STEP 5] Generating visualizations...")
    viz_dir = Path(args.output) / "charts"
    viz = VisualizationGenerator(output_dir=viz_dir)

    # Get current holdings
    latest_date = portfolio_df["Date"].max()
    holdings_df = portfolio_df[portfolio_df["Date"] == latest_date].copy()

    # Rename columns to match expected format
    if "Ticker" in holdings_df.columns:
        holdings_df["ticker"] = holdings_df["Ticker"]
    if "Total Value" in holdings_df.columns:
        holdings_df["current_value"] = pd.to_numeric(holdings_df["Total Value"], errors="coerce")
    if "Shares" in holdings_df.columns:
        holdings_df["shares"] = pd.to_numeric(holdings_df["Shares"], errors="coerce")
    if "Buy Price" in holdings_df.columns:
        holdings_df["buy_price"] = pd.to_numeric(holdings_df["Buy Price"], errors="coerce")
    if "Current Price" in holdings_df.columns:
        holdings_df["current_price"] = pd.to_numeric(holdings_df["Current Price"], errors="coerce")
    if "PnL" in holdings_df.columns:
        holdings_df["pnl"] = pd.to_numeric(holdings_df["PnL"], errors="coerce")

    # Calculate ROI if not present
    if (
        "roi_percent" not in holdings_df.columns
        and "buy_price" in holdings_df.columns
        and "current_price" in holdings_df.columns
    ):
        holdings_df["roi_percent"] = (
            (holdings_df["current_price"] / holdings_df["buy_price"]) - 1
        ) * 100

    # Filter out cash rows
    holdings_df = holdings_df[holdings_df["ticker"] != "CASH"].copy()

    chart_paths = {}

    # Daily performance
    chart_paths["daily_performance"] = viz.plot_daily_performance(equity_series)
    print("  ✅ Daily performance chart")

    # Drawdown analysis
    chart_paths["drawdown_analysis"] = viz.plot_drawdown_over_time(equity_series)
    print("  ✅ Drawdown analysis chart")

    # Performance vs benchmark
    if not benchmark_data.empty:
        chart_paths["performance_vs_benchmark"] = viz.plot_performance_vs_benchmark(
            equity_series, benchmark_data
        )
        print("  ✅ Performance vs S&P 500 chart")

    # Portfolio composition
    if not holdings_df.empty:
        chart_paths["composition"] = viz.plot_portfolio_composition(holdings_df)
        print("  ✅ Portfolio composition chart")

    # Win/loss analysis
    if not trades_df.empty:
        chart_paths["win_loss"] = viz.plot_win_loss_analysis(trades_df)
        print("  ✅ Win/loss analysis chart")

    # Cash position
    chart_paths["cash_position"] = viz.plot_cash_position(equity_series, cash_series)
    print("  ✅ Cash position chart")

    print(f"\n  📊 Generated {len(chart_paths)} charts in: {viz_dir}")
    print()

    # 6. Generate HTML report
    print("[STEP 6] Generating HTML report...")
    reporter = HTMLReportGenerator()

    # Prepare portfolio summary
    portfolio_summary = {
        "total_equity": equity_series.iloc[-1],
        "cash_balance": cash_series.iloc[-1],
        "total_pnl": equity_series.iloc[-1] - equity_series.iloc[0],
        "roi_percent": ((equity_series.iloc[-1] / equity_series.iloc[0]) - 1) * 100,
        "num_positions": len(holdings_df) if not holdings_df.empty else 0,
    }

    # Generate report
    report_path = Path(args.output) / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    output_file = reporter.generate_full_report(
        output_path=report_path,
        portfolio_summary=portfolio_summary,
        metrics=metrics,
        chart_paths=chart_paths,
        holdings_df=holdings_df if not holdings_df.empty else None,
    )

    print(f"  ✅ HTML report saved to: {output_file}")
    print()

    # 7. Summary
    print("=" * 70)
    print("✅ FASE 2 COMPLETE!")
    print("=" * 70)
    print()
    print("Generated Files:")
    print(f"  📊 Charts: {len(chart_paths)} visualizations in {viz_dir}")
    print(f"  📄 Report: {output_file}")
    print()
    print("Key Metrics:")
    print(f"  • Total Equity: ${portfolio_summary['total_equity']:,.2f}")
    print(f"  • ROI: {portfolio_summary['roi_percent']:+.2f}%")
    print(f"  • Sharpe Ratio: {metrics.get('sharpe_annual', 0):.2f}")
    print(f"  • Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
    print(f"  • Win Rate: {metrics.get('win_rate', 0):.1f}%")
    print()


if __name__ == "__main__":
    main()

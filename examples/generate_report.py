"""
Simple Report Generation Example
=================================
Genera un reporte FASE 2 completo con métricas avanzadas.

Usage:
    python examples/generate_report.py
    python examples/generate_report.py --data-dir "path/to/data"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from core import (
    HTMLReportGenerator,
    InteractiveVisualizationGenerator,
    MetricsCalculator,
    create_insights_generator,
)
from fase2_example_interactive import (
    calculate_equity_series,
    fetch_benchmark_data,
    load_portfolio_data,
    prepare_holdings_df,
)


def main():
    """Generate comprehensive analytics report"""
    parser = argparse.ArgumentParser(description="Generate FASE 2 analytics report")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="../Scripts and CSV Files",
        help="Directory containing portfolio CSVs",
    )
    parser.add_argument(
        "--output-dir", type=str, default="../reports", help="Directory to save report"
    )
    parser.add_argument("--no-ai", action="store_true", help="Skip AI insights generation")

    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)

    print("\n" + "=" * 70)
    print("GENERATING ANALYTICS REPORT")
    print("=" * 70)

    # Load data
    print("\n[1/6] Loading portfolio data...")
    portfolio_df, trades_df = load_portfolio_data(data_dir)
    equity, cash = calculate_equity_series(portfolio_df)
    print(f"  ✅ Loaded {len(portfolio_df)} records, {len(trades_df)} trades")

    # Fetch benchmark
    print("\n[2/6] Fetching benchmark data...")
    start_date = equity.index.min()
    end_date = equity.index.max()
    benchmark = fetch_benchmark_data(start_date, end_date)
    print(f"  ✅ Benchmark: {len(benchmark)} days")

    # Calculate metrics
    print("\n[3/6] Calculating metrics...")
    calculator = MetricsCalculator(risk_free_rate=0.05)
    metrics = calculator.calculate_all_metrics(
        equity_series=equity,
        trades_df=trades_df,
        benchmark_ticker="^GSPC" if not benchmark.empty else None,
    )
    print(f"  ✅ Sharpe: {metrics.get('sharpe_annual', 0):.2f}")
    print(f"  ✅ Max Drawdown: {metrics.get('max_drawdown', 0):.1f}%")

    # Generate AI insights
    llm_insights = None
    if not args.no_ai:
        print("\n[4/6] Generating AI insights...")
        try:
            llm_gen = create_insights_generator()
            if llm_gen:
                portfolio_summary = {
                    "total_equity": equity.iloc[-1],
                    "cash_balance": cash.iloc[-1],
                    "roi_percent": ((equity.iloc[-1] / equity.iloc[0]) - 1) * 100,
                    "num_positions": prepare_holdings_df(portfolio_df).shape[0],
                }

                trades_summary = {
                    "total_trades": len(trades_df),
                    "win_rate": metrics.get("win_rate", 0),
                    "winning_trades": metrics.get("winning_trades", 0),
                    "losing_trades": metrics.get("losing_trades", 0),
                }

                llm_insights = llm_gen.generate_insights(portfolio_summary, metrics, trades_summary)
                print(f"  ✅ AI insights generated")
        except Exception as e:
            print(f"  ⚠️  AI insights failed: {e}")
    else:
        print("\n[4/6] Skipping AI insights (--no-ai)")

    # Generate charts
    print("\n[5/6] Generating charts...")
    charts_dir = output_dir / "charts"
    viz = InteractiveVisualizationGenerator(output_dir=charts_dir)
    holdings_df = prepare_holdings_df(portfolio_df)

    chart_paths = viz.generate_all_plots(
        portfolio_equity=equity,
        trades_df=trades_df,
        cash_series=cash,
        benchmark_data=benchmark if not benchmark.empty else None,
        holdings_df=holdings_df if not holdings_df.empty else None,
    )
    print(f"  ✅ {len(chart_paths)} charts generated")

    # Generate HTML report
    print("\n[6/6] Generating HTML report...")
    reporter = HTMLReportGenerator()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"report_{timestamp}.html"

    portfolio_summary = {
        "total_equity": equity.iloc[-1],
        "cash_balance": cash.iloc[-1],
        "total_pnl": equity.iloc[-1] - equity.iloc[0],
        "roi_percent": ((equity.iloc[-1] / equity.iloc[0]) - 1) * 100,
        "num_positions": len(holdings_df) if not holdings_df.empty else 0,
    }

    reporter.generate_full_report(
        output_path=str(report_path),
        portfolio_summary=portfolio_summary,
        metrics=metrics,
        chart_paths=chart_paths,
        holdings_df=holdings_df if not holdings_df.empty else None,
        llm_insights=llm_insights,
    )

    print("\n" + "=" * 70)
    print("✅ REPORT GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📄 Report: {report_path}")
    print(f"📊 Charts: {charts_dir}")
    print(f"\n💡 Open report: start {report_path}")


if __name__ == "__main__":
    main()

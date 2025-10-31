"""
Advanced Reporter Integration - Example Usage
==============================================
Demonstrates how to integrate FASE 2 analytics into the Agno agent workflow.

This example shows:
1. Running the complete trading team (9 agents)
2. Generating advanced analytics report with FASE 2 system
3. Combining AI agent decisions with comprehensive analytics

Usage:
    python agente-agno/scripts/advanced_reporting_workflow.py --data-dir "Scripts and CSV Files"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

# Import trading functions
from trading_script import PORTFOLIO_CSV, TRADE_LOG_CSV, load_latest_portfolio_state, set_data_dir

# Import agent system
from agents import load_advanced_reporter, load_complete_team

# Import FASE 2 analytics
from core import HTMLReportGenerator, MetricsCalculator
from core.llm_insights import create_insights_generator
from core.visualization_plotly import InteractiveVisualizationGenerator


def load_portfolio_summary(data_dir: Path) -> dict:
    """Load current portfolio state and return summary"""
    set_data_dir(str(data_dir))

    portfolio_df, cash = load_latest_portfolio_state(str(PORTFOLIO_CSV))

    if portfolio_df.empty:
        total_equity = cash
        roi = 0.0
    else:
        total_value = portfolio_df["Total Value"].sum()
        total_equity = total_value + cash
        # Calculate ROI (assuming $100 start)
        roi = ((total_equity / 100.0) - 1) * 100

    return {
        "cash": cash,
        "total_equity": total_equity,
        "roi": roi,
        "num_positions": len(portfolio_df) if not portfolio_df.empty else 0,
    }


def run_trading_workflow(data_dir: Path):
    """
    Complete trading workflow:
    1. Load current portfolio
    2. Run 9-agent team for trading decisions
    3. Execute trades (simulated)
    4. Generate advanced analytics report
    """

    print("\n" + "=" * 80)
    print("ADVANCED TRADING WORKFLOW WITH ANALYTICS")
    print("=" * 80)

    # Step 1: Load portfolio summary
    print("\n[STEP 1/4] Loading portfolio summary...")
    portfolio_summary = load_portfolio_summary(data_dir)

    print(f"  💰 Cash: ${portfolio_summary['cash']:,.2f}")
    print(f"  📊 Total Equity: ${portfolio_summary['total_equity']:,.2f}")
    print(f"  📈 ROI: {portfolio_summary['roi']:+.2f}%")
    print(f"  📋 Positions: {portfolio_summary['num_positions']}")

    # Step 2: Load and run trading team (optional - for trading decisions)
    print("\n[STEP 2/4] Running trading team analysis (OPTIONAL)...")
    response = input("  Run 9-agent trading team? (y/n): ").strip().lower()

    if response == "y":
        team = load_complete_team(use_openrouter=True, portfolio_summary=portfolio_summary)

        query = f"""
        Analiza el portafolio actual y proporciona recomendaciones de trading.

        Estado Actual:
        - Cash: ${portfolio_summary['cash']:,.2f}
        - Total Equity: ${portfolio_summary['total_equity']:,.2f}
        - ROI: {portfolio_summary['roi']:+.2f}%
        - Posiciones: {portfolio_summary['num_positions']}

        Por favor, proporciona:
        1. Análisis del mercado actual
        2. Evaluación de riesgos
        3. Recomendaciones de trading específicas
        4. Decisión final (comprar/mantener/vender)
        """

        print("\n" + "-" * 80)
        print("RUNNING 9-AGENT TEAM...")
        print("-" * 80)
        team.print_response(query, stream=True)
        print("\n" + "-" * 80)
        print("✅ Team analysis complete")
        print("-" * 80)
    else:
        print("  ⏭️  Skipping team analysis")

    # Step 3: Execute trades (simulated - would use trading_script.py)
    print("\n[STEP 3/4] Executing trades (SIMULATED)...")
    print("  ⏭️  No trades executed in this example")
    print("  💡 In production, you would:")
    print("     - Parse team recommendations")
    print("     - Execute buy/sell orders")
    print("     - Update portfolio CSVs")

    # Step 4: Generate advanced analytics report
    print("\n[STEP 4/4] Generating advanced analytics report...")
    print("  📊 Using FASE 2 system:")
    print("     - Loading portfolio & trade data")
    print("     - Calculating advanced metrics")
    print("     - Generating interactive charts")
    print("     - Creating AI insights")
    print("     - Compiling HTML report")

    try:
        # Import and run the FASE 2 report generator
        from fase2_example_interactive import (
            calculate_equity_series,
            fetch_benchmark_data,
            load_portfolio_data,
            prepare_holdings_df,
        )

        # Load data
        portfolio_df, trades_df = load_portfolio_data(data_dir)
        equity, cash_series = calculate_equity_series(portfolio_df)

        if len(equity) < 2:
            print("\n  ⚠️  Insufficient data for analytics report")
            print("     Need at least 2 days of portfolio history")
            return

        # Fetch benchmark
        start_date = equity.index.min()
        end_date = equity.index.max()
        benchmark = fetch_benchmark_data(start_date, end_date)

        # Calculate metrics
        calculator = MetricsCalculator(risk_free_rate=0.05)
        metrics = calculator.calculate_all_metrics(
            equity_series=equity,
            trades_df=trades_df,
            benchmark_ticker="^GSPC" if not benchmark.empty else None,
        )

        # Generate AI insights (optional)
        llm_insights = None
        try:
            llm_gen = create_insights_generator()
            if llm_gen:
                trades_summary = {
                    "total_trades": len(trades_df) if not trades_df.empty else 0,
                    "win_rate": metrics.get("win_rate", 0),
                    "winning_trades": metrics.get("winning_trades", 0),
                    "losing_trades": metrics.get("losing_trades", 0),
                    "avg_win": metrics.get("avg_win", 0),
                    "avg_loss": metrics.get("avg_loss", 0),
                    "profit_factor": metrics.get("profit_factor", 0),
                }

                llm_insights = llm_gen.generate_insights(portfolio_summary, metrics, trades_summary)

                if llm_insights:
                    print(f"     ✅ AI insights generated")
        except Exception as e:
            print(f"     ⚠️  AI insights failed: {e}")

        # Generate charts
        charts_dir = Path("reports") / "charts"
        charts_dir.mkdir(parents=True, exist_ok=True)

        viz = InteractiveVisualizationGenerator(output_dir=charts_dir)
        holdings_df = prepare_holdings_df(portfolio_df)

        chart_paths = viz.generate_all_plots(
            portfolio_equity=equity,
            trades_df=trades_df,
            cash_series=cash_series,
            benchmark_data=benchmark if not benchmark.empty else None,
            holdings_df=holdings_df if not holdings_df.empty else None,
        )

        print(f"     ✅ {len(chart_paths)} interactive charts generated")

        # Generate HTML report
        reporter = HTMLReportGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path("reports") / f"advanced_report_{timestamp}.html"

        reporter.generate_full_report(
            output_path=str(report_path),
            portfolio_summary=portfolio_summary,
            metrics=metrics,
            chart_paths=chart_paths,
            holdings_df=holdings_df if not holdings_df.empty else None,
            llm_insights=llm_insights,
        )

        print(f"\n  ✅ Advanced analytics report saved:")
        print(f"     📄 {report_path}")
        print(f"\n  💡 Open the report in your browser:")
        print(f"     start {report_path}")

        # Summary
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETE!")
        print("=" * 80)
        print(f"\n  📊 Report Features:")
        print(f"     - Executive Summary")
        print(f"     - Performance Metrics (Sharpe: {metrics.get('sharpe_annual', 0):.2f})")
        print(f"     - Trade Statistics (Win Rate: {metrics.get('win_rate', 0):.1f}%)")
        print(f"     - {len(chart_paths)} Interactive Charts")
        if llm_insights:
            print(f"     - AI-Powered Insights (DeepSeek)")
        print(f"     - Dark Mode Toggle")
        print(f"\n  📈 Next Steps:")
        print(f"     1. Review the HTML report")
        print(f"     2. Analyze AI insights and recommendations")
        print(f"     3. Execute trading decisions")
        print(f"     4. Re-run workflow after trades")

    except Exception as e:
        print(f"\n  ❌ Error generating report: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Advanced Trading Workflow with Analytics")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="Start Your Own",
        help='Directory containing portfolio CSVs (default: "Start Your Own")',
    )

    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return

    # Check for required files
    portfolio_csv = data_dir / "chatgpt_portfolio_update.csv"
    if not portfolio_csv.exists():
        print(f"❌ Portfolio file not found: {portfolio_csv}")
        return

    # Run workflow
    run_trading_workflow(data_dir)


if __name__ == "__main__":
    main()

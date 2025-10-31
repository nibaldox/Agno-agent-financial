"""
Test Suite for FASE 2 - Metrics, Visualizations & Reports

Tests all Phase 2 components:
1. MetricsCalculator - All metric calculations
2. VisualizationGenerator - Chart generation
3. HTMLReportGenerator - Report creation

Run with:
    python test_phase2.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add agente-agno to path
sys.path.insert(0, str(Path(__file__).parent))

from core.html_reports import HTMLReportGenerator
from core.metrics import MetricsCalculator
from core.visualization import VisualizationGenerator


def create_sample_data():
    """Create sample portfolio and trade data for testing."""
    # Create 30 days of equity data
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")

    # Simulate portfolio growth with some volatility
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 30)  # Daily returns
    equity_values = [100.0]  # Start with $100

    for ret in returns[1:]:
        equity_values.append(equity_values[-1] * (1 + ret))

    equity_series = pd.Series(equity_values, index=dates)

    # Create cash series (decreasing as we invest)
    cash_values = [50 - i * 0.5 for i in range(30)]  # Start with $50, decrease
    cash_series = pd.Series(cash_values, index=dates)

    # Create sample trades
    trades_data = []
    for i in range(10):
        # Random buy/sell trades
        pnl = np.random.normal(5, 15)  # Random P&L
        trades_data.append(
            {
                "Date": dates[i * 2],
                "Ticker": f"TEST{i}",
                "Shares Bought": 10 if pnl > 0 else 0,
                "Buy Price": 10.0,
                "Shares Sold": 10 if pnl > 0 else 0,
                "Sell Price": 10 + pnl if pnl > 0 else 10,
                "PnL": pnl,
                "Reason": "Test trade",
            }
        )

    trades_df = pd.DataFrame(trades_data)
    trades_df["Date"] = pd.to_datetime(trades_df["Date"])

    # Create sample holdings
    holdings_data = [
        {
            "ticker": "AAPL",
            "shares": 10,
            "buy_price": 150.0,
            "current_price": 160.0,
            "current_value": 1600.0,
            "pnl": 100.0,
            "roi_percent": 6.67,
        },
        {
            "ticker": "MSFT",
            "shares": 5,
            "buy_price": 300.0,
            "current_price": 310.0,
            "current_value": 1550.0,
            "pnl": 50.0,
            "roi_percent": 3.33,
        },
        {
            "ticker": "GOOGL",
            "shares": 8,
            "buy_price": 140.0,
            "current_price": 135.0,
            "current_value": 1080.0,
            "pnl": -40.0,
            "roi_percent": -3.57,
        },
    ]
    holdings_df = pd.DataFrame(holdings_data)

    return equity_series, cash_series, trades_df, holdings_df


def test_metrics_calculator():
    """Test MetricsCalculator functionality."""
    print("=" * 70)
    print("TEST 1: MetricsCalculator")
    print("=" * 70)

    equity_series, _, trades_df, _ = create_sample_data()

    calculator = MetricsCalculator(risk_free_rate=0.05)

    # Test individual metrics
    print("\n[1.1] Testing Sharpe Ratio...")
    returns = equity_series.pct_change().dropna()
    sharpe = calculator.calculate_sharpe_ratio(returns, period="daily")

    assert "sharpe_period" in sharpe, "Missing sharpe_period"
    assert "sharpe_annual" in sharpe, "Missing sharpe_annual"
    print(f"  ✅ Sharpe (period): {sharpe['sharpe_period']:.2f}")
    print(f"  ✅ Sharpe (annual): {sharpe['sharpe_annual']:.2f}")

    print("\n[1.2] Testing Sortino Ratio...")
    sortino = calculator.calculate_sortino_ratio(returns, period="daily")

    assert "sortino_period" in sortino, "Missing sortino_period"
    assert "sortino_annual" in sortino, "Missing sortino_annual"
    print(f"  ✅ Sortino (period): {sortino['sortino_period']:.2f}")
    print(f"  ✅ Sortino (annual): {sortino['sortino_annual']:.2f}")

    print("\n[1.3] Testing Max Drawdown...")
    drawdown = calculator.calculate_max_drawdown(equity_series)

    assert "max_drawdown" in drawdown, "Missing max_drawdown"
    assert "max_drawdown_date" in drawdown, "Missing max_drawdown_date"
    print(f"  ✅ Max Drawdown: {drawdown['max_drawdown']:.2f}%")
    print(f"  ✅ Drawdown Date: {drawdown['max_drawdown_date']}")

    print("\n[1.4] Testing Volatility Metrics...")
    volatility = calculator.calculate_volatility_metrics(returns)

    assert "daily_volatility" in volatility, "Missing daily_volatility"
    assert "annual_volatility" in volatility, "Missing annual_volatility"
    print(f"  ✅ Daily Volatility: {volatility['daily_volatility']:.4f}")
    print(f"  ✅ Annual Volatility: {volatility['annual_volatility']:.4f}")

    print("\n[1.5] Testing Win/Loss Statistics...")
    win_loss = calculator.calculate_win_loss_stats(trades_df)

    assert "total_trades" in win_loss, "Missing total_trades"
    assert "win_rate" in win_loss, "Missing win_rate"
    print(f"  ✅ Total Trades: {win_loss['total_trades']}")
    print(f"  ✅ Win Rate: {win_loss['win_rate']:.1f}%")
    print(f"  ✅ Avg Win: ${win_loss['avg_win']:.2f}")
    print(f"  ✅ Avg Loss: ${win_loss['avg_loss']:.2f}")

    print("\n[1.6] Testing Comprehensive Metrics...")
    all_metrics = calculator.calculate_all_metrics(
        equity_series=equity_series, trades_df=trades_df, benchmark_ticker="^GSPC"
    )

    required_keys = [
        "sharpe_annual",
        "sortino_annual",
        "max_drawdown",
        "annual_volatility",
        "win_rate",
        "total_trades",
    ]

    for key in required_keys:
        assert key in all_metrics, f"Missing key in all_metrics: {key}"

    print(f"  ✅ All metrics calculated: {len(all_metrics)} metrics")

    print("\n✅ TEST 1 PASSED - All metrics working correctly")
    return True


def test_visualization_generator():
    """Test VisualizationGenerator functionality."""
    print("\n" + "=" * 70)
    print("TEST 2: VisualizationGenerator")
    print("=" * 70)

    equity_series, cash_series, trades_df, holdings_df = create_sample_data()

    # Create temporary output directory
    output_dir = Path("test_output/charts")
    viz = VisualizationGenerator(output_dir=output_dir)

    print("\n[2.1] Testing Daily Performance Chart...")
    path1 = viz.plot_daily_performance(equity_series)
    assert Path(path1).exists(), "Daily performance chart not created"
    print(f"  ✅ Created: {path1}")

    print("\n[2.2] Testing Drawdown Chart...")
    path2 = viz.plot_drawdown_over_time(equity_series)
    assert Path(path2).exists(), "Drawdown chart not created"
    print(f"  ✅ Created: {path2}")

    print("\n[2.3] Testing Portfolio Composition Chart...")
    path3 = viz.plot_portfolio_composition(holdings_df)
    assert Path(path3).exists(), "Composition chart not created"
    print(f"  ✅ Created: {path3}")

    print("\n[2.4] Testing Win/Loss Analysis Chart...")
    path4 = viz.plot_win_loss_analysis(trades_df)
    assert Path(path4).exists(), "Win/loss chart not created"
    print(f"  ✅ Created: {path4}")

    print("\n[2.5] Testing Cash Position Chart...")
    path5 = viz.plot_cash_position(equity_series, cash_series)
    assert Path(path5).exists(), "Cash position chart not created"
    print(f"  ✅ Created: {path5}")

    print("\n[2.6] Testing Batch Generation...")
    all_plots = viz.generate_all_plots(
        portfolio_equity=equity_series,
        holdings_df=holdings_df,
        trades_df=trades_df,
        cash_series=cash_series,
    )

    assert len(all_plots) >= 5, "Not enough plots generated"
    print(f"  ✅ Generated {len(all_plots)} plots")

    for name, path in all_plots.items():
        print(f"     • {name}: {Path(path).name}")

    print("\n✅ TEST 2 PASSED - All visualizations working correctly")
    return True


def test_html_report_generator():
    """Test HTMLReportGenerator functionality."""
    print("\n" + "=" * 70)
    print("TEST 3: HTMLReportGenerator")
    print("=" * 70)

    equity_series, _, trades_df, holdings_df = create_sample_data()

    # Calculate metrics first
    calculator = MetricsCalculator(risk_free_rate=0.05)
    metrics = calculator.calculate_all_metrics(
        equity_series=equity_series, trades_df=trades_df, benchmark_ticker="^GSPC"
    )

    # Generate visualizations
    viz_dir = Path("test_output/charts")
    viz = VisualizationGenerator(output_dir=viz_dir)

    chart_paths = {
        "daily_performance": viz.plot_daily_performance(equity_series),
        "composition": viz.plot_portfolio_composition(holdings_df),
        "win_loss": viz.plot_win_loss_analysis(trades_df),
    }

    print("\n[3.1] Testing Executive Summary Generation...")
    reporter = HTMLReportGenerator()

    portfolio_summary = {
        "total_equity": equity_series.iloc[-1],
        "cash_balance": 45.0,
        "total_pnl": equity_series.iloc[-1] - equity_series.iloc[0],
        "roi_percent": ((equity_series.iloc[-1] / equity_series.iloc[0]) - 1) * 100,
        "num_positions": 3,
    }

    exec_summary = reporter.generate_executive_summary(
        total_equity=portfolio_summary["total_equity"],
        cash_balance=portfolio_summary["cash_balance"],
        total_pnl=portfolio_summary["total_pnl"],
        roi_percent=portfolio_summary["roi_percent"],
        num_positions=portfolio_summary["num_positions"],
        win_rate=metrics["win_rate"],
    )

    assert '<div class="section">' in exec_summary, "Invalid HTML structure"
    assert "Total Equity" in exec_summary, "Missing Total Equity"
    print("  ✅ Executive summary HTML generated")

    print("\n[3.2] Testing Performance Metrics Section...")
    perf_metrics = reporter.generate_performance_metrics(metrics)

    assert "Sharpe Ratio" in perf_metrics, "Missing Sharpe Ratio"
    assert "Sortino Ratio" in perf_metrics, "Missing Sortino Ratio"
    print("  ✅ Performance metrics HTML generated")

    print("\n[3.3] Testing Holdings Table...")
    holdings_table = reporter.generate_holdings_table(holdings_df)

    assert "<table>" in holdings_table, "Missing table tag"
    assert "AAPL" in holdings_table, "Missing AAPL ticker"
    print("  ✅ Holdings table HTML generated")

    print("\n[3.4] Testing Full Report Generation...")
    output_path = Path("test_output/test_report.html")

    report_file = reporter.generate_full_report(
        output_path=output_path,
        portfolio_summary=portfolio_summary,
        metrics=metrics,
        chart_paths=chart_paths,
        holdings_df=holdings_df,
    )

    assert Path(report_file).exists(), "Report file not created"

    # Check file size (should be substantial with embedded images)
    file_size = Path(report_file).stat().st_size
    assert file_size > 10000, f"Report file too small: {file_size} bytes"

    print(f"  ✅ Full report created: {report_file}")
    print(f"  ✅ File size: {file_size:,} bytes")

    # Verify HTML content
    with open(report_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    assert "<!DOCTYPE html>" in html_content, "Invalid HTML document"
    assert "Trading Performance Report" in html_content, "Missing title"
    assert "data:image/png;base64," in html_content, "No embedded images"

    print("  ✅ HTML structure validated")
    print("  ✅ Embedded images verified")

    print("\n✅ TEST 3 PASSED - HTML report generation working correctly")
    return True


def run_all_tests():
    """Run all Phase 2 tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "FASE 2 TEST SUITE - FULL RUN" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    results = {}

    # Test 1: Metrics
    try:
        results["metrics"] = test_metrics_calculator()
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        results["metrics"] = False

    # Test 2: Visualizations
    try:
        results["visualization"] = test_visualization_generator()
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        results["visualization"] = False

    # Test 3: HTML Reports
    try:
        results["html_reports"] = test_html_report_generator()
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        results["html_reports"] = False

    # Summary
    print("\n")
    print("=" * 70)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")

    total_tests = len(results)
    passed_tests = sum(results.values())
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"\nTotal: {passed_tests}/{total_tests} tests pasados ({pass_rate:.1f}%)")

    if all(results.values()):
        print("\n🎉 ¡TODOS LOS TESTS DE FASE 2 PASARON!")
        print("\n✅ FASE 2 COMPLETADA CON ÉXITO")
        print("   • MetricsCalculator: 100% funcional")
        print("   • VisualizationGenerator: 100% funcional")
        print("   • HTMLReportGenerator: 100% funcional")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores arriba.")

    print("=" * 70)
    print()


if __name__ == "__main__":
    run_all_tests()

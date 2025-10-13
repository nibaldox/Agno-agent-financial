"""
FASE 2 Example Script - INTERACTIVE CHARTS VERSION

Demonstrates the complete FASE 2 workflow with INTERACTIVE Plotly charts:
1. Load portfolio and trade data
2. Calculate equity and cash series
3. Fetch benchmark data (S&P 500)
4. Calculate advanced metrics (Sharpe, Sortino, Beta, Alpha, etc.)
5. Generate INTERACTIVE visualizations (zoom, pan, hover tooltips)
6. Create comprehensive HTML report with embedded interactive charts

Usage:
    python agente-agno/fase2_example_interactive.py --data-dir "Start Your Own"
    python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import warnings
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core import MetricsCalculator, HTMLReportGenerator
    from core.visualization_plotly import InteractiveVisualizationGenerator
    HAS_PLOTLY = True
except ImportError:
    print("⚠️  Plotly not installed. Install with:")
    print("   pip install plotly")
    print("\nFalling back to matplotlib...")
    from core import MetricsCalculator, VisualizationGenerator, HTMLReportGenerator
    HAS_PLOTLY = False

import yfinance as yf

# Suppress warnings
warnings.filterwarnings('ignore')


def load_portfolio_data(data_dir: Path) -> tuple:
    """Load portfolio and trade log CSVs."""
    portfolio_path = data_dir / "chatgpt_portfolio_update.csv"
    trades_path = data_dir / "chatgpt_trade_log.csv"
    
    if not portfolio_path.exists():
        print(f"❌ Portfolio file not found: {portfolio_path}")
        print(f"\nVerify the data directory exists and contains the required CSV files.")
        sys.exit(1)
    
    # Load portfolio
    portfolio_df = pd.read_csv(portfolio_path)
    portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
    
    # Load trades
    if trades_path.exists():
        trades_df = pd.read_csv(trades_path)
        trades_df['Date'] = pd.to_datetime(trades_df['Date'])
    else:
        trades_df = pd.DataFrame()
        print("⚠️  No trade log found, skipping trade metrics")
    
    return portfolio_df, trades_df


def calculate_equity_series(portfolio_df: pd.DataFrame) -> tuple:
    """Calculate daily equity and cash series."""
    # Group by date and get last values
    daily_data = portfolio_df.groupby('Date').agg({
        'Total Equity': 'last',
        'Cash Balance': 'last'
    })
    
    # Convert to numeric (handle any string values)
    daily_data['Total Equity'] = pd.to_numeric(daily_data['Total Equity'], errors='coerce')
    daily_data['Cash Balance'] = pd.to_numeric(daily_data['Cash Balance'], errors='coerce')
    
    equity_series = daily_data['Total Equity']
    cash_series = daily_data['Cash Balance']
    
    return equity_series, cash_series


def fetch_benchmark_data(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.Series:
    """Fetch S&P 500 benchmark data."""
    print(f"[INFO] Fetching S&P 500 data from {start_date.date()} to {end_date.date()}...")
    
    try:
        sp500 = yf.download('^GSPC', start=start_date, end=end_date, progress=False)
        
        if sp500.empty:
            print("[WARNING] No S&P 500 data retrieved")
            return pd.Series(dtype=float)
        
        # Use Adj Close if available, else Close
        if 'Adj Close' in sp500.columns:
            benchmark = sp500['Adj Close']
        else:
            benchmark = sp500['Close']
        
        # Ensure it's a Series
        if isinstance(benchmark, pd.DataFrame):
            benchmark = benchmark.iloc[:, 0]
        
        return benchmark
    
    except Exception as e:
        print(f"[WARNING] Failed to fetch benchmark data: {e}")
        return pd.Series(dtype=float)


def prepare_holdings_df(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare current holdings DataFrame for visualizations."""
    # Get latest date
    latest_date = portfolio_df['Date'].max()
    holdings = portfolio_df[portfolio_df['Date'] == latest_date].copy()
    
    # Ensure required columns exist and rename for compatibility
    if 'Ticker' in holdings.columns:
        holdings = holdings.rename(columns={'Ticker': 'ticker'})
    
    if 'Total Value' in holdings.columns:
        holdings = holdings.rename(columns={'Total Value': 'current_value'})
        holdings['current_value'] = pd.to_numeric(holdings['current_value'], errors='coerce')
    
    return holdings[['ticker', 'current_value']].dropna()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='FASE 2: Interactive Analytics & Reporting')
    parser.add_argument(
        '--data-dir',
        type=str,
        default='Start Your Own',
        help='Directory containing portfolio CSV files'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='reports',
        help='Output directory for reports'
    )
    
    args = parser.parse_args()
    
    # Setup paths
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("FASE 2: ADVANCED ANALYTICS & REPORTING (INTERACTIVE)")
    print("=" * 70)
    
    # Step 1: Load data
    print("\n[STEP 1] Loading portfolio data...")
    portfolio_df, trades_df = load_portfolio_data(data_dir)
    
    if portfolio_df.empty:
        print("❌ Portfolio is empty. Add some data first!")
        print("\nRun the trading script to populate your portfolio.")
        sys.exit(0)
    
    print(f"  ✅ Portfolio: {len(portfolio_df)} records")
    print(f"  ✅ Trades: {len(trades_df)} records")
    
    # Step 2: Calculate equity series
    print("\n[STEP 2] Calculating equity series...")
    equity, cash = calculate_equity_series(portfolio_df)
    
    print(f"  ✅ Equity range: ${equity.min():.2f} - ${equity.max():.2f}")
    print(f"  ✅ Current equity: ${equity.iloc[-1]:.2f}")
    
    # Step 3: Fetch benchmark
    print("\n[STEP 3] Fetching S&P 500 benchmark...")
    start_date = equity.index.min()
    end_date = equity.index.max()
    
    benchmark = fetch_benchmark_data(start_date, end_date)
    
    if not benchmark.empty:
        print(f"  ✅ Benchmark data: {len(benchmark)} days")
    else:
        print("  ⚠️  Benchmark data unavailable (will skip CAPM)")
    
    # Step 4: Calculate metrics
    print("\n[STEP 4] Calculating advanced metrics...")
    calculator = MetricsCalculator(risk_free_rate=0.05)
    
    metrics = calculator.calculate_all_metrics(
        equity_series=equity,
        trades_df=trades_df,
        benchmark_ticker='^GSPC' if not benchmark.empty else None
    )
    
    # Print key metrics
    print(f"  ✅ Sharpe Ratio (annual): {metrics.get('sharpe_annual', 0):.2f}")
    print(f"  ✅ Sortino Ratio (annual): {metrics.get('sortino_annual', 0):.2f}")
    print(f"  ✅ Beta: {metrics.get('beta', 0):.2f}")
    print(f"  ✅ Alpha (annual): {metrics.get('alpha_annual', 0):.1f}%")
    print(f"  ✅ Max Drawdown: {metrics.get('max_drawdown', 0):.1f}%")
    print(f"  ✅ Win Rate: {metrics.get('win_rate', 0):.1f}%")
    
    # Step 4.5: Generate AI insights (optional)
    print("\n[STEP 4.5] Generating AI insights...")
    llm_insights = None
    try:
        from core import create_insights_generator
        import os
        
        if os.getenv('OPENROUTER_API_KEY'):
            llm_gen = create_insights_generator()
            if llm_gen:
                # Prepare trades summary
                trades_summary = {
                    'total_trades': len(trades_df) if not trades_df.empty else 0,
                    'win_rate': metrics.get('win_rate', 0),
                    'winning_trades': metrics.get('winning_trades', 0),
                    'losing_trades': metrics.get('losing_trades', 0),
                    'avg_win': metrics.get('avg_win', 0),
                    'avg_loss': metrics.get('avg_loss', 0),
                    'profit_factor': metrics.get('profit_factor', 0)
                }
                
                # Portfolio summary for insights
                portfolio_summary_for_llm = {
                    'total_equity': equity.iloc[-1],
                    'cash_balance': cash.iloc[-1],
                    'roi_percent': ((equity.iloc[-1] / equity.iloc[0]) - 1) * 100,
                    'num_positions': prepare_holdings_df(portfolio_df).shape[0] if not portfolio_df.empty else 0
                }
                
                llm_insights = llm_gen.generate_insights(
                    portfolio_summary_for_llm,
                    metrics,
                    trades_summary
                )
                
                if llm_insights:
                    print(f"  ✅ AI insights generated ({llm_insights.get('metadata', {}).get('tokens_used', 'N/A')} tokens)")
                else:
                    print("  ⚠️  No insights generated (API may have failed)")
        else:
            print("  ⚠️  Skipping AI insights: OPENROUTER_API_KEY not set")
            print("     Set it with: $env:OPENROUTER_API_KEY='your-key'")
    except ImportError:
        print("  ⚠️  LLM insights not available (module not found)")
    except Exception as e:
        print(f"  ⚠️  Skipping AI insights: {e}")
    
    # Step 5: Generate visualizations
    print("\n[STEP 5] Generating visualizations...")
    
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    
    if HAS_PLOTLY:
        print("  🎨 Using INTERACTIVE Plotly charts (zoom, pan, hover)...")
        viz = InteractiveVisualizationGenerator(output_dir=charts_dir)
    else:
        print("  🎨 Using static matplotlib charts...")
        viz = VisualizationGenerator(output_dir=charts_dir)
    
    # Prepare holdings
    holdings_df = prepare_holdings_df(portfolio_df)
    
    # Generate all charts
    chart_paths = viz.generate_all_plots(
        portfolio_equity=equity,
        trades_df=trades_df,
        cash_series=cash,
        benchmark_data=benchmark if not benchmark.empty else None,
        holdings_df=holdings_df if not holdings_df.empty else None
    )
    
    print(f"\n  📊 Generated {len(chart_paths)} charts in: {charts_dir}")
    
    # Step 6: Generate HTML report
    print("\n[STEP 6] Generating HTML report...")
    reporter = HTMLReportGenerator()
    
    # Portfolio summary
    portfolio_summary = {
        'total_equity': equity.iloc[-1],
        'cash_balance': cash.iloc[-1],
        'total_pnl': equity.iloc[-1] - equity.iloc[0],
        'roi_percent': ((equity.iloc[-1] / equity.iloc[0]) - 1) * 100,
        'num_positions': len(holdings_df) if not holdings_df.empty else 0
    }
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = output_dir / f"report_{timestamp}.html"
    
    reporter.generate_full_report(
        output_path=str(report_path),
        portfolio_summary=portfolio_summary,
        metrics=metrics,
        chart_paths=chart_paths,
        holdings_df=holdings_df if not holdings_df.empty else None,
        llm_insights=llm_insights
    )
    
    print(f"  ✅ HTML report saved to: {report_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ FASE 2 COMPLETE!")
    print("=" * 70)
    
    print(f"\nGenerated Files:")
    print(f"  📊 Charts: {len(chart_paths)} visualizations in {charts_dir}")
    if HAS_PLOTLY:
        print(f"     ⚡ INTERACTIVE HTML charts (zoom, pan, hover tooltips)")
    else:
        print(f"     📷 Static PNG images")
    print(f"  📄 Report: {report_path}")
    
    print(f"\nKey Metrics:")
    print(f"  • Total Equity: ${portfolio_summary['total_equity']:,.2f}")
    print(f"  • ROI: {portfolio_summary['roi_percent']:+.2f}%")
    print(f"  • Sharpe Ratio: {metrics.get('sharpe_annual', 0):.2f}")
    print(f"  • Max Drawdown: {metrics.get('max_drawdown', 0):.1f}%")
    print(f"  • Win Rate: {metrics.get('win_rate', 0):.1f}%")
    
    if HAS_PLOTLY:
        print(f"\n💡 Open {report_path} in your browser to explore INTERACTIVE charts!")
    else:
        print(f"\n💡 Install Plotly for interactive charts:")
        print(f"   pip install plotly")
    
    print()


if __name__ == '__main__':
    main()

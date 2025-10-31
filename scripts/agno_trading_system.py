"""
🤖 Agno Multi-Agent Trading System
==================================

Sistema de trading automatizado usando Agno Framework con:
- DeepSeek como proveedor principal
- OpenRouter como fallback
- Multi-agentes especializados
- Custom tools para portfolio management

Uso:
    python agno_trading_system.py --provider deepseek
    python agno_trading_system.py --provider openrouter --model gemini-2.0-flash
    python agno_trading_system.py --dry-run  # Solo análisis, sin trades
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# Agno Framework imports
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.yfinance import YFinanceTools

# Local imports
from llm_config import get_llm_response, llm_config

# ============================================================================
# CUSTOM TOOLS - Integración con sistema existente
# ============================================================================


class PortfolioAnalyzerTool:
    """Custom tool para analizar el portfolio actual"""

    def __init__(self, data_dir: str = "Scripts and CSV Files"):
        self.data_dir = Path(data_dir)
        self.portfolio_file = self.data_dir / "chatgpt_portfolio_update.csv"
        self.trade_log_file = self.data_dir / "chatgpt_trade_log.csv"

    def get_current_portfolio(self) -> str:
        """Lee el portfolio actual y retorna un resumen"""
        try:
            if not self.portfolio_file.exists():
                return "No portfolio file found. Starting with empty portfolio."

            df = pd.read_csv(self.portfolio_file)
            if df.empty:
                return "Portfolio is empty."

            latest = df.groupby("Ticker").last()

            summary = "📊 Current Portfolio:\n\n"
            for ticker, row in latest.iterrows():
                summary += f"• {ticker}: {row['Shares']} shares @ ${row['Current Price']:.2f}\n"
                summary += f"  Cost Basis: ${row['Cost Basis']:.2f} | P&L: ${row['PnL']:.2f}\n"

            total_value = latest["Total Value"].sum()
            cash = latest["Cash Balance"].iloc[0] if "Cash Balance" in latest.columns else 0

            summary += f"\n💰 Cash: ${cash:.2f}\n"
            summary += f"📈 Total Equity: ${total_value + cash:.2f}\n"

            return summary
        except Exception as e:
            return f"Error reading portfolio: {str(e)}"

    def get_trade_history(self, limit: int = 10) -> str:
        """Lee el historial de trades"""
        try:
            if not self.trade_log_file.exists():
                return "No trade history found."

            df = pd.read_csv(self.trade_log_file)
            if df.empty:
                return "No trades yet."

            recent = df.tail(limit)

            summary = f"📜 Last {limit} Trades:\n\n"
            for _, row in recent.iterrows():
                action = "BUY" if row["Shares Bought"] > 0 else "SELL"
                ticker = row["Ticker"]
                shares = row["Shares Bought"] if action == "BUY" else row["Shares Sold"]
                price = row["Buy Price"] if action == "BUY" else row["Sell Price"]

                summary += f"• {row['Date']}: {action} {shares} {ticker} @ ${price:.2f}\n"
                if pd.notna(row["Reason"]):
                    summary += f"  Reason: {row['Reason']}\n"

            return summary
        except Exception as e:
            return f"Error reading trade history: {str(e)}"

    def calculate_performance_metrics(self) -> str:
        """Calcula métricas de performance del portfolio"""
        try:
            if not self.portfolio_file.exists():
                return "No data available for metrics calculation."

            df = pd.read_csv(self.portfolio_file)
            if df.empty:
                return "No portfolio data."

            latest = df.groupby("Ticker").last()

            total_cost = latest["Cost Basis"].sum()
            total_value = latest["Total Value"].sum()
            total_pnl = latest["PnL"].sum()

            if total_cost > 0:
                roi = (total_pnl / total_cost) * 100
            else:
                roi = 0

            metrics = "📊 Performance Metrics:\n\n"
            metrics += f"• Total Cost Basis: ${total_cost:.2f}\n"
            metrics += f"• Current Value: ${total_value:.2f}\n"
            metrics += f"• Total P&L: ${total_pnl:.2f}\n"
            metrics += f"• ROI: {roi:.2f}%\n"

            # Winners vs Losers
            winners = len(latest[latest["PnL"] > 0])
            losers = len(latest[latest["PnL"] < 0])

            metrics += f"\n📈 Winners: {winners} | 📉 Losers: {losers}\n"

            return metrics
        except Exception as e:
            return f"Error calculating metrics: {str(e)}"


class RiskAnalyzerTool:
    """Custom tool para análisis de riesgo"""

    def __init__(self, data_dir: str = "Scripts and CSV Files"):
        self.data_dir = Path(data_dir)
        self.portfolio_file = self.data_dir / "chatgpt_portfolio_update.csv"

    def analyze_position_risk(self, ticker: str) -> str:
        """Analiza el riesgo de una posición específica"""
        try:
            if not self.portfolio_file.exists():
                return f"No portfolio data for {ticker}"

            df = pd.read_csv(self.portfolio_file)
            ticker_data = df[df["Ticker"] == ticker]

            if ticker_data.empty:
                return f"No position found for {ticker}"

            latest = ticker_data.iloc[-1]

            risk_analysis = f"⚠️ Risk Analysis for {ticker}:\n\n"

            # Stop Loss
            if pd.notna(latest.get("Stop Loss", None)):
                stop_loss = latest["Stop Loss"]
                current_price = latest["Current Price"]
                risk_pct = ((current_price - stop_loss) / current_price) * 100

                risk_analysis += f"• Stop Loss: ${stop_loss:.2f}\n"
                risk_analysis += f"• Current Price: ${current_price:.2f}\n"
                risk_analysis += f"• Risk: {risk_pct:.2f}%\n"

            # P&L
            pnl = latest.get("PnL", 0)
            cost_basis = latest.get("Cost Basis", 0)

            if cost_basis > 0:
                pnl_pct = (pnl / cost_basis) * 100
                risk_analysis += f"• Current P&L: ${pnl:.2f} ({pnl_pct:.2f}%)\n"

            return risk_analysis
        except Exception as e:
            return f"Error analyzing risk for {ticker}: {str(e)}"

    def calculate_portfolio_risk(self) -> str:
        """Calcula el riesgo total del portfolio"""
        try:
            if not self.portfolio_file.exists():
                return "No portfolio data available"

            df = pd.read_csv(self.portfolio_file)
            if df.empty:
                return "Empty portfolio"

            latest = df.groupby("Ticker").last()

            total_value = latest["Total Value"].sum()

            risk_summary = "⚠️ Portfolio Risk Analysis:\n\n"

            # Concentración por posición
            risk_summary += "Position Concentration:\n"
            for ticker, row in latest.iterrows():
                concentration = (row["Total Value"] / total_value) * 100
                risk_summary += f"• {ticker}: {concentration:.1f}%\n"

            # Diversificación
            num_positions = len(latest)
            risk_summary += f"\n📊 Diversification: {num_positions} positions\n"

            if num_positions < 3:
                risk_summary += "⚠️ LOW DIVERSIFICATION - High risk!\n"
            elif num_positions < 5:
                risk_summary += "⚠️ MODERATE DIVERSIFICATION\n"
            else:
                risk_summary += "✅ GOOD DIVERSIFICATION\n"

            return risk_summary
        except Exception as e:
            return f"Error calculating portfolio risk: {str(e)}"


# ============================================================================
# AGNO AGENTS - Sistema Multi-Agente
# ============================================================================


def create_data_analyst_agent(provider: str = "deepseek", model: Optional[str] = None) -> Agent:
    """
    Agente especializado en análisis de datos y portfolio
    """

    # Seleccionar modelo
    if provider == "deepseek":
        agent_model = DeepSeek(id=model or "deepseek-chat")
    else:  # openrouter
        agent_model = OpenAIChat(
            id=model or "google/gemini-2.0-flash-exp:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    # Custom tools
    portfolio_tool = PortfolioAnalyzerTool()

    agent = Agent(
        name="Data Analyst",
        model=agent_model,
        role="Portfolio data analyst and performance tracker",
        description="""You are a data analyst specializing in portfolio analysis.
        Your job is to:
        - Analyze current portfolio holdings
        - Track performance metrics
        - Identify trends in trade history
        - Provide quantitative insights
        """,
        instructions=[
            "Always start by checking the current portfolio state",
            "Calculate key metrics: ROI, win rate, average P&L",
            "Identify best and worst performing positions",
            "Use tables and bullet points for clarity",
            "Be precise with numbers and percentages",
        ],
        markdown=True,
    )

    # Agregar métodos como tools personalizados
    # Nota: Agno permite custom tools via Python callables

    return agent


def create_market_researcher_agent(
    provider: str = "deepseek", model: Optional[str] = None
) -> Agent:
    """
    Agente especializado en research de mercado
    """

    if provider == "deepseek":
        agent_model = DeepSeek(id=model or "deepseek-chat")
    else:
        agent_model = OpenAIChat(
            id=model or "google/gemini-2.0-flash-exp:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    agent = Agent(
        name="Market Researcher",
        model=agent_model,
        role="Market research and stock analysis specialist",
        tools=[
            YFinanceTools(
                include_tools=[
                    "get_current_stock_price",
                    "get_analyst_recommendations",
                    "get_company_info",
                    "get_company_news",
                ]
            )
        ],
        description="""You are a market research specialist focused on finding opportunities.
        Your job is to:
        - Research stock fundamentals
        - Analyze analyst recommendations
        - Track market news and sentiment
        - Find micro-cap opportunities
        """,
        instructions=[
            "Focus on micro-cap stocks (market cap < $300M)",
            "Check analyst ratings and price targets",
            "Look for recent positive news catalysts",
            "Verify trading volume and liquidity",
            "Use tables to present stock data clearly",
        ],
        markdown=True,
    )

    return agent


def create_risk_manager_agent(provider: str = "deepseek", model: Optional[str] = None) -> Agent:
    """
    Agente especializado en gestión de riesgo
    """

    if provider == "deepseek":
        agent_model = DeepSeek(id=model or "deepseek-chat")
    else:
        agent_model = OpenAIChat(
            id=model or "google/gemini-2.0-flash-exp:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    risk_tool = RiskAnalyzerTool()

    agent = Agent(
        name="Risk Manager",
        model=agent_model,
        role="Risk assessment and position sizing specialist",
        description="""You are a risk management specialist.
        Your job is to:
        - Assess portfolio risk levels
        - Calculate position sizes
        - Set stop-loss levels
        - Monitor concentration risk
        - Ensure proper diversification
        """,
        instructions=[
            "Maximum 20% of portfolio in any single position",
            "Stop-loss should be set at -10% to -15%",
            "Require minimum 5 positions for diversification",
            "Flag any position exceeding risk limits",
            "Calculate risk/reward ratios for new trades",
        ],
        markdown=True,
    )

    return agent


def create_trading_strategist_agent(
    provider: str = "deepseek", model: Optional[str] = None
) -> Agent:
    """
    Agente líder que coordina decisiones de trading
    """

    # Para el strategist, usar el mejor modelo disponible
    if provider == "deepseek":
        agent_model = DeepSeek(id=model or "deepseek-chat")
    else:
        # Usar Gemini 2.0 Flash Thinking para razonamiento
        agent_model = OpenAIChat(
            id=model or "google/gemini-2.0-flash-thinking-exp:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    agent = Agent(
        name="Trading Strategist",
        model=agent_model,
        role="Lead trading strategist and decision maker",
        description="""You are the lead trading strategist coordinating all trading decisions.
        Your job is to:
        - Synthesize insights from all team members
        - Make final BUY/SELL/HOLD decisions
        - Provide clear trade rationale
        - Generate JSON-formatted trade recommendations
        """,
        instructions=[
            "Wait for input from Data Analyst, Researcher, and Risk Manager",
            "Consider all factors: fundamentals, technicals, risk, sentiment",
            "Make conservative decisions - capital preservation is key",
            "Provide confidence scores (0-100) for each recommendation",
            "Format final output as JSON with: action, ticker, shares, confidence, reason",
        ],
        markdown=True,
    )

    return agent


# ============================================================================
# TEAM ORCHESTRATION
# ============================================================================


def create_trading_team(provider: str = "deepseek", model: Optional[str] = None) -> Team:
    """
    Crea el equipo multi-agente de trading
    """

    # Crear agentes especializados
    data_analyst = create_data_analyst_agent(provider, model)
    researcher = create_market_researcher_agent(provider, model)
    risk_manager = create_risk_manager_agent(provider, model)
    strategist = create_trading_strategist_agent(provider, model)

    # Crear team con Agno
    trading_team = Team(
        name="Micro-Cap Trading Team",
        members=[data_analyst, researcher, risk_manager, strategist],
        description="""A multi-agent team for micro-cap stock trading.
        The team collaborates to:
        1. Analyze current portfolio (Data Analyst)
        2. Research market opportunities (Market Researcher)
        3. Assess risks (Risk Manager)
        4. Make trading decisions (Trading Strategist)
        """,
        instructions=[
            "Follow the sequential workflow: Data → Research → Risk → Decision",
            "Each agent should build on previous insights",
            "Prioritize capital preservation and risk management",
            "Focus on micro-cap opportunities with high potential",
            "Provide clear, actionable recommendations",
        ],
        markdown=True,
        show_members_responses=True,
    )

    return trading_team


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def run_trading_analysis(
    provider: str = "deepseek",
    model: Optional[str] = None,
    data_dir: str = "Scripts and CSV Files",
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Ejecuta análisis de trading con el equipo multi-agente
    """

    print(f"\n{'='*60}")
    print(f"🤖 Agno Multi-Agent Trading System")
    print(f"{'='*60}")
    print(f"Provider: {provider}")
    print(f"Model: {model or 'default'}")
    print(f"Data Dir: {data_dir}")
    print(f"Mode: {'DRY RUN (no trades)' if dry_run else 'LIVE TRADING'}")
    print(f"{'='*60}\n")

    # Crear equipo
    team = create_trading_team(provider, model)

    # Portfolio tools para contexto
    portfolio_tool = PortfolioAnalyzerTool(data_dir)
    risk_tool = RiskAnalyzerTool(data_dir)

    # Construir prompt con contexto del portfolio
    today = datetime.now().strftime("%Y-%m-%d")

    context_prompt = f"""
📅 Date: {today}

{portfolio_tool.get_current_portfolio()}

{portfolio_tool.get_trade_history(limit=5)}

{risk_tool.calculate_portfolio_risk()}

---

**TASK**: Analyze the current portfolio and market conditions, then provide trading recommendations.

**WORKFLOW**:
1. Data Analyst: Review portfolio performance and key metrics
2. Market Researcher: Find potential buy opportunities (micro-cap stocks)
3. Risk Manager: Assess current risk levels and position sizing
4. Trading Strategist: Make final BUY/SELL/HOLD recommendations

**OUTPUT FORMAT** (Trading Strategist final response):
```json
{{
    "date": "{today}",
    "analysis_summary": "Brief summary of market conditions and portfolio state",
    "recommendations": [
        {{
            "action": "BUY|SELL|HOLD",
            "ticker": "TICKER",
            "shares": 100,
            "price_target": 10.50,
            "confidence": 85,
            "reason": "Detailed reasoning for this trade",
            "risk_level": "LOW|MEDIUM|HIGH"
        }}
    ],
    "risk_assessment": "Overall portfolio risk assessment",
    "next_steps": "Suggested actions for next trading session"
}}
```

Begin analysis now.
"""

    print("🚀 Starting team analysis...\n")

    # Ejecutar team
    response = team.run(context_prompt)

    print(f"\n{'='*60}")
    print("✅ Analysis Complete")
    print(f"{'='*60}\n")

    # Mostrar response
    print(response.content)

    # Si no es dry run, aquí se ejecutarían los trades
    if not dry_run:
        print("\n⚠️ LIVE TRADING MODE: Trades would be executed here")
        print("(Implementation needed in trading_script.py)")

    return {
        "date": today,
        "provider": provider,
        "model": model,
        "response": response.content,
        "dry_run": dry_run,
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agno Multi-Agent Trading System")
    parser.add_argument(
        "--provider",
        type=str,
        default="deepseek",
        choices=["deepseek", "openrouter"],
        help="LLM provider (default: deepseek)",
    )
    parser.add_argument(
        "--model", type=str, help="Specific model to use (default: provider's default)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="Scripts and CSV Files",
        help="Directory containing portfolio CSV files",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run analysis without executing trades"
    )

    args = parser.parse_args()

    # Verificar API keys
    if args.provider == "deepseek":
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("❌ Error: DEEPSEEK_API_KEY not found in environment")
            print("Get your key at: https://platform.deepseek.com/")
            return
    else:  # openrouter
        if not os.getenv("OPENROUTER_API_KEY"):
            print("❌ Error: OPENROUTER_API_KEY not found in environment")
            print("Get your FREE key at: https://openrouter.ai/keys")
            return

    # Ejecutar análisis
    try:
        result = run_trading_analysis(
            provider=args.provider, model=args.model, data_dir=args.data_dir, dry_run=args.dry_run
        )

        print("\n✅ Trading analysis completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

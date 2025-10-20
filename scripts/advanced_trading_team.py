"""
Advanced Multi-Agent Trading System with Specialized OpenRouter Models
Uses 5 specialized free models from OpenRouter for different trading tasks
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.team import Team
from agno.models.openrouter import OpenRouter
from agno.models.deepseek import DeepSeek
from agno.tools.yfinance import YFinanceTools

# Load environment variables
load_dotenv()

# Model Configuration
MODELS = {
    "deep_research": "alibaba/tongyi-deepresearch-30b-a3b:free",  # Market research
    "reasoning": "tngtech/deepseek-r1t2-chimera:free",  # Complex decisions
    "fast_calc": "nvidia/nemotron-nano-9b-v2:free",  # Quick calculations
    "general": "z-ai/glm-4.5-air:free",  # General analysis
    "advanced": "qwen/qwen3-235b-a22b:free",  # Strategy planning
    "deepseek": "deepseek-chat"  # Fallback/primary
}


class PortfolioMemoryManager:
    """In-memory portfolio manager using DataFrames instead of CSV"""
    
    def __init__(self, initial_cash: float = 100.0):
        import pandas as pd
        from datetime import datetime
        
        self.cash = initial_cash
        self.initial_cash = initial_cash
        
        # Portfolio holdings (in-memory)
        self.holdings = pd.DataFrame(columns=[
            'ticker', 'shares', 'buy_price', 'buy_date', 
            'current_price', 'current_value', 'pnl', 'pnl_pct'
        ])
        
        # Trade history (in-memory)
        self.trades = pd.DataFrame(columns=[
            'date', 'ticker', 'action', 'shares', 'price', 
            'cost', 'cash_after', 'reason'
        ])
        
        self.last_update = datetime.now()
    
    def get_portfolio_summary(self) -> dict:
        """Get current portfolio state as dict"""
        import pandas as pd
        
        total_invested = self.holdings['current_value'].sum() if not self.holdings.empty else 0
        total_equity = self.cash + total_invested
        total_pnl = self.holdings['pnl'].sum() if not self.holdings.empty else 0
        roi = ((total_equity - self.initial_cash) / self.initial_cash * 100)
        
        return {
            'cash': self.cash,
            'invested': total_invested,
            'total_equity': total_equity,
            'total_pnl': total_pnl,
            'roi': roi,
            'num_positions': len(self.holdings),
            'holdings': self.holdings.to_dict('records') if not self.holdings.empty else [],
            'last_update': self.last_update.isoformat()
        }
    
    def add_position(self, ticker: str, shares: float, price: float, reason: str = ""):
        """Add new position to portfolio"""
        import pandas as pd
        from datetime import datetime
        
        cost = shares * price
        
        if cost > self.cash:
            return {"success": False, "message": f"Insufficient cash. Need ${cost:.2f}, have ${self.cash:.2f}"}
        
        # Update cash
        self.cash -= cost
        
        # Add to holdings
        new_holding = pd.DataFrame([{
            'ticker': ticker,
            'shares': shares,
            'buy_price': price,
            'buy_date': datetime.now(),
            'current_price': price,
            'current_value': cost,
            'pnl': 0,
            'pnl_pct': 0
        }])
        
        self.holdings = pd.concat([self.holdings, new_holding], ignore_index=True)
        
        # Log trade
        new_trade = pd.DataFrame([{
            'date': datetime.now(),
            'ticker': ticker,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'cost': cost,
            'cash_after': self.cash,
            'reason': reason
        }])
        
        self.trades = pd.concat([self.trades, new_trade], ignore_index=True)
        
        return {"success": True, "message": f"Bought {shares} shares of {ticker} at ${price:.2f}"}
    
    def update_prices(self, price_data: dict):
        """Update current prices for all holdings"""
        from datetime import datetime
        
        for idx, row in self.holdings.iterrows():
            ticker = row['ticker']
            if ticker in price_data:
                current_price = price_data[ticker]
                self.holdings.at[idx, 'current_price'] = current_price
                self.holdings.at[idx, 'current_value'] = row['shares'] * current_price
                self.holdings.at[idx, 'pnl'] = (current_price - row['buy_price']) * row['shares']
                self.holdings.at[idx, 'pnl_pct'] = ((current_price - row['buy_price']) / row['buy_price']) * 100
        
        self.last_update = datetime.now()


def create_market_researcher(use_openrouter: bool = True):
    """Agent specialized in deep market research using Tongyi DeepResearch"""
    
    model = (
        OpenRouter(id=MODELS["deep_research"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    return Agent(
        name="Market Researcher",
        role="Deep market analysis specialist",
        model=model,
        tools=[YFinanceTools(include_tools=["get_current_stock_price", "get_company_info", "get_company_news"])],
        instructions=[
            "You are a market research specialist focused on micro-cap stocks",
            "Provide comprehensive analysis of market trends, company news, and sector dynamics",
            "Use YFinance tools to gather real-time market data",
            "Focus on identifying high-potential micro-cap opportunities",
            "Consider both fundamental and technical factors",
            "Be thorough but concise in your analysis"
        ],
        markdown=True,
    )


def create_risk_analyst(use_openrouter: bool = True):
    """Agent specialized in risk analysis using Nemotron Nano for fast calculations"""
    
    model = (
        OpenRouter(id=MODELS["fast_calc"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    return Agent(
        name="Risk Analyst",
        role="Risk assessment and portfolio calculations",
        model=model,
        instructions=[
            "You are a risk management specialist",
            "Calculate portfolio metrics: volatility, concentration, drawdown risk",
            "Assess position sizing based on risk tolerance",
            "Recommend stop-loss levels and position limits",
            "Focus on capital preservation",
            "Provide quick, accurate numerical analysis"
        ],
        markdown=True,
    )


def create_trading_strategist(use_openrouter: bool = True):
    """Agent for complex reasoning and trade decisions using DeepSeek R1T2 Chimera"""
    
    model = (
        OpenRouter(id=MODELS["reasoning"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    return Agent(
        name="Trading Strategist",
        role="Strategic decision maker with advanced reasoning",
        model=model,
        instructions=[
            "You are the chief trading strategist",
            "Synthesize market research and risk analysis into actionable decisions",
            "Use logical reasoning to evaluate trade opportunities",
            "Consider: risk/reward, timing, market conditions, portfolio balance",
            "Provide clear BUY/SELL/HOLD recommendations with detailed reasoning",
            "Think step-by-step through complex trade scenarios",
            "Always explain your decision-making process"
        ],
        markdown=True,
    )


def create_portfolio_manager(use_openrouter: bool = True):
    """Agent for overall strategy using Qwen3 235B for advanced planning"""
    
    model = (
        OpenRouter(id=MODELS["advanced"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    # Simple portfolio context without external tool
    portfolio_context = "Demo portfolio - analyzing individual stocks for potential investment"
    
    return Agent(
        name="Portfolio Manager",
        role="Overall strategy and portfolio optimization",
        model=model,
        instructions=[
            "You are the portfolio manager overseeing the entire trading operation",
            "Review current portfolio composition and performance",
            "Set strategic direction and allocation targets",
            "Ensure diversification and risk management",
            "Make final decisions on trade execution",
            "Provide comprehensive 3-6 month strategic plans",
            f"Current portfolio context: {portfolio_context}"
        ],
        markdown=True,
    )


def create_trading_team(use_openrouter: bool = True):
    """Create coordinated team of specialized agents"""
    
    # Create all agents
    researcher = create_market_researcher(use_openrouter)
    risk_analyst = create_risk_analyst(use_openrouter)
    strategist = create_trading_strategist(use_openrouter)
    portfolio_mgr = create_portfolio_manager(use_openrouter)
    
    # Create team with sequential workflow
    team = Team(
        name="Trading Analysis Team",
        members=[researcher, risk_analyst, strategist, portfolio_mgr],
        instructions=[
            "Work together to analyze trading opportunities",
            "Market Researcher: Gather and analyze market data first",
            "Risk Analyst: Calculate risk metrics and position sizing",
            "Trading Strategist: Make BUY/SELL/HOLD recommendations",
            "Portfolio Manager: Make final decision and provide action plan"
        ],
        markdown=True,
    )
    
    return team


def analyze_stock(ticker: str, use_openrouter: bool = True, dry_run: bool = True):
    """Analyze a specific stock using the multi-agent team"""
    
    print(f"\n{'='*70}")
    print(f"ANALYZING STOCK: {ticker}")
    print(f"Provider: {'OpenRouter' if use_openrouter else 'DeepSeek'}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    # Create team
    team = create_trading_team(use_openrouter)
    
    # Analysis query
    query = f"""
Analyze {ticker} as a potential micro-cap investment opportunity.

Please provide:
1. Market Research: Current price, company info, recent news, sector trends
2. Risk Analysis: Volatility, position sizing recommendation, stop-loss levels
3. Trading Decision: BUY/SELL/HOLD with clear reasoning
4. Portfolio Impact: How this fits into overall $100 portfolio strategy

Current constraints:
- Maximum position size: $30 (30% of portfolio)
- Minimum cash reserve: $20 (20% of portfolio)
- Risk tolerance: Moderate (willing to accept volatility for growth)
"""
    
    # Run team analysis
    team.print_response(query, stream=True)
    
    print(f"\n{'='*70}")
    print(f"ANALYSIS COMPLETE: {ticker}")
    print(f"{'='*70}\n")


def run_daily_analysis(use_openrouter: bool = True, dry_run: bool = True):
    """Run daily portfolio analysis"""
    
    print(f"\n{'='*70}")
    print(f"DAILY PORTFOLIO ANALYSIS - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Provider: {'OpenRouter (5 specialized models)' if use_openrouter else 'DeepSeek'}")
    print(f"{'='*70}\n")
    
    # Create team
    team = create_trading_team(use_openrouter)
    
    # Daily analysis query
    query = """
Conduct a comprehensive daily portfolio review:

1. PORTFOLIO STATUS:
   - Review current holdings and cash position
   - Calculate overall performance metrics (ROI, win/loss ratio)
   - Assess portfolio diversification and concentration risk

2. MARKET RESEARCH:
   - Identify 2-3 high-potential micro-cap opportunities
   - Analyze current market trends affecting micro-caps
   - Review news on existing holdings

3. RISK ASSESSMENT:
   - Calculate portfolio volatility and drawdown risk
   - Review stop-loss levels on existing positions
   - Recommend position size adjustments if needed

4. TRADING RECOMMENDATIONS:
   - Provide specific BUY/SELL/HOLD actions with reasoning
   - Include entry/exit prices and position sizes
   - Explain risk/reward for each recommendation

5. STRATEGIC PLAN:
   - 30-day outlook and strategy
   - Portfolio rebalancing recommendations
   - Key catalysts to watch

Format the final output as a JSON object with clear action items.
"""
    
    # Run team analysis
    team.print_response(query, stream=True)
    
    print(f"\n{'='*70}")
    print(f"DAILY ANALYSIS COMPLETE")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Multi-Agent Trading System with Specialized Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze specific stock with OpenRouter models
  python advanced_trading_team.py --ticker AAPL --provider openrouter
  
  # Daily analysis with DeepSeek (stable fallback)
  python advanced_trading_team.py --daily --provider deepseek
  
  # Stock analysis with DeepSeek
  python advanced_trading_team.py --ticker TSLA --provider deepseek
  
  # Daily analysis with OpenRouter (recommended for variety)
  python advanced_trading_team.py --daily --provider openrouter

Models Used (OpenRouter):
  - Deep Research: Tongyi DeepResearch 30B (market analysis)
  - Reasoning: DeepSeek R1T2 Chimera (trade decisions)
  - Fast Calc: Nemotron Nano 9B (risk calculations)
  - General: GLM 4.5 Air (general analysis)
  - Advanced: Qwen3 235B (strategy planning)
        """
    )
    
    parser.add_argument(
        "--ticker",
        type=str,
        help="Stock ticker to analyze (e.g., AAPL, TSLA)"
    )
    
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Run daily portfolio analysis"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openrouter", "deepseek"],
        default="openrouter",
        help="LLM provider (default: openrouter)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry run mode (no actual trades)"
    )
    
    args = parser.parse_args()
    
    # Check for API keys
    use_openrouter = args.provider == "openrouter"
    
    if use_openrouter and not os.getenv("OPENROUTER_API_KEY"):
        print("\n[ERROR] OPENROUTER_API_KEY not found in .env file")
        print("Get your API key from: https://openrouter.ai/keys")
        print("\nAlternatively, use --provider deepseek")
        sys.exit(1)
    
    if not use_openrouter and not os.getenv("DEEPSEEK_API_KEY"):
        print("\n[ERROR] DEEPSEEK_API_KEY not found in .env file")
        print("Get your API key from: https://platform.deepseek.com/")
        sys.exit(1)
    
    # Run analysis
    if args.ticker:
        analyze_stock(args.ticker, use_openrouter, args.dry_run)
    elif args.daily:
        run_daily_analysis(use_openrouter, args.dry_run)
    else:
        print("\n[INFO] Please specify --ticker or --daily")
        parser.print_help()


if __name__ == "__main__":
    main()

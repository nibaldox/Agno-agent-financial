"""
Modular Agent System
====================
Load trading agents from YAML configurations.

Quick Start:
    >>> from agents import load_complete_team
    >>> team = load_complete_team()
    >>> team.print_response("Analiza ABEO", stream=True)

Individual Agents:
    >>> from agents import load_market_researcher, load_risk_analysts
    >>> researcher = load_market_researcher()
    >>> risk_analysts = load_risk_analysts()

Advanced:
    >>> from agents import AgentLoader
    >>> loader = AgentLoader()
    >>> agent = loader.load_agent("market_researcher")
"""

from .loader import (
    AgentLoader,
    load_advanced_reporter,
    load_complete_team,
    load_daily_reporter,
    load_market_researcher,
    load_portfolio_manager,
    load_risk_analysts,
    load_trading_strategists,
)

__all__ = [
    "AgentLoader",
    "load_market_researcher",
    "load_risk_analysts",
    "load_trading_strategists",
    "load_portfolio_manager",
    "load_daily_reporter",
    "load_advanced_reporter",
    "load_complete_team",
]

__version__ = "2.1.0"

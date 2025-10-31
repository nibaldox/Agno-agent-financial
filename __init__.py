"""
Agno Trading System
===================
Sistema avanzado de trading con agentes AI y analytics profesionales.

Este paquete provee:
- Sistema de 9 agentes especializados usando Agno Framework
- Analytics institucionales (FASE 2): Sharpe, Sortino, Beta, Alpha
- Visualizaciones interactivas con Plotly
- AI Insights con DeepSeek (ultra bajo costo)
- Reportes profesionales en HTML

Instalación:
    pip install -e .

Uso básico:
    >>> from agno_trading.agents import load_complete_team
    >>> team = load_complete_team()
    >>> team.print_response("Analiza ABEO", stream=True)

Documentación completa:
    Ver docs/ o README.md
"""

__version__ = "2.1.0"
__author__ = "Romamo"
__license__ = "MIT"

from .agents import (
    load_advanced_reporter,
    load_complete_team,
    load_daily_reporter,
    load_market_researcher,
    load_portfolio_manager,
    load_risk_analysts,
    load_trading_strategists,
)

# Importaciones principales para facilitar el uso
from .core import (
    HTMLReportGenerator,
    InteractiveVisualizationGenerator,
    LLMInsightsGenerator,
    MetricsCalculator,
)

__all__ = [
    # Core analytics
    "MetricsCalculator",
    "HTMLReportGenerator",
    "InteractiveVisualizationGenerator",
    "LLMInsightsGenerator",
    # Agents
    "load_complete_team",
    "load_market_researcher",
    "load_risk_analysts",
    "load_trading_strategists",
    "load_portfolio_manager",
    "load_daily_reporter",
    "load_advanced_reporter",
]

# Metadata
__all_exports__ = {
    "version": __version__,
    "author": __author__,
    "license": __license__,
}

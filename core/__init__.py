"""
Core modules for the trading system.

This package contains reusable components:
- portfolio: Portfolio management, persistence, stop-loss automation, data fetching
- validation: Trade validation logic
- analysis: Stock analysis workflows
- reporting: Report generation
- execution: Live trade execution (MOO/limit orders)
- metrics: Advanced financial metrics (Sharpe, Sortino, CAPM, etc.)
- visualization: Professional charts and plots (matplotlib-based, 15+ types)
- visualization_plotly: INTERACTIVE charts with Plotly (zoom, pan, tooltips)
- html_reports: HTML report generator with dark mode toggle and modern UI

Version: 3.7.0 - Interactive Plotly charts with modern UI (FASE 2 Enhanced)
"""

from .portfolio import PortfolioMemoryManager
from .validation import ValidationHandler
from .analysis import StockAnalyzer
from .reporting import DailyReporter
from .execution import TradeExecutor
from .metrics import MetricsCalculator
from .visualization import VisualizationGenerator
from .html_reports import HTMLReportGenerator

# Try to import LLM insights generator (optional, requires OpenRouter API key)
try:
    from .llm_insights import LLMInsightsGenerator, create_insights_generator
    _HAS_LLM_INSIGHTS = True
except ImportError:
    _HAS_LLM_INSIGHTS = False
    LLMInsightsGenerator = None
    create_insights_generator = None

# Try to import interactive Plotly visualizations (preferred)
try:
    from .visualization_plotly import InteractiveVisualizationGenerator
    _HAS_INTERACTIVE_VIZ = True
except ImportError:
    _HAS_INTERACTIVE_VIZ = False
    InteractiveVisualizationGenerator = None

__all__ = [
    'PortfolioMemoryManager',
    'ValidationHandler',
    'StockAnalyzer',
    'DailyReporter',
    'TradeExecutor',
    'MetricsCalculator',
    'VisualizationGenerator',
    'InteractiveVisualizationGenerator',
    'HTMLReportGenerator',
    'LLMInsightsGenerator',
    'create_insights_generator'
]

__version__ = '3.7.0'

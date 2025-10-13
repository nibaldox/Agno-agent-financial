"""
Daily Reporter - Handles portfolio reporting

Handles:
- Daily report generation
- Portfolio performance summaries
- Trade history formatting
- Report query building
"""

from typing import Dict, Optional
import pandas as pd


class DailyReporter:
    """
    Generates daily portfolio reports using AI reporter agent.
    
    Features:
    - Loads Daily Reporter agent from YAML
    - Formats portfolio data for reporting
    - Generates comprehensive daily summaries
    - Supports OpenRouter/DeepSeek providers
    
    Example:
        >>> reporter = DailyReporter()
        >>> reporter.generate_report(
        >>>     portfolio_summary={'cash': 100, 'roi': 5.2},
        >>>     holdings_df=portfolio.holdings,
        >>>     trades_df=portfolio.trades
        >>> )
    """
    
    def __init__(self, agents_available: bool = True):
        """
        Initialize daily reporter.
        
        Args:
            agents_available: Whether modular agent system is available
        """
        self.agents_available = agents_available
    
    def build_report_query(
        self,
        portfolio_summary: Dict,
        holdings_df: pd.DataFrame,
        trades_df: pd.DataFrame,
        num_recent_trades: int = 5
    ) -> str:
        """
        Build comprehensive report query.
        
        Args:
            portfolio_summary: Portfolio summary dict
            holdings_df: Current holdings DataFrame
            trades_df: Trades history DataFrame
            num_recent_trades: Number of recent trades to include
            
        Returns:
            str: Formatted report query
        """
        # Format holdings
        holdings_str = holdings_df.to_string() if not holdings_df.empty else "Sin posiciones"
        
        # Format recent trades
        recent_trades_str = "Sin operaciones"
        if not trades_df.empty:
            recent = trades_df.tail(num_recent_trades)
            recent_trades_str = recent.to_string(index=False)
        
        query = f"""
Genera un reporte diario completo del portfolio.

ESTADO ACTUAL:
- Efectivo: ${portfolio_summary['cash']:.2f}
- Valor Posiciones: ${portfolio_summary.get('holdings_value', 0):.2f}
- Equity Total: ${portfolio_summary['total_equity']:.2f}
- ROI: {portfolio_summary['roi']:.2f}%
- Posiciones: {portfolio_summary['num_positions']}

HOLDINGS:
{holdings_str}

ÚLTIMAS {num_recent_trades} OPERACIONES:
{recent_trades_str}

Incluye:
1. Resumen de rendimiento
2. Análisis de posiciones
3. Cambios desde ayer
4. Eventos de mercado relevantes
5. Métricas de riesgo

⚠️ CRÍTICO: Responder ÚNICAMENTE en ESPAÑOL
"""
        return query
    
    def load_reporter_agent(
        self,
        use_openrouter: bool = True,
        portfolio_summary: Optional[Dict] = None
    ):
        """
        Load Daily Reporter agent from YAML config.
        
        Args:
            use_openrouter: Provider selection
            portfolio_summary: Optional portfolio context
            
        Returns:
            Agent: Loaded Daily Reporter agent
        """
        if not self.agents_available:
            raise ImportError("Modular agent system not available")
        
        try:
            from agents import load_daily_reporter
            
            reporter = load_daily_reporter(
                use_openrouter=use_openrouter,
                portfolio_summary=portfolio_summary
            )
            
            return reporter
        except Exception as e:
            raise ImportError(f"Error loading daily reporter: {e}")
    
    def generate_report(
        self,
        portfolio_summary: Dict,
        holdings_df: pd.DataFrame,
        trades_df: pd.DataFrame,
        use_openrouter: bool = True,
        stream: bool = True,
        verbose: bool = True
    ) -> Optional[str]:
        """
        Generate complete daily portfolio report.
        
        Args:
            portfolio_summary: Portfolio summary dict
            holdings_df: Current holdings DataFrame
            trades_df: Trades history DataFrame
            use_openrouter: Provider selection
            stream: Enable streaming output
            verbose: Print loading messages
            
        Returns:
            str: Report content (if not streaming)
        """
        if verbose:
            print("[CARGANDO DAILY REPORTER...]")
        
        # Load reporter
        try:
            reporter = self.load_reporter_agent(
                use_openrouter=use_openrouter,
                portfolio_summary=portfolio_summary
            )
            
            if verbose:
                print("✅ Daily Reporter cargado desde YAML\n")
        except Exception as e:
            if verbose:
                print(f"❌ Error cargando reporter: {e}")
            return None
        
        # Build query
        query = self.build_report_query(
            portfolio_summary,
            holdings_df,
            trades_df
        )
        
        if verbose:
            print("\n" + "="*70)
            print("GENERANDO REPORTE DIARIO")
            print("="*70 + "\n")
        
        # Generate report
        try:
            if stream:
                reporter.print_response(query, stream=True)
                return None
            else:
                response = reporter.run(query)
                return response.content
        except Exception as e:
            if verbose:
                print(f"\n❌ Error generando reporte: {e}")
            return None
    
    def format_portfolio_summary(self, portfolio_summary: Dict) -> str:
        """
        Format portfolio summary for display.
        
        Args:
            portfolio_summary: Portfolio summary dict
            
        Returns:
            str: Formatted summary string
        """
        return f"""
[ESTADO DEL PORTFOLIO]
  Efectivo: ${portfolio_summary['cash']:.2f}
  Valor Posiciones: ${portfolio_summary.get('holdings_value', 0):.2f}
  Equity Total: ${portfolio_summary['total_equity']:.2f}
  ROI: {portfolio_summary['roi']:.2f}%
  Última Actualización: {portfolio_summary.get('last_update', 'N/A')}
"""
    
    def format_holdings(self, holdings_df: pd.DataFrame) -> str:
        """
        Format holdings DataFrame for display.
        
        Args:
            holdings_df: Holdings DataFrame
            
        Returns:
            str: Formatted holdings string
        """
        if holdings_df.empty:
            return "[INFO] No hay posiciones abiertas"
        
        return f"[POSICIONES ACTUALES ({len(holdings_df)})]\n{holdings_df.to_string()}"

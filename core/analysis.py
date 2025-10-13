"""
Stock Analyzer - Handles stock analysis workflows

Handles:
- Multi-agent analysis orchestration
- Query building with portfolio context
- Team loading and execution
- Result formatting
"""

from typing import Dict, Optional
from pathlib import Path


class StockAnalyzer:
    """
    Orchestrates multi-agent stock analysis.
    
    Features:
    - Loads 9-agent trading team from YAML
    - Builds contextual analysis queries
    - Executes analysis with streaming
    - Handles different providers (OpenRouter/DeepSeek)
    
    Example:
        >>> analyzer = StockAnalyzer()
        >>> result = analyzer.analyze(
        >>>     ticker="ABEO",
        >>>     portfolio_summary={'cash': 100, 'roi': 0},
        >>>     use_openrouter=True
        >>> )
    """
    
    def __init__(self, agents_available: bool = True):
        """
        Initialize stock analyzer.
        
        Args:
            agents_available: Whether modular agent system is available
        """
        self.agents_available = agents_available
    
    def build_analysis_query(
        self,
        ticker: str,
        portfolio_summary: Dict,
        holdings_df = None
    ) -> str:
        """
        Build comprehensive analysis query with portfolio context.
        
        Args:
            ticker: Stock symbol to analyze
            portfolio_summary: Current portfolio summary dict
            holdings_df: Optional DataFrame of current holdings
            
        Returns:
            str: Formatted analysis query for agents
        """
        holdings_str = ""
        if holdings_df is not None and not holdings_df.empty:
            holdings_str = holdings_df.to_string()
        else:
            holdings_str = "Sin posiciones"
        
        query = f"""
Analiza {ticker} como potencial inversión micro-cap.

CONTEXTO DEL PORTFOLIO:
- Efectivo Disponible: ${portfolio_summary['cash']:.2f}
- Equity Total: ${portfolio_summary['total_equity']:.2f}
- ROI Actual: {portfolio_summary['roi']:.2f}%
- Posiciones Actuales: {portfolio_summary['num_positions']}

POSICIONES EXISTENTES:
{holdings_str}

INSTRUCCIONES:
1. Market Researcher: Investiga {ticker} a fondo (precio, fundamentales, noticias)
2. Risk Analysts (3): Evalúen riesgo desde perspectivas Conservadora/Moderada/Agresiva
3. Trading Strategists (3): Analicen desde enfoques Técnico/Fundamental/Momentum
4. Portfolio Manager: Sintetiza las 6 opiniones y decide
5. Daily Reporter: Resume la decisión final

REGLAS CRÍTICAS:
- Solo micro-caps (market cap < $300M)
- Máximo 30% del portfolio por posición
- Stop-loss automático a -15%
- Responder SIEMPRE en ESPAÑOL

Proporciona tu análisis y recomendación final.
"""
        return query
    
    def load_trading_team(
        self,
        use_openrouter: bool = True,
        portfolio_summary: Optional[Dict] = None
    ):
        """
        Load complete 9-agent trading team from YAML configs.
        
        Args:
            use_openrouter: If True, use OpenRouter; else DeepSeek
            portfolio_summary: Optional portfolio context for agents
            
        Returns:
            Team: Loaded trading team
            
        Raises:
            ImportError: If modular agents not available
        """
        if not self.agents_available:
            raise ImportError("Modular agent system not available")
        
        try:
            from agents import load_complete_team
            
            team = load_complete_team(
                use_openrouter=use_openrouter,
                portfolio_summary=portfolio_summary
            )
            
            return team
        except Exception as e:
            raise ImportError(f"Error loading trading team: {e}")
    
    def analyze(
        self,
        ticker: str,
        portfolio_summary: Dict,
        holdings_df = None,
        use_openrouter: bool = True,
        stream: bool = True,
        verbose: bool = True
    ) -> Optional[str]:
        """
        Run complete multi-agent analysis on a stock.
        
        Args:
            ticker: Stock symbol
            portfolio_summary: Portfolio summary dict
            holdings_df: Current holdings DataFrame
            use_openrouter: Provider selection
            stream: Enable streaming output
            verbose: Print loading messages
            
        Returns:
            str: Analysis result (if not streaming)
        """
        if verbose:
            print("[CARGANDO SISTEMA MODULAR DE AGENTES...]")
            print("├─ 1/9 Market Researcher")
            print("├─ 2-4/9 Risk Analysts (Consensus)")
            print("├─ 5-7/9 Trading Strategists (Convergence)")
            print("├─ 8/9 Portfolio Manager")
            print("└─ 9/9 Daily Reporter\n")
        
        # Load team
        try:
            team = self.load_trading_team(
                use_openrouter=use_openrouter,
                portfolio_summary=portfolio_summary
            )
            
            if verbose:
                print(f"✅ Equipo de {len(team.members)} agentes cargado desde YAML\n")
        except Exception as e:
            if verbose:
                print(f"❌ Error cargando equipo: {e}")
            return None
        
        # Build query
        query = self.build_analysis_query(ticker, portfolio_summary, holdings_df)
        
        if verbose:
            print("\n" + "="*70)
            print("EJECUTANDO ANÁLISIS MULTI-AGENTE")
            print("="*70 + "\n")
        
        # Execute analysis
        try:
            if stream:
                team.print_response(query, stream=True)
                return None
            else:
                response = team.run(query)
                return response.content
        except Exception as e:
            if verbose:
                print(f"\n❌ Error durante análisis: {e}")
            return None

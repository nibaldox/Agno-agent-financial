"""
LLM-Powered Portfolio Analyzer

Generates natural language insights and explanations for trading reports using OpenAI.
Analyzes metrics, performance, and provides actionable recommendations.
"""

from typing import Dict, Optional, List
import os
import warnings

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    warnings.warn("OpenAI not installed. Install with: pip install openai")


class LLMPortfolioAnalyzer:
    """
    Generate natural language insights from portfolio metrics using LLM.
    
    Features:
    - Executive summary in plain language
    - Performance analysis with context
    - Risk assessment and recommendations
    - Comparison with benchmarks
    - Actionable next steps
    
    Example:
        >>> analyzer = LLMPortfolioAnalyzer(api_key="sk-...")
        >>> insights = analyzer.generate_insights(metrics, portfolio_summary)
        >>> print(insights['executive_summary'])
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM analyzer.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-4o-mini for cost efficiency)
        """
        if not HAS_OPENAI:
            raise ImportError("OpenAI library required. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter"
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def _format_metrics_for_llm(
        self,
        metrics: Dict,
        portfolio_summary: Dict
    ) -> str:
        """Format metrics into a clear text prompt for the LLM."""
        
        prompt = f"""Analiza el siguiente portfolio de trading y genera insights en español:

RESUMEN DEL PORTFOLIO:
- Equity Total: ${portfolio_summary.get('total_equity', 0):,.2f}
- Cash Balance: ${portfolio_summary.get('cash_balance', 0):,.2f}
- P&L Total: ${portfolio_summary.get('total_pnl', 0):,.2f}
- ROI: {portfolio_summary.get('roi_percent', 0):.2f}%
- Posiciones Abiertas: {portfolio_summary.get('num_positions', 0)}

MÉTRICAS DE RENDIMIENTO:
- Sharpe Ratio (anual): {metrics.get('sharpe_annual', 0):.2f}
- Sortino Ratio (anual): {metrics.get('sortino_annual', 0):.2f}
- Beta: {metrics.get('beta', 0):.2f}
- Alpha (anual): {metrics.get('alpha_annual', 0):.2f}%
- Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%

ESTADÍSTICAS DE TRADING:
- Total Trades: {metrics.get('total_trades', 0)}
- Win Rate: {metrics.get('win_rate', 0):.1f}%
- Trades Ganadores: {metrics.get('winning_trades', 0)}
- Trades Perdedores: {metrics.get('losing_trades', 0)}
- Average Win: ${metrics.get('avg_win', 0):,.2f}
- Average Loss: ${metrics.get('avg_loss', 0):,.2f}
- Profit Factor: {metrics.get('profit_factor', 0):.2f}

VOLATILIDAD Y RIESGO:
- Volatilidad (anual): {metrics.get('volatility_annual', 0):.2f}%
- Downside Deviation: {metrics.get('downside_deviation', 0):.2f}%
"""
        return prompt
    
    def generate_executive_summary(
        self,
        metrics: Dict,
        portfolio_summary: Dict
    ) -> str:
        """
        Generate executive summary in natural language.
        
        Args:
            metrics: Dictionary of portfolio metrics
            portfolio_summary: Portfolio summary statistics
        
        Returns:
            str: Executive summary in Spanish
        """
        prompt = self._format_metrics_for_llm(metrics, portfolio_summary)
        
        prompt += """
Genera un RESUMEN EJECUTIVO conciso (3-4 párrafos máximo) que:
1. Describa el estado actual del portfolio en lenguaje claro
2. Destaque los puntos más importantes (positivos y negativos)
3. Use analogías o comparaciones para hacer las métricas entendibles
4. Mantenga un tono profesional pero accesible

NO uses bullets, solo párrafos narrativos. Sé directo y específico."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista financiero experto que explica métricas de trading en lenguaje claro y accesible."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            warnings.warn(f"Failed to generate executive summary: {e}")
            return "Error generando resumen ejecutivo. Verifica tu API key de OpenAI."
    
    def generate_performance_analysis(
        self,
        metrics: Dict,
        portfolio_summary: Dict
    ) -> str:
        """
        Generate detailed performance analysis.
        
        Args:
            metrics: Dictionary of portfolio metrics
            portfolio_summary: Portfolio summary statistics
        
        Returns:
            str: Performance analysis in Spanish
        """
        prompt = self._format_metrics_for_llm(metrics, portfolio_summary)
        
        prompt += """
Genera un ANÁLISIS DE RENDIMIENTO detallado que explique:

1. **ROI y Comparación con Mercado**: Explica el ROI en contexto. ¿Es bueno o malo? Compara con el Alpha para ver si supera al S&P 500.

2. **Sharpe y Sortino Ratios**: Explica qué significan estos números en términos simples. ¿El riesgo está justificado por el retorno?

3. **Drawdown**: ¿Qué tan severa fue la peor caída? ¿Es preocupante o normal para este tipo de trading?

4. **Win Rate vs Profit Factor**: Analiza la relación entre cuánto ganas vs cuántas veces ganas. ¿Es un buen balance?

Usa lenguaje claro, evita jerga técnica o explícala. Máximo 4 párrafos."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista financiero que explica métricas complejas de forma simple y práctica."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            warnings.warn(f"Failed to generate performance analysis: {e}")
            return "Error generando análisis de rendimiento."
    
    def generate_risk_assessment(
        self,
        metrics: Dict,
        portfolio_summary: Dict
    ) -> str:
        """
        Generate risk assessment and recommendations.
        
        Args:
            metrics: Dictionary of portfolio metrics
            portfolio_summary: Portfolio summary statistics
        
        Returns:
            str: Risk assessment in Spanish
        """
        prompt = self._format_metrics_for_llm(metrics, portfolio_summary)
        
        prompt += """
Genera una EVALUACIÓN DE RIESGO que incluya:

1. **Nivel de Riesgo Actual**: Basándote en Beta, volatilidad y drawdown, ¿qué tan arriesgado es este portfolio? (Bajo/Medio/Alto)

2. **Principales Riesgos Identificados**: Lista 2-3 riesgos específicos basados en las métricas.

3. **Señales de Alerta**: ¿Hay alguna métrica que requiera atención inmediata?

Sé específico y práctico. Máximo 3 párrafos."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista de riesgo que identifica problemas potenciales en portfolios de trading."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            warnings.warn(f"Failed to generate risk assessment: {e}")
            return "Error generando evaluación de riesgo."
    
    def generate_recommendations(
        self,
        metrics: Dict,
        portfolio_summary: Dict
    ) -> List[str]:
        """
        Generate actionable recommendations.
        
        Args:
            metrics: Dictionary of portfolio metrics
            portfolio_summary: Portfolio summary statistics
        
        Returns:
            List[str]: List of 3-5 specific recommendations
        """
        prompt = self._format_metrics_for_llm(metrics, portfolio_summary)
        
        prompt += """
Genera 4 RECOMENDACIONES ESPECÍFICAS Y ACCIONABLES para mejorar este portfolio.

Cada recomendación debe:
- Ser específica y accionable (no genérica)
- Estar basada directamente en las métricas
- Incluir el "por qué" (la métrica que la justifica)

Formato: Una recomendación por línea, empezando con un emoji relevante.
Ejemplo: "📊 Considera reducir posiciones en 20% - tu drawdown de -38% indica exposición muy alta"

NO numeres las recomendaciones, solo usa emojis."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asesor de trading que da recomendaciones específicas y accionables."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            # Split by lines and filter empty
            recommendations = [line.strip() for line in content.split('\n') if line.strip()]
            return recommendations
        
        except Exception as e:
            warnings.warn(f"Failed to generate recommendations: {e}")
            return ["Error generando recomendaciones."]
    
    def generate_all_insights(
        self,
        metrics: Dict,
        portfolio_summary: Dict
    ) -> Dict[str, any]:
        """
        Generate all insights at once.
        
        Args:
            metrics: Dictionary of portfolio metrics
            portfolio_summary: Portfolio summary statistics
        
        Returns:
            Dict containing all insights sections
        """
        print("\n🤖 Generando insights con LLM...")
        
        insights = {}
        
        # Executive summary
        print("  📝 Resumen ejecutivo...")
        insights['executive_summary'] = self.generate_executive_summary(
            metrics, portfolio_summary
        )
        
        # Performance analysis
        print("  📊 Análisis de rendimiento...")
        insights['performance_analysis'] = self.generate_performance_analysis(
            metrics, portfolio_summary
        )
        
        # Risk assessment
        print("  ⚠️  Evaluación de riesgo...")
        insights['risk_assessment'] = self.generate_risk_assessment(
            metrics, portfolio_summary
        )
        
        # Recommendations
        print("  💡 Recomendaciones...")
        insights['recommendations'] = self.generate_recommendations(
            metrics, portfolio_summary
        )
        
        print("  ✅ Insights generados\n")
        
        return insights

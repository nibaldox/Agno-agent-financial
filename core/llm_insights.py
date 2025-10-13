"""
LLM Insights Generator - Natural Language Portfolio Analysis

Uses DeepSeek via OpenRouter for cost-effective AI-generated insights.
Analyzes portfolio metrics and generates human-readable explanations.

Cost: ~$0.14 per 1M tokens (DeepSeek-V3) - very economical!
"""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime
import warnings

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    warnings.warn("openai package not installed. Install with: pip install openai")


class LLMInsightsGenerator:
    """
    Generate natural language insights about portfolio performance using LLM.
    
    Uses DeepSeek via OpenRouter for cost-effective analysis.
    
    Features:
    - Executive summary of performance
    - Risk analysis and recommendations
    - Trade pattern insights
    - Market context explanations
    
    Example:
        >>> generator = LLMInsightsGenerator(api_key="your-openrouter-key")
        >>> insights = generator.generate_insights(portfolio_summary, metrics)
        >>> print(insights['executive_summary'])
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek/deepseek-chat",
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Initialize LLM insights generator.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: Model to use (default: deepseek/deepseek-chat - very cheap!)
            base_url: OpenRouter API base URL
        """
        if not HAS_OPENAI:
            raise ImportError("openai package required. Install with: pip install openai")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Either:\n"
                "1. Pass api_key parameter, or\n"
                "2. Set OPENROUTER_API_KEY environment variable\n"
                "Get your key at: https://openrouter.ai/keys"
            )
        
        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
    
    def _create_analysis_prompt(
        self,
        portfolio_summary: Dict,
        metrics: Dict,
        trades_summary: Optional[Dict] = None
    ) -> str:
        """
        Create comprehensive prompt for LLM analysis.
        
        Args:
            portfolio_summary: Portfolio summary metrics
            metrics: Performance metrics (Sharpe, Sortino, etc.)
            trades_summary: Optional trade statistics
        
        Returns:
            str: Formatted prompt
        """
        prompt = f"""Eres un analista financiero experto. Analiza este portafolio de trading y genera insights en español.

**DATOS DEL PORTAFOLIO:**
- Equity Total: ${portfolio_summary.get('total_equity', 0):,.2f}
- Cash Balance: ${portfolio_summary.get('cash_balance', 0):,.2f}
- Total P&L: ${portfolio_summary.get('total_pnl', 0):,.2f}
- ROI: {portfolio_summary.get('roi_percent', 0):.2f}%
- Posiciones Abiertas: {portfolio_summary.get('num_positions', 0)}

**MÉTRICAS DE RENDIMIENTO:**
- Sharpe Ratio (anual): {metrics.get('sharpe_annual', 0):.2f}
- Sortino Ratio (anual): {metrics.get('sortino_annual', 0):.2f}
- Beta: {metrics.get('beta', 0):.2f}
- Alpha (anual): {metrics.get('alpha_annual', 0):.1f}%
- Max Drawdown: {metrics.get('max_drawdown', 0):.1f}%
- Volatilidad (anual): {metrics.get('volatility_annual', 0):.1f}%

**ESTADÍSTICAS DE TRADING:**
"""
        
        if trades_summary:
            prompt += f"""- Total Trades: {trades_summary.get('total_trades', 0)}
- Win Rate: {trades_summary.get('win_rate', 0):.1f}%
- Trades Ganadores: {trades_summary.get('winning_trades', 0)}
- Trades Perdedores: {trades_summary.get('losing_trades', 0)}
- Promedio Ganancia: ${trades_summary.get('avg_win', 0):,.2f}
- Promedio Pérdida: ${trades_summary.get('avg_loss', 0):,.2f}
- Profit Factor: {trades_summary.get('profit_factor', 0):.2f}
"""
        
        prompt += """
**GENERA UN ANÁLISIS ESTRUCTURADO EN JSON CON ESTAS SECCIONES:**

```json
{
    "executive_summary": "Resumen ejecutivo del rendimiento (2-3 oraciones concisas)",
    "performance_analysis": "Análisis detallado del rendimiento vs mercado (3-4 oraciones)",
    "risk_assessment": "Evaluación de riesgos y volatilidad (2-3 oraciones)",
    "trading_patterns": "Análisis de patrones de trading y efectividad (2-3 oraciones)",
    "recommendations": [
        "Recomendación específica 1",
        "Recomendación específica 2",
        "Recomendación específica 3"
    ],
    "key_strengths": [
        "Fortaleza principal 1",
        "Fortaleza principal 2"
    ],
    "areas_for_improvement": [
        "Área de mejora 1",
        "Área de mejora 2"
    ]
}
```

**INSTRUCCIONES:**
1. Sé específico con los números - menciona las métricas exactas
2. Compara con benchmarks estándar (Sharpe > 1 es bueno, Win Rate > 50% es positivo, etc.)
3. Identifica patrones significativos en los datos
4. Proporciona recomendaciones accionables basadas en los datos
5. Mantén un tono profesional pero accesible
6. Responde SOLO con el JSON, sin texto adicional
"""
        
        return prompt
    
    def generate_insights(
        self,
        portfolio_summary: Dict,
        metrics: Dict,
        trades_summary: Optional[Dict] = None,
        temperature: float = 0.3
    ) -> Dict:
        """
        Generate AI-powered insights about portfolio performance.
        
        Args:
            portfolio_summary: Portfolio summary metrics
            metrics: Performance metrics
            trades_summary: Optional trade statistics
            temperature: LLM temperature (0.0-1.0, lower = more focused)
        
        Returns:
            Dict: Structured insights with analysis and recommendations
        """
        try:
            # Create prompt
            prompt = self._create_analysis_prompt(
                portfolio_summary,
                metrics,
                trades_summary
            )
            
            # Call DeepSeek via OpenRouter
            print("🤖 Generating AI insights with DeepSeek...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista financiero experto especializado en análisis de portafolios de trading. Proporcionas insights claros, específicos y accionables basados en datos cuantitativos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=2000
            )
            
            # Extract and parse response
            content = response.choices[0].message.content
            
            # Remove markdown code blocks if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            insights = json.loads(content)
            
            # Add metadata
            insights['_metadata'] = {
                'model': self.model,
                'generated_at': datetime.now().isoformat(),
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
            print(f"  ✅ AI insights generated ({response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'} tokens)")
            
            return insights
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️ Failed to parse LLM response as JSON: {e}")
            print(f"  Raw response: {content[:200]}...")
            
            # Fallback: return basic structure with raw text
            return {
                'executive_summary': content[:200] if content else "Error generating insights",
                'performance_analysis': "",
                'risk_assessment': "",
                'trading_patterns': "",
                'recommendations': [],
                'key_strengths': [],
                'areas_for_improvement': [],
                '_error': str(e),
                '_raw_response': content
            }
            
        except Exception as e:
            print(f"  ❌ Error generating insights: {e}")
            
            return {
                'executive_summary': f"Error al generar insights: {str(e)}",
                'performance_analysis': "",
                'risk_assessment': "",
                'trading_patterns': "",
                'recommendations': ["Verificar configuración de API key"],
                'key_strengths': [],
                'areas_for_improvement': [],
                '_error': str(e)
            }
    
    def generate_quick_summary(
        self,
        portfolio_summary: Dict,
        metrics: Dict
    ) -> str:
        """
        Generate a quick one-paragraph summary (faster, cheaper).
        
        Args:
            portfolio_summary: Portfolio summary metrics
            metrics: Performance metrics
        
        Returns:
            str: Single paragraph summary
        """
        try:
            prompt = f"""Genera un resumen ejecutivo de 2-3 oraciones sobre este portafolio:

Equity: ${portfolio_summary.get('total_equity', 0):,.2f}
ROI: {portfolio_summary.get('roi_percent', 0):.2f}%
Sharpe: {metrics.get('sharpe_annual', 0):.2f}
Max DD: {metrics.get('max_drawdown', 0):.1f}%
Win Rate: {metrics.get('win_rate', 0):.1f}%

Sé específico y menciona los números clave."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Portafolio con ${portfolio_summary.get('total_equity', 0):,.2f} de equity y ROI de {portfolio_summary.get('roi_percent', 0):.2f}%"


def create_insights_generator(api_key: Optional[str] = None) -> Optional[LLMInsightsGenerator]:
    """
    Factory function to create insights generator with error handling.
    
    Args:
        api_key: Optional OpenRouter API key
    
    Returns:
        LLMInsightsGenerator or None if creation fails
    """
    try:
        return LLMInsightsGenerator(api_key=api_key)
    except Exception as e:
        warnings.warn(f"Could not create LLM insights generator: {e}")
        return None

"""
Advanced Multi-Agent Trading System with In-Memory Portfolio
Uses DataFrames instead of CSV for efficiency
Includes 5 specialized agents: Market Researcher, Risk Analyst, Trading Strategist, 
Portfolio Manager, and Daily Reporter
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

from agno.agent import Agent
from agno.team import Team
from agno.models.openrouter import OpenRouter
from agno.models.deepseek import DeepSeek
from agno.tools.yfinance import YFinanceTools
from agno.tools.serper import SerperTools  # Herramienta de búsqueda web

# CRITICAL: Importar validadores del sistema original
try:
    from validators import TradeValidator
    from stop_loss_monitor import AutoStopLossExecutor
    VALIDATORS_AVAILABLE = True
    print("✅ Critical validators loaded (micro-cap, position sizing, stop-loss)")
except ImportError as e:
    VALIDATORS_AVAILABLE = False
    print(f"⚠️ Critical validators not available: {e}")
    print("   Running without validation - NOT RECOMMENDED for production")

SERPER_AVAILABLE = True

# Load environment variables
load_dotenv()

# Configuración de directorios
PROJECT_ROOT = Path(__file__).parent.parent.parent
HISTORY_DIR = PROJECT_ROOT / "agente-agno" / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

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
    """In-memory portfolio manager con persistencia CSV para historial"""
    
    def __init__(self, initial_cash: float = 100.0, history_file: str | None = None):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        
        # Archivos de historial
        if history_file is None:
            self.history_file = HISTORY_DIR / "portfolio_history.csv"
            self.trades_file = HISTORY_DIR / "trades_history.csv"
            self.daily_summary_file = HISTORY_DIR / "daily_summary.csv"
        else:
            self.history_file = Path(history_file)
            self.trades_file = self.history_file.parent / "trades_history.csv"
            self.daily_summary_file = self.history_file.parent / "daily_summary.csv"
        
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
        
        # Cargar historial si existe
        self._load_history()
    
    def _load_history(self):
        """Carga el historial desde archivos CSV"""
        try:
            if self.history_file.exists():
                history_df = pd.read_csv(self.history_file)
                if not history_df.empty:
                    last_row = history_df.iloc[-1]
                    self.cash = last_row['cash']
                    self.initial_cash = last_row['initial_cash']
                    print(f"[INFO] Historial cargado: Cash ${self.cash:.2f}, ROI {last_row['roi']:.2f}%")
            
            if self.trades_file.exists():
                self.trades = pd.read_csv(self.trades_file, parse_dates=['date'])
                print(f"[INFO] {len(self.trades)} operaciones históricas cargadas")
        except Exception as e:
            print(f"[WARNING] Error cargando historial: {e}")
    
    def save_daily_snapshot(self):
        """Guarda snapshot diario del portafolio"""
        summary = self.get_portfolio_summary()
        
        snapshot = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cash': self.cash,
            'invested': summary['invested'],
            'total_equity': summary['total_equity'],
            'total_pnl': summary['total_pnl'],
            'roi': summary['roi'],
            'num_positions': summary['num_positions'],
            'initial_cash': self.initial_cash
        }
        
        # Guardar en CSV
        df = pd.DataFrame([snapshot])
        if self.daily_summary_file.exists():
            df.to_csv(self.daily_summary_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.daily_summary_file, index=False)
        
        print(f"[INFO] Snapshot guardado: Equity ${summary['total_equity']:.2f}, ROI {summary['roi']:.2f}%")
    
    def get_historical_performance(self) -> dict:
        """Obtiene métricas de rendimiento histórico"""
        if not self.daily_summary_file.exists():
            return {
                'total_days': 0,
                'best_day': None,
                'worst_day': None,
                'total_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'current_roi': 0,
                'peak_equity': self.initial_cash,
                'max_drawdown': 0
            }
        
        df = pd.read_csv(self.daily_summary_file)
        
        # Calcular retornos diarios
        if len(df) > 1:
            df['daily_return'] = df['roi'].pct_change() * 100
        
        # Estadísticas de trades
        win_trades = len(self.trades[self.trades['action'] == 'SELL']) if not self.trades.empty else 0
        total_trades = len(self.trades)
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
        avg_return = df['roi'].mean() if not df.empty else 0
        
        return {
            'total_days': len(df),
            'best_day': df.loc[df['roi'].idxmax()].to_dict() if not df.empty else None,
            'worst_day': df.loc[df['roi'].idxmin()].to_dict() if not df.empty else None,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'current_roi': df['roi'].iloc[-1] if not df.empty else 0,
            'peak_equity': df['total_equity'].max() if not df.empty else 0,
            'max_drawdown': (df['total_equity'].min() - df['total_equity'].max()) / df['total_equity'].max() * 100 if not df.empty else 0
        }
    
    def get_portfolio_summary(self) -> dict:
        """Get current portfolio state as dict"""
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
            'recent_trades': self.trades.tail(10).to_dict('records') if not self.trades.empty else [],
            'last_update': self.last_update.isoformat()
        }
    
    def add_position(self, ticker: str, shares: float, price: float, reason: str = ""):
        """Add new position to portfolio"""
        cost = shares * price
        
        if cost > self.cash:
            return {"success": False, "message": f"Insufficient cash. Need ${cost:.2f}, have ${self.cash:.2f}"}
        
        # Update cash
        self.cash -= cost
        
        # Add to holdings
        new_holding = {
            'ticker': ticker,
            'shares': shares,
            'buy_price': price,
            'buy_date': datetime.now(),
            'current_price': price,
            'current_value': cost,
            'pnl': 0,
            'pnl_pct': 0
        }
        
        self.holdings = pd.concat([self.holdings, pd.DataFrame([new_holding])], ignore_index=True)
        
        # Log trade
        new_trade = {
            'date': datetime.now(),
            'ticker': ticker,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'cost': cost,
            'cash_after': self.cash,
            'reason': reason
        }
        
        self.trades = pd.concat([self.trades, pd.DataFrame([new_trade])], ignore_index=True)
        
        # Guardar trade en CSV
        trade_df = pd.DataFrame([new_trade])
        if self.trades_file.exists():
            trade_df.to_csv(self.trades_file, mode='a', header=False, index=False)
        else:
            trade_df.to_csv(self.trades_file, index=False)
        
        return {"success": True, "message": f"Bought {shares} shares of {ticker} at ${price:.2f}"}
    
    def update_prices_from_yfinance(self, tickers: list | None = None):
        """Update current prices from YFinance"""
        import yfinance as yf
        
        if tickers is None:
            if self.holdings.empty:
                return
            tickers = self.holdings['ticker'].unique().tolist()
        
        # Type guard para el checker
        assert tickers is not None, "tickers cannot be None at this point"
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
                
                if current_price:
                    # Update holdings for this ticker
                    mask = self.holdings['ticker'] == ticker
                    self.holdings.loc[mask, 'current_price'] = current_price
                    self.holdings.loc[mask, 'current_value'] = self.holdings.loc[mask, 'shares'] * current_price
                    self.holdings.loc[mask, 'pnl'] = (current_price - self.holdings.loc[mask, 'buy_price']) * self.holdings.loc[mask, 'shares']
                    self.holdings.loc[mask, 'pnl_pct'] = ((current_price - self.holdings.loc[mask, 'buy_price']) / self.holdings.loc[mask, 'buy_price']) * 100
            except Exception as e:
                print(f"Warning: Could not update price for {ticker}: {e}")
        
        self.last_update = datetime.now()


# Global portfolio instance with historical tracking
HISTORY_FILE = str(HISTORY_DIR / "portfolio_state.csv")
PORTFOLIO = PortfolioMemoryManager(initial_cash=100.0, history_file=HISTORY_FILE)


def create_market_researcher(use_openrouter: bool = True, use_fallback: bool = True):
    """Agent specialized in deep market research using Tongyi DeepResearch"""
    
    # Try OpenRouter first, fallback to DeepSeek if issues
    if use_openrouter and use_fallback:
        try:
            # Use DeepSeek as more reliable option for market research
            model = DeepSeek(id=MODELS["deepseek"])
            print("[INFO] Market Researcher usando DeepSeek (más confiable)")
        except Exception as e:
            print(f"[WARNING] Error con DeepSeek: {e}")
            model = OpenRouter(id=MODELS["deep_research"])
    elif use_openrouter:
        model = OpenRouter(id=MODELS["deep_research"])
    else:
        model = DeepSeek(id=MODELS["deepseek"])
    
    # Configurar herramientas
    # Lista de herramientas con tipado flexible
    tools: list = [
        YFinanceTools()  # Usa todas las herramientas disponibles
    ]
    
    # Agregar Serper si la API key está disponible y la librería instalada
    if SERPER_AVAILABLE and os.getenv("SERPER_API_KEY"):
        tools.append(SerperTools())
        print("[INFO] Serper Web Search habilitado para Market Researcher")
    elif not SERPER_AVAILABLE:
        print("[WARNING] Serper no disponible. Instala con: pip install agno[serper]")
    else:
        print("[WARNING] SERPER_API_KEY no encontrada en .env")
    
    return Agent(
        name="Market Researcher",
        role="Deep market analysis specialist with web search capabilities",
        model=model,
        tools=tools,
        instructions=[
            "Eres un especialista en investigación de mercado enfocado en acciones micro-cap",
            "Proporciona análisis completo de tendencias de mercado, noticias de empresas y dinámicas del sector",
            "USA TODAS las herramientas disponibles:",
            "  - YFinance: Precio actual, fundamentales, históricos, recomendaciones",
            "  - Serper (si disponible): Noticias recientes de la web, tendencias del sector, sentiment analysis",
            "ESTRATEGIA DE BÚSQUEDA WEB:",
            "  1. Busca noticias recientes sobre la empresa (menos de 7 días)",
            "  2. Busca análisis de expertos y opiniones de analistas",
            "  3. Busca tendencias del sector y competidores",
            "  4. Busca eventos corporativos (earnings, productos, regulaciones)",
            "Enfócate en identificar oportunidades micro-cap de alto potencial",
            "Considera factores tanto fundamentales como técnicos",
            "Sé exhaustivo pero conciso en tu análisis",
            "IMPORTANTE: Responde SIEMPRE en ESPAÑOL",
            "CRÍTICO: Siempre proporciona una respuesta completa con datos de todas las herramientas"
        ],
        markdown=True,
    )


def create_risk_analyst(use_openrouter: bool = True):
    """Agent specialized in risk analysis using Nemotron Nano for fast calculations"""
    
    model = (
        OpenRouter(id=MODELS["fast_calc"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    return Agent(
        name="Risk Analyst",
        role="Risk assessment and portfolio calculations",
        model=model,
        tools=[YFinanceTools(include_tools=[
            "get_key_financial_ratios",
            "get_technical_indicators",
            "get_historical_stock_prices"
        ])],
        instructions=[
            "IMPORTANTE: Responde SIEMPRE en ESPAÑOL",
            "Eres un especialista en gestión de riesgos",
            "USA las herramientas disponibles:",
            "  - get_key_financial_ratios: Beta, volatilidad, ratios de deuda",
            "  - get_technical_indicators: RSI, MACD, Bollinger Bands para volatilidad",
            "  - get_historical_stock_prices: Calcular drawdowns históricos",
            "Calcula métricas del portafolio: volatilidad, concentración, riesgo de drawdown",
            "Evalúa el tamaño de posiciones según la tolerancia al riesgo",
            "Recomienda niveles de stop-loss y límites de posición",
            "Enfócate en la preservación de capital",
            "Proporciona análisis numérico rápido y preciso con datos reales",
            f"Portafolio actual: Efectivo ${portfolio_summary['cash']:.2f}, Equity ${portfolio_summary['total_equity']:.2f}, ROI {portfolio_summary['roi']:.2f}%",
            "IMPORTANTE: Responde SIEMPRE en ESPAÑOL"
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
        tools=[YFinanceTools()],  # Usa todas las herramientas
        instructions=[
            "Eres el estratega principal de trading",
            "USA las herramientas para validar decisiones:",
            "  - get_technical_indicators: Confirma señales técnicas (RSI, MACD, etc.)",
            "  - get_income_statements: Valida salud financiera",
            "  - get_analyst_recommendations: Contrasta con consenso del mercado",
            "Sintetiza la investigación de mercado y el análisis de riesgos en decisiones accionables",
            "Usa razonamiento lógico para evaluar oportunidades de trading",
            "Considera: riesgo/recompensa, timing, condiciones de mercado, balance del portafolio",
            "Proporciona recomendaciones claras de COMPRAR/VENDER/MANTENER con razonamiento detallado",
            "Piensa paso a paso en escenarios complejos de trading",
            "Explica siempre tu proceso de toma de decisiones con datos reales",
            "IMPORTANTE: Responde SIEMPRE en ESPAÑOL"
        ],
        markdown=True,
    )


def create_portfolio_manager(use_openrouter: bool = True):
    """Agent for overall strategy using Qwen3 235B for advanced planning"""
    
    model = (
        OpenRouter(id=MODELS["advanced"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    historical_perf = PORTFOLIO.get_historical_performance()
    
    return Agent(
        name="Portfolio Manager",
        role="Senior portfolio manager synthesizing 6 expert opinions",
        model=model,
        instructions=[
            "Eres el Portfolio Manager senior - Autoridad de decisión final",
            "RESPONSABILIDAD: Sintetizar 6 opiniones expertas (3 Risk + 3 Strategy)",
            "",
            "ESTADO ACTUAL DEL PORTAFOLIO:",
            f"- Efectivo: ${portfolio_summary['cash']:.2f}",
            f"- Equity Total: ${portfolio_summary['total_equity']:.2f}",
            f"- P&L Total: ${portfolio_summary['total_pnl']:.2f}",
            f"- ROI: {portfolio_summary['roi']:.2f}%",
            f"- Posiciones: {portfolio_summary['num_positions']}",
            "",
            "HISTORIAL DE RENDIMIENTO:",
            f"- Total Días: {historical_perf['total_days']}",
            f"- ROI Actual: {historical_perf['current_roi']:.2f}%",
            f"- Peak Equity: ${historical_perf['peak_equity']:.2f}",
            f"- Max Drawdown: {historical_perf['max_drawdown']:.2f}%",
            f"- Total Trades: {historical_perf['total_trades']}",
            f"- Win Rate: {historical_perf['win_rate']:.1f}%",
            "",
            "OPINIONES QUE RECIBES (7 agentes antes de ti):",
            "1. Market Researcher: Datos de mercado + web",
            "2. Risk Analyst Conservador: Protección capital",
            "3. Risk Analyst Moderado: Balance riesgo/retorno",
            "4. Risk Analyst Agresivo: Oportunidades crecimiento",
            "5. Strategist Técnico: Price action",
            "6. Strategist Fundamental: Value investing",
            "7. Strategist Momentum: Trend following",
            "",
            "PROCESO DE SÍNTESIS:",
            "",
            "PASO 1 - ANALIZAR CONSENSO RISK (3 analistas):",
            "  ¿Cuántos dicen BAJO/MEDIO/ALTO/MUY ALTO?",
            "  Ponderación: Conservador 40%, Moderado 30%, Agresivo 30%",
            "  Si 2+ dicen ALTO RIESGO → Max 10% portfolio",
            "",
            "PASO 2 - EVALUAR ESTRATEGIAS (3 strategists):",
            "  ¿Cuántos BUY vs SELL vs HOLD?",
            "  ¿Técnico + Fundamental alineados?",
            "  Si divergen = señal precaución",
            "",
            "PASO 3 - DECISIÓN FINAL:",
            "  Considera:",
            "    - Mayoría de opiniones (no democracia ciega)",
            "    - Calidad de argumentos con datos",
            "    - Historial del portfolio",
            "    - Riesgo total actual",
            "",
            "REGLAS DE DECISIÓN:",
            "  - 2+ Risk Analysts ALTO → Max 10% portfolio",
            "  - 3 Strategists divididos → HOLD (esperar)",
            "  - Técnico+Fundamental OK, Momentum NO → Entry gradual",
            "  - Solo Momentum positivo → Posición pequeña",
            "",
            "DECISIÓN FINAL debe incluir:",
            "  - Acción: BUY/SELL/HOLD",
            "  - Consenso: X/3 Risk, Y/3 Strategy",
            "  - Si BUY: % portfolio (max 20%)",
            "  - Si SELL: % posición",
            "  - Justificación: Síntesis + criterio",
            "  - Stop Loss: El más conservador",
            "  - Take Profit: Promedio objetivos",
            "",
            "FILOSOFÍA: Múltiples opiniones = Mejor decisión",
            "Conservador por defecto - Riesgo solo con consenso sólido",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ MANDATORIO: Tu decisión final, razonamiento y todos los datos en ESPAÑOL",
            "⚠️ NO uses inglés en ninguna parte de tu respuesta"
        ],
        markdown=True,
    )


def create_daily_reporter(use_openrouter: bool = True):
    """NEW: Agent specialized in generating daily reports with transaction summaries"""
    
    model = (
        OpenRouter(id=MODELS["general"]) if use_openrouter
        else DeepSeek(id=MODELS["deepseek"])
    )
    
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    return Agent(
        name="Daily Reporter",
        role="Generate comprehensive daily reports and transaction summaries",
        model=model,
        instructions=[
            "Eres el especialista en reportes diarios",
            "Genera reportes diarios claros y profesionales que resuman:",
            "1. Rendimiento del portafolio (valor actual, P&L, ROI)",
            "2. Todas las transacciones ejecutadas hoy",
            "3. Cambios de posición y su justificación",
            "4. Eventos clave del mercado que afectan las posiciones",
            "5. Métricas de riesgo y salud del portafolio",
            "Formatea la salida como un reporte diario estructurado",
            "Usa tablas y viñetas para mayor claridad",
            "Destaca cambios importantes y alertas",
            f"Posiciones Actuales: {len(portfolio_summary['holdings'])} posiciones",
            f"Operaciones Recientes: {len(portfolio_summary['recent_trades'])} operaciones",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ MANDATORIO: TODO tu reporte debe estar en ESPAÑOL"
        ],
        markdown=True,
    )


# =============================================================================
# MÚLTIPLES RISK ANALYSTS - 3 Perspectivas Diferentes
# =============================================================================

def create_risk_analyst_conservative(use_openrouter: bool = True):
    """Risk Analyst #1: Perfil CONSERVADOR - Protección de capital"""
    model = DeepSeek(id=MODELS["deepseek"])  # Siempre DeepSeek (tiene tools)
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    return Agent(
        name="Risk Analyst Conservador",
        role="Conservative risk assessment - Capital preservation",
        model=model,
        tools=[YFinanceTools(include_tools=[
            "get_key_financial_ratios",
            "get_technical_indicators",
            "get_historical_stock_prices"
        ])],
        instructions=[
            "Eres un analista de riesgo CONSERVADOR - Prioridad: proteger capital",
            "PERFIL: Evitar pérdidas > Maximizar ganancias",
            "ENFOQUE: Empresas establecidas, baja deuda, flujo de caja positivo",
            "",
            "Criterios CONSERVADORES:",
            "  - Deuda/Capital < 50% (ideal < 30%)",
            "  - Current Ratio > 1.5",
            "  - Beta < 1.2 (baja volatilidad)",
            "  - RSI evitar > 70 (sobrecomprado)",
            "",
            "Clasifica riesgo: BAJO / MEDIO / ALTO / MUY ALTO",
            "Sé estricto: ante duda, mayor riesgo",
            f"Portfolio: ${portfolio_summary['total_equity']:.2f}, ROI {portfolio_summary['roi']:.2f}%",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ IMPORTANTE: TODO tu análisis, conclusiones y datos deben estar en ESPAÑOL"
        ],
        markdown=True,
    )

def create_risk_analyst_moderate(use_openrouter: bool = True):
    """Risk Analyst #2: Perfil MODERADO - Balance riesgo/retorno"""
    model = DeepSeek(id=MODELS["deepseek"])  # Siempre DeepSeek (tiene tools)
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    return Agent(
        name="Risk Analyst Moderado",
        role="Balanced risk assessment - Risk/reward optimization",
        model=model,
        tools=[YFinanceTools(include_tools=[
            "get_key_financial_ratios",
            "get_technical_indicators",
            "get_historical_stock_prices"
        ])],
        instructions=[
            "Eres un analista de riesgo MODERADO - Balance riesgo/retorno",
            "PERFIL: 50/50 protección y crecimiento",
            "ENFOQUE: Empresas en crecimiento con finanzas razonables",
            "",
            "Criterios BALANCEADOS:",
            "  - Deuda/Capital < 80%",
            "  - Current Ratio > 1.0",
            "  - Beta 0.8-1.5 (volatilidad normal)",
            "  - Crecimiento > 10% anual",
            "",
            "Clasifica riesgo: BAJO / MEDIO / ALTO",
            "Considera upside vs downside",
            f"Portfolio: ${portfolio_summary['total_equity']:.2f}, ROI {portfolio_summary['roi']:.2f}%",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ IMPORTANTE: TODO tu análisis, conclusiones y datos deben estar en ESPAÑOL"
        ],
        markdown=True,
    )

def create_risk_analyst_aggressive(use_openrouter: bool = True):
    """Risk Analyst #3: Perfil AGRESIVO - Alto crecimiento"""
    model = DeepSeek(id=MODELS["deepseek"])  # Siempre DeepSeek (tiene tools)
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    return Agent(
        name="Risk Analyst Agresivo",
        role="Growth-focused risk assessment - High return opportunities",
        model=model,
        tools=[YFinanceTools(include_tools=[
            "get_key_financial_ratios",
            "get_technical_indicators",
            "get_historical_stock_prices"
        ])],
        instructions=[
            "Eres un analista de riesgo AGRESIVO - Oportunidades de alto crecimiento",
            "PERFIL: Maximizar retorno > Minimizar riesgo",
            "ENFOQUE: Disruptivos, alto crecimiento, micro-cap con potencial",
            "",
            "Criterios AGRESIVOS:",
            "  - Deuda/Capital < 150% (toleras apalancamiento)",
            "  - Crecimiento > 30% anual",
            "  - Beta > 1.5 OK si hay catalizadores",
            "  - RSI > 50, MACD positivo",
            "",
            "Clasifica riesgo: ACEPTABLE / ALTO / EXTREMO",
            "Toleras riesgo si retorno lo justifica",
            f"Portfolio: ${portfolio_summary['total_equity']:.2f}, ROI {portfolio_summary['roi']:.2f}%",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ IMPORTANTE: TODO tu análisis, conclusiones y datos deben estar en ESPAÑOL"
        ],
        markdown=True,
    )


# =============================================================================
# MÚLTIPLES TRADING STRATEGISTS - 3 Enfoques Diferentes
# =============================================================================

def create_strategist_technical(use_openrouter: bool = True):
    """Trading Strategist #1: Enfoque TÉCNICO - Price action"""
    model = DeepSeek(id=MODELS["deepseek"])  # Siempre DeepSeek (tiene tools)
    
    return Agent(
        name="Strategist Técnico",
        role="Pure technical analysis - Charts and indicators",
        model=model,
        tools=[YFinanceTools()],  # Usa todas las herramientas
        instructions=[
            "Eres un estratega TÉCNICO puro - Solo charts, precio, volumen",
            "ENFOQUE: Price action, patrones, indicadores",
            "IGNORAS: Fundamentales (eso lo ven otros)",
            "",
            "DEBES analizar:",
            "  1. TENDENCIA: Alcista/Bajista/Lateral (MA)",
            "  2. MOMENTUM: RSI (>70 sobrecomprado, <30 sobrevendido)",
            "  3. MACD: Cruces, divergencias",
            "  4. VOLUMEN: Confirmación",
            "  5. SOPORTE/RESISTENCIA: Niveles clave",
            "",
            "Recomienda: BUY/SELL/HOLD con:",
            "  - Confianza técnica (1-10)",
            "  - Entry point ideal",
            "  - Stop loss técnico",
            "  - Take profit",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ IMPORTANTE: TODO tu análisis y conclusiones deben estar en ESPAÑOL"
        ],
        markdown=True,
    )

def create_strategist_fundamental(use_openrouter: bool = True):
    """Trading Strategist #2: Enfoque FUNDAMENTAL - Value investing"""
    model = DeepSeek(id=MODELS["deepseek"])  # Siempre DeepSeek (tiene tools)
    
    return Agent(
        name="Strategist Fundamental",
        role="Value investor - Fundamental analysis",
        model=model,
        tools=[YFinanceTools()],  # Usa todas las herramientas
        instructions=[
            "Eres un estratega FUNDAMENTAL - Value investing",
            "ENFOQUE: Análisis financiero profundo",
            "FILOSOFÍA: Warren Buffett / Benjamin Graham",
            "",
            "DEBES analizar:",
            "  1. VALUACIÓN: P/E, P/B, P/S vs industria",
            "  2. CRECIMIENTO: Revenue, earnings growth",
            "  3. RENTABILIDAD: ROE, ROA, márgenes",
            "  4. SALUD FINANCIERA: Deuda, liquidez, cash flow",
            "  5. CALIDAD: Moat, ventajas competitivas",
            "",
            "Recomienda: BUY/SELL/HOLD basado en:",
            "  - Valor intrínseco vs precio",
            "  - Margen de seguridad (%)",
            "  - Calidad del negocio (1-10)",
            "  - Catalizadores de valor",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ IMPORTANTE: TODO tu análisis y conclusiones deben estar en ESPAÑOL"
        ],
        markdown=True,
    )

def create_strategist_momentum(use_openrouter: bool = True):
    """Trading Strategist #3: Enfoque MOMENTUM - Trend following"""
    model = DeepSeek(id=MODELS["deepseek"])  # Siempre DeepSeek (tiene tools)
    
    return Agent(
        name="Strategist Momentum",
        role="Momentum and trend following specialist",
        model=model,
        tools=[YFinanceTools()],  # Usa todas las herramientas
        instructions=[
            "Eres un estratega de MOMENTUM - Sigues la tendencia",
            "ENFOQUE: 'The trend is your friend'",
            "FILOSOFÍA: Comprar fuerza, vender debilidad",
            "",
            "DEBES analizar:",
            "  1. TENDENCIA FUERTE: Múltiples timeframes",
            "  2. ACELERACIÓN: Incremento volumen y precio",
            "  3. CATALIZADORES: Noticias, earnings, eventos",
            "  4. SENTIMIENTO: Analistas upgrading",
            "  5. FUERZA RELATIVA: vs sector y mercado",
            "",
            "Recomienda: BUY/SELL/HOLD basado en:",
            "  - Fuerza momentum (1-10)",
            "  - Catalizadores próximos",
            "  - Timing del entry",
            "  - Trailing stop",
            "",
            "REGLA: Solo compras tendencias fuertes confirmadas",
            "",
            "⚠️ CRÍTICO: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL",
            "⚠️ IMPORTANTE: TODO tu análisis y conclusiones deben estar en ESPAÑOL"
        ],
        markdown=True,
    )


def create_trading_team(use_openrouter: bool = True):
    """Create coordinated team of 9 specialized agents with multiple perspectives
    
    STRUCTURE:
    1. Market Researcher (1) - Recopila datos
    2. Risk Analysts (3) - Múltiples perspectivas de riesgo
    3. Trading Strategists (3) - Múltiples estrategias
    4. Portfolio Manager (1) - Sintetiza todo
    5. Daily Reporter (1) - Reporte final
    """
    
    print("\n" + "="*70)
    print("CREANDO EQUIPO DE 9 AGENTES ESPECIALIZADOS")
    print("="*70)
    
    # 1. Market Researcher (con herramientas)
    print("\n[1/9] Market Researcher...")
    researcher = create_market_researcher(use_openrouter=False)  # DeepSeek
    
    # 2-4. Risk Analysts (3 perspectivas)
    print("[2/9] Risk Analyst Conservador...")
    risk_conservative = create_risk_analyst_conservative(use_openrouter)
    
    print("[3/9] Risk Analyst Moderado...")
    risk_moderate = create_risk_analyst_moderate(use_openrouter)
    
    print("[4/9] Risk Analyst Agresivo...")
    risk_aggressive = create_risk_analyst_aggressive(use_openrouter)
    
    # 5-7. Trading Strategists (3 enfoques)
    print("[5/9] Strategist Técnico...")
    strat_technical = create_strategist_technical(use_openrouter)
    
    print("[6/9] Strategist Fundamental...")
    strat_fundamental = create_strategist_fundamental(use_openrouter)
    
    print("[7/9] Strategist Momentum...")
    strat_momentum = create_strategist_momentum(use_openrouter)
    
    # 8. Portfolio Manager (sintetiza todo)
    print("[8/9] Portfolio Manager...")
    portfolio_mgr = create_portfolio_manager(use_openrouter)
    
    # 9. Daily Reporter
    print("[9/9] Daily Reporter...")
    reporter = create_daily_reporter(use_openrouter)
    
    print("="*70)
    print("EQUIPO COMPLETO - 9 AGENTES LISTOS")
    print("="*70 + "\n")
    
    # Create team with sequential workflow
    team = Team(
        name="Equipo de Análisis de Trading - 9 Expertos",
        members=[
            researcher,          # 1. Datos
            risk_conservative,   # 2. Riesgo conservador
            risk_moderate,       # 3. Riesgo moderado
            risk_aggressive,     # 4. Riesgo agresivo
            strat_technical,     # 5. Estrategia técnica
            strat_fundamental,   # 6. Estrategia fundamental
            strat_momentum,      # 7. Estrategia momentum
            portfolio_mgr,       # 8. Decisión final
            reporter             # 9. Reporte
        ],
        instructions=[
            "⚠️ CRÍTICO: TODO tu trabajo, coordinación y respuestas deben ser en ESPAÑOL",
            "⚠️ MANDATORIO: Comunícate con el usuario SOLO en ESPAÑOL",
            "",
            "FLUJO DE TRABAJO SECUENCIAL - 9 AGENTES:",
            "",
            "1. INVESTIGADOR DE MERCADO:",
            "   - Recopila datos completos (YFinance + Serper)",
            "",
            "2-4. ANALISTAS DE RIESGO (3 perspectivas):",
            "   - Conservador: Protección de capital",
            "   - Moderado: Balance riesgo/retorno",
            "   - Agresivo: Oportunidades de crecimiento",
            "   → El PM verá consenso entre los 3",
            "",
            "5-7. ESTRATEGAS DE TRADING (3 enfoques):",
            "   - Técnico: Price action puro",
            "   - Fundamental: Value investing",
            "   - Momentum: Trend following",
            "   → El PM verá convergencia de estrategias",
            "",
            "8. PORTFOLIO MANAGER:",
            "   - Sintetiza las 6 opiniones expertas",
            "   - Decide BUY/SELL/HOLD final",
            "   - Aplica gestión de riesgo",
            "",
            "9. DAILY REPORTER:",
            "   - Genera reporte profesional en español",
            "",
            "VENTAJA: Múltiples perspectivas = Mejor decisión",
            "",
            "⚠️ RECUERDA: Responde SIEMPRE en ESPAÑOL, nunca en inglés"
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
    
    # Update prices from YFinance
    print("[INFO] Actualizando precios desde YFinance...")
    PORTFOLIO.update_prices_from_yfinance()
    
    # Get current portfolio state
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    # Create team
    print("[INFO] Creando equipo de 5 agentes especializados...")
    print("  - Market Researcher: DeepSeek (confiable)")
    print(f"  - Risk Analyst: {'OpenRouter' if use_openrouter else 'DeepSeek'}")
    print(f"  - Trading Strategist: {'OpenRouter' if use_openrouter else 'DeepSeek'}")
    print(f"  - Portfolio Manager: {'OpenRouter' if use_openrouter else 'DeepSeek'}")
    print(f"  - Daily Reporter: {'OpenRouter' if use_openrouter else 'DeepSeek'}")
    team = create_trading_team(use_openrouter)
    
    # Analysis query
    query = f"""
Analyze {ticker} as a potential micro-cap investment opportunity.

Current Portfolio Status:
- Cash Available: ${portfolio_summary['cash']:.2f}
- Total Equity: ${portfolio_summary['total_equity']:.2f}
- Current ROI: {portfolio_summary['roi']:.2f}%
- Positions: {portfolio_summary['num_positions']}

Please provide:
1. Market Research: Current price, company info, recent news, sector trends
2. Risk Analysis: Volatility, position sizing recommendation, stop-loss levels
3. Trading Decision: BUY/SELL/HOLD with clear reasoning
4. Portfolio Impact: How this fits into overall portfolio strategy
5. Daily Report: Summary of analysis and recommended actions

Constraints:
- Maximum position size: $30 (30% of initial capital)
- Minimum cash reserve: $20 (20% of initial capital)
- Risk tolerance: Moderate (willing to accept volatility for growth)
"""
    
    # Run team analysis
    team.print_response(query, stream=True)
    
    # Guardar snapshot diario
    PORTFOLIO.save_daily_snapshot()
    
    print(f"\n{'='*70}")
    print(f"ANALYSIS COMPLETE: {ticker}")
    print(f"{'='*70}\n")


def run_daily_analysis(use_openrouter: bool = True, dry_run: bool = True):
    """Run daily portfolio analysis with full report"""
    
    print(f"\n{'='*70}")
    print(f"DAILY PORTFOLIO ANALYSIS - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Provider: {'OpenRouter (5 specialized models)' if use_openrouter else 'DeepSeek'}")
    print(f"{'='*70}\n")
    
    # Update all prices
    print("[INFO] Actualizando todos los precios desde YFinance...")
    PORTFOLIO.update_prices_from_yfinance()
    
    # Get current portfolio state
    portfolio_summary = PORTFOLIO.get_portfolio_summary()
    
    print(f"\n[RESUMEN DE PORTAFOLIO]")
    print(f"  Efectivo: ${portfolio_summary['cash']:.2f}")
    print(f"  Invertido: ${portfolio_summary['invested']:.2f}")
    print(f"  Equity Total: ${portfolio_summary['total_equity']:.2f}")
    print(f"  P&L Total: ${portfolio_summary['total_pnl']:.2f}")
    print(f"  ROI: {portfolio_summary['roi']:.2f}%")
    print(f"  Posiciones: {portfolio_summary['num_positions']}\n")
    
    # Create team
    print("[INFO] Creando equipo de análisis (5 agentes)...")
    team = create_trading_team(use_openrouter)
    
    # Daily analysis query
    query = f"""
Conduct a comprehensive daily portfolio review and generate a detailed daily report.

CURRENT PORTFOLIO STATUS:
- Cash Balance: ${portfolio_summary['cash']:.2f}
- Invested Capital: ${portfolio_summary['invested']:.2f}
- Total Equity: ${portfolio_summary['total_equity']:.2f}
- Total P&L: ${portfolio_summary['total_pnl']:.2f}
- ROI: {portfolio_summary['roi']:.2f}%
- Number of Positions: {portfolio_summary['num_positions']}

Holdings:
{json.dumps(portfolio_summary['holdings'], indent=2)}

Recent Trades:
{json.dumps(portfolio_summary['recent_trades'], indent=2)}

Please provide:

1. MARKET RESEARCH:
   - Identify 2-3 high-potential micro-cap opportunities
   - Analyze current market trends affecting micro-caps
   - Review news on existing holdings

2. RISK ASSESSMENT:
   - Calculate portfolio volatility and drawdown risk
   - Review position concentration
   - Recommend position size adjustments if needed

3. TRADING RECOMMENDATIONS:
   - Provide specific BUY/SELL/HOLD actions with reasoning
   - Include entry/exit prices and position sizes
   - Explain risk/reward for each recommendation

4. STRATEGIC PLAN:
   - 30-day outlook and strategy
   - Portfolio rebalancing recommendations
   - Key catalysts to watch

5. DAILY REPORT:
   - Executive summary of portfolio performance
   - Transaction summary (if any trades executed)
   - Key highlights and alerts
   - Action items for tomorrow

Format the final output as a professional daily trading report with clear sections.
"""
    
    # Run team analysis
    team.print_response(query, stream=True)
    
    # Guardar snapshot diario
    PORTFOLIO.save_daily_snapshot()
    
    print(f"\n{'='*70}")
    print(f"DAILY ANALYSIS COMPLETE")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Multi-Agent Trading System with In-Memory Portfolio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze specific stock with OpenRouter models
  python advanced_trading_team.py --ticker AAPL --provider openrouter
  
  # Daily analysis with DeepSeek (stable fallback)
  python advanced_trading_team.py --daily --provider deepseek
  
  # Initialize portfolio with some positions
  python advanced_trading_team.py --init-demo

Models Used (OpenRouter):
  - Deep Research: Tongyi DeepResearch 30B (market analysis)
  - Reasoning: DeepSeek R1T2 Chimera (trade decisions)
  - Fast Calc: Nemotron Nano 9B (risk calculations)
  - General: GLM 4.5 Air (general analysis)
  - Advanced: Qwen3 235B (strategy planning)
  - Reporter: GLM 4.5 Air (daily reports)
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
        help="Run daily portfolio analysis with full report"
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
    
    parser.add_argument(
        "--init-demo",
        action="store_true",
        help="Initialize portfolio with demo positions"
    )
    
    parser.add_argument(
        "--show-history",
        action="store_true",
        help="Show historical performance and statistics"
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
    
    # Initialize demo portfolio if requested
    if args.init_demo:
        print("\n[INFO] Initializing demo portfolio...")
        PORTFOLIO.add_position("AAPL", 0.2, 175.0, "Initial demo position")
        PORTFOLIO.add_position("TSLA", 0.3, 250.0, "Initial demo position")
        PORTFOLIO.save_daily_snapshot()
        print("[SUCCESS] Demo portfolio initialized")
        print(f"  Cash: ${PORTFOLIO.cash:.2f}")
        print(f"  Holdings: {len(PORTFOLIO.holdings)} positions")
        return
    
    # Show history if requested
    if args.show_history:
        print("\n" + "="*70)
        print("HISTORIAL DE RENDIMIENTO DEL PORTAFOLIO")
        print("="*70 + "\n")
        
        hist = PORTFOLIO.get_historical_performance()
        summary = PORTFOLIO.get_portfolio_summary()
        
        print(f"[ESTADO ACTUAL]")
        print(f"  Equity Total: ${summary['total_equity']:.2f}")
        print(f"  ROI Actual: {summary['roi']:.2f}%")
        print(f"  Efectivo: ${summary['cash']:.2f}")
        print(f"  Posiciones: {summary['num_positions']}\n")
        
        print(f"[ESTADÍSTICAS HISTÓRICAS]")
        print(f"  Días Operando: {hist['total_days']}")
        print(f"  Equity Máximo: ${hist['peak_equity']:.2f}")
        print(f"  Máximo Drawdown: {hist['max_drawdown']:.2f}%")
        print(f"  Total Operaciones: {hist['total_trades']}\n")
        
        if hist['best_day']:
            print(f"[MEJOR DÍA]")
            print(f"  Fecha: {hist['best_day']['date']}")
            print(f"  ROI: {hist['best_day']['roi']:.2f}%\n")
        
        if hist['worst_day']:
            print(f"[PEOR DÍA]")
            print(f"  Fecha: {hist['worst_day']['date']}")
            print(f"  ROI: {hist['worst_day']['roi']:.2f}%\n")
        
        # Mostrar últimas 10 operaciones
        if not PORTFOLIO.trades.empty:
            print(f"[ÚTIMAS 10 OPERACIONES]")
            print(PORTFOLIO.trades.tail(10).to_string(index=False))
        
        print("\n" + "="*70 + "\n")
        return
    
    # Run analysis
    if args.ticker:
        analyze_stock(args.ticker, use_openrouter, args.dry_run)
    elif args.daily:
        run_daily_analysis(use_openrouter, args.dry_run)
    else:
        print("\n[INFO] Please specify --ticker, --daily, or --init-demo")
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Sistema de Backtesting HORARIO/5MIN - VERSION 3.0 HÍBRIDA

MEJORAS V3.0 (19-Oct-2025):
- ✅ Híbrido: Velocidad V2.1 + EMA48 del Consenso
- ✅ Structured outputs con Pydantic (type safety)
- ✅ EMA48 con proyección de 2 periodos futuros
- ✅ Suite completa de indicadores técnicos
- ✅ Stop Loss/Take Profit automáticos (-3%/+5%)
- ✅ Position sizing dinámico basado en ATR
- ✅ Soporte para datos de 5 minutos y 1 hora
- ✅ Un solo agente optimizado (no equipo completo)

Versión: 3.0.0
Fecha: 2025-10-19
"""

import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Literal
import time

from agno.models.openrouter import OpenRouter
from agno.models.deepseek import DeepSeek
from agno.agent import Agent
from pydantic import BaseModel, Field

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════
# PYDANTIC MODEL - STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════════

class TradingDecision(BaseModel):
    """
    Decisión de trading estructurada y validada - V3.0 Hybrid

    Combina lo mejor de ambos mundos:
    - Type safety del V2.1
    - Lógica de consenso con EMA48
    """
    action: Literal["BUY", "SELL", "HOLD"] = Field(
        description="Acción a tomar: BUY (comprar), SELL (vender) o HOLD (mantener)"
    )
    amount: float = Field(
        ge=0,
        description="Monto a operar: USD para BUY, porcentaje (25-100) para SELL, 0 para HOLD."
    )
    reason: str = Field(
        max_length=300,
        description="Justificación técnica concisa (máximo 1-2 líneas)"
    )
    strategy: str = Field(
        default="",
        max_length=100,
        description="Estrategia utilizada (trend_following, momentum, mean_reversion, etc.)"
    )
    confidence: float = Field(
        ge=0, le=1,
        default=0.5,
        description="Nivel de confianza en la decisión (0-1)"
    )

# ═══════════════════════════════════════════════════════════════════════
# TRADING INSTRUCTIONS - V3.0 HYBRID
# ═══════════════════════════════════════════════════════════════════════

TRADING_INSTRUCTIONS_V3 = [
    "Eres un trader algorítmico HÍBRIDO especializado en análisis técnico completo.",
    "Tu objetivo es MAXIMIZAR RETORNOS aprovechando oportunidades de corto plazo con visión de largo plazo.",
    "Tienes autonomía total para proponer estrategias creativas, incluyendo compras/ventas parciales y combinaciones de señales.",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "🎯 ESTRATEGIA HÍBRIDA - V3.0:",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "✅ ANÁLISIS DE LARGO PLAZO (EMA48):",
    "- EMA48 representa la tendencia general del mercado",
    "- Si precio > EMA48: Tendencia alcista general",
    "- Si precio < EMA48: Tendencia bajista general",
    "- Considera las proyecciones EMA48+1/+2 para anticipar movimientos",
    "",
    "✅ ANÁLISIS DE CORTO PLAZO (Indicadores Técnicos):",
    "- EMA12/26 para momentum inmediato",
    "- MACD para señales de entrada/salida",
    "- Bollinger Bands para niveles de soporte/resistencia",
    "- ATR para volatilidad y position sizing",
    "",
    "✅ COMPRAR (BUY) - Considera si cumple AL MENOS 2 DE ESTAS:",
    "1. Precio > EMA48 (tendencia alcista general)",
    "2. EMA12 > EMA26 (momentum positivo)",
    "3. MACD > MACD Signal (convergencia positiva)",
    "4. Precio cerca de Bollinger Inferior (oportunidad de rebote)",
    "5. RSI < 70 (no sobrecomprado)",
    "6. Cambio positivo en últimas horas",
    "",
    "💡 OPORTUNIDADES ESPECIALES DE COMPRA:",
    "- SOBREVENTA: Precio toca Bollinger Inferior + EMA48 alcista",
    "- BREAKOUT: Precio rompe EMA12 al alza + EMA48 de soporte",
    "- MOMENTUM: MACD cruza al alza + histograma creciendo",
    "",
    "❌ VENDER (SELL) - Considera si cumple AL MENOS 1 DE ESTAS:",
    "1. Ganancia no realizada > 3% (asegurar beneficios)",
    "2. MACD cruza a la baja (pérdida de momentum)",
    "3. Precio toca Bollinger Superior (sobrecompra)",
    "4. RSI > 75 (sobrecompra extrema)",
    "5. Precio rompe EMA48 a la baja (cambio de tendencia)",
    "",
    "⚪ MANTENER (HOLD) - SOLO si:",
    "- NO tienes posición Y señales contradictorias",
    "- Tienes posición con ganancia < 2% y momentum aún positivo",
    "- Esperando confirmación de cambio de tendencia EMA48",
    "",
    "🎲 FILOSOFÍA HÍBRIDA:",
    "- ACTÚA RÁPIDO: El mercado premia la velocidad",
    "- CONSIDERA TENDENCIA: EMA48 como brújula general",
    "- APROVECHA VOLATILIDAD: La volatilidad = oportunidad",
    "- GESTIONA RIESGO: Stop Loss automático protege capital",
    "- REALIZA BENEFICIOS: Mejor 3% seguro que 5% incierto",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "🧠 APRENDIZAJE DE DECISIONES PREVIAS:",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "Analiza las últimas 3 decisiones tomadas para mejorar tu estrategia:",
    "",
    "✅ PATRONES EXITOSOS A REPETIR:",
    "- Si una BUY resultó en ganancia >3%: Busca señales similares",
    "- Si una SELL evitó pérdida >2%: Considera salidas anticipadas",
    "- Si HOLD evitó operación perdedora: Sé más conservador en dudas",
    "",
    "❌ ERRORES A EVITAR:",
    "- Si BUY resultó en pérdida >2%: Evita señales similares",
    "- Si SELL prematura dejó ganancias: Espera confirmación más fuerte",
    "- Si HOLD perdió oportunidad: Sé más agresivo en señales claras",
    "",
    "📈 ADAPTACIÓN DINÁMICA:",
    "- Si últimas decisiones fueron mayormente exitosas: Aumenta confianza",
    "- Si últimas decisiones tuvieron pérdidas: Reduce tamaño de posiciones",
    "- Si mercado cambió dirección: Ajusta estrategia a nueva tendencia",
    "",
    "🎯 DECISIONES RECIENTES (últimas 3):",
    "[El sistema te proporcionará automáticamente el historial de decisiones previas]",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "⚠️ RESTRICCIONES DURAS:",
    "- NO operar sin indicadores válidos",
    "- NO comprar con RSI > 80",
    "- Respetar límites de MONTO especificados",
    "- Considerar siempre la tendencia EMA48",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "📋 FORMATO DE RESPUESTA:",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "Debes responder con un JSON estructurado con estos campos:",
    "- action: 'BUY', 'SELL' o 'HOLD'",
    "- amount: número (USD para BUY, porcentaje para SELL, 0 para HOLD)",
    "- reason: texto breve (máximo 1-2 líneas)",
    "- strategy: texto corto (ej: 'trend_following', 'momentum', 'mean_reversion')",
    "- confidence: número entre 0 y 1",
    "",
    "⚠️ PROTECCIÓN AUTOMÁTICA (no te preocupes por esto):",
    "- Stop Loss: -3% (se ejecuta automáticamente)",
    "- Take Profit: +5% (se ejecuta automáticamente)",
]

class TradingSimulatorV3:
    """Simulador de trading con gestión de riesgo automática - V3.0"""

    def __init__(self, initial_capital: float = 10000.0, transaction_cost: float = 0.001,
                 stop_loss_pct: float = 0.03, take_profit_pct: float = 0.05):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.transaction_cost = transaction_cost

        # Gestión de riesgo automática
        self.stop_loss_pct = stop_loss_pct  # 3% stop loss
        self.take_profit_pct = take_profit_pct  # 5% take profit

        self.portfolio = {}
        self.history = []
        self.equity_curve = []
        self.decisions_log = []
        self.auto_closes = []  # Registro de cierres automáticos

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calcular valor total del portfolio"""
        holdings_value = sum(
            self.portfolio[ticker]['shares'] * current_prices.get(ticker, 0)
            for ticker in self.portfolio
        )
        return self.cash + holdings_value

    def check_risk_limits(self, current_prices: Dict[str, float], timestamp: str) -> List[Dict]:
        """Verificar stop loss y take profit automáticamente"""
        auto_sales = []

        for ticker in list(self.portfolio.keys()):
            if ticker not in current_prices:
                continue

            position = self.portfolio[ticker]
            current_price = current_prices[ticker]
            avg_price = position['avg_price']
            pnl_pct = ((current_price - avg_price) / avg_price)

            # Stop Loss: Pérdida > 3%
            if pnl_pct <= -self.stop_loss_pct:
                result = self.execute_sell(
                    ticker=ticker,
                    shares=position['shares'],
                    price=current_price,
                    date=timestamp,
                    reason=f"🛑 STOP LOSS AUTO: Pérdida {pnl_pct*100:.2f}%"
                )
                if result['success']:
                    auto_sales.append({
                        'type': 'STOP_LOSS',
                        'ticker': ticker,
                        'pnl_pct': pnl_pct * 100,
                        'trade': result['trade']
                    })

            # Take Profit: Ganancia > 5%
            elif pnl_pct >= self.take_profit_pct:
                result = self.execute_sell(
                    ticker=ticker,
                    shares=position['shares'],
                    price=current_price,
                    date=timestamp,
                    reason=f"🎯 TAKE PROFIT AUTO: Ganancia {pnl_pct*100:.2f}%"
                )
                if result['success']:
                    auto_sales.append({
                        'type': 'TAKE_PROFIT',
                        'ticker': ticker,
                        'pnl_pct': pnl_pct * 100,
                        'trade': result['trade']
                    })

        return auto_sales

    def execute_buy(self, ticker: str, shares: float, price: float, date: str, reason: str = "") -> Dict:
        """Ejecutar compra"""
        if shares <= 0:
            return {"success": False, "message": "Shares debe ser > 0"}

        cost = shares * price
        fee = cost * self.transaction_cost
        total_cost = cost + fee

        if total_cost > self.cash:
            return {"success": False, "message": f"Efectivo insuficiente: ${self.cash:.2f} < ${total_cost:.2f}"}

        self.cash -= total_cost

        if ticker in self.portfolio:
            old_shares = self.portfolio[ticker]['shares']
            old_avg = self.portfolio[ticker]['avg_price']
            new_shares = old_shares + shares
            new_avg = ((old_shares * old_avg) + (shares * price)) / new_shares
            self.portfolio[ticker]['shares'] = new_shares
            self.portfolio[ticker]['avg_price'] = new_avg
        else:
            self.portfolio[ticker] = {
                'shares': shares,
                'avg_price': price
            }

        trade = {
            'date': date,
            'action': 'BUY',
            'ticker': ticker,
            'shares': shares,
            'price': price,
            'cost': cost,
            'fee': fee,
            'total': total_cost,
            'reason': reason
        }
        self.history.append(trade)

        return {"success": True, "message": "Compra exitosa", "trade": trade}

    def execute_sell(self, ticker: str, shares: float, price: float, date: str, reason: str = "") -> Dict:
        """Ejecutar venta"""
        if ticker not in self.portfolio:
            return {"success": False, "message": f"No tienes posición en {ticker}"}

        position = self.portfolio[ticker]
        if shares > position['shares']:
            shares = position['shares']

        revenue = shares * price
        fee = revenue * self.transaction_cost
        net_revenue = revenue - fee

        avg_price = position['avg_price']
        profit = (price - avg_price) * shares
        profit_pct = ((price - avg_price) / avg_price) * 100

        self.cash += net_revenue
        position['shares'] -= shares

        if position['shares'] < 0.00000001:
            del self.portfolio[ticker]

        trade = {
            'date': date,
            'action': 'SELL',
            'ticker': ticker,
            'shares': shares,
            'price': price,
            'revenue': revenue,
            'fee': fee,
            'net_revenue': net_revenue,
            'avg_price': avg_price,
            'profit': profit,
            'profit_pct': profit_pct,
            'reason': reason
        }
        self.history.append(trade)

        return {"success": True, "message": "Venta exitosa", "trade": trade}

class BacktestEngineV3:
    """Motor de backtesting híbrido V3.0 - Un agente, máxima eficiencia"""

    def __init__(self, simulator: TradingSimulatorV3, model_id: str = "deepseek-chat"):
        self.simulator = simulator
        self.model_id = model_id
        
        # Historial de decisiones para aprendizaje contextual
        self.decision_history = []  # Lista de las últimas decisiones tomadas
        
        # Crear agente con instructions híbridas y output_schema
        if model_id == "deepseek-chat":
            model = DeepSeek(id=model_id)
        else:
            model = OpenRouter(id=model_id)

        self.agent = Agent(
            name="Hybrid Trader V3.0",
            model=model,
            instructions=TRADING_INSTRUCTIONS_V3,
            output_schema=TradingDecision,
            markdown=True
        )
    
    def add_decision_to_history(self, decision: Dict, execution_result: Dict, timestamp: datetime):
        """
        Agregar decisión al historial y mantener solo las últimas 3
        
        Args:
            decision: Diccionario con la decisión tomada
            execution_result: Resultado de la ejecución
            timestamp: Timestamp de la decisión (datetime object)
        """
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M')
        history_entry = {
            'timestamp': timestamp_str,
            'decision': decision,
            'execution': execution_result,
            'outcome': self._analyze_decision_outcome(decision, execution_result)
        }
        
        self.decision_history.append(history_entry)
        
        # Mantener solo las últimas 3 decisiones
        if len(self.decision_history) > 3:
            self.decision_history = self.decision_history[-3:]
    
    def _analyze_decision_outcome(self, decision: Dict, execution_result: Dict) -> str:
        """
        Analizar el resultado de una decisión para aprendizaje
        
        Returns:
            String describiendo si la decisión fue acertada o no
        """
        action = decision.get('action', 'HOLD')
        success = execution_result.get('success', False)
        
        if action == 'HOLD':
            return "HOLD - Sin riesgo, sin ganancia"
        elif action == 'BUY':
            if success:
                return "BUY - Ejecución exitosa, esperando resultado"
            else:
                return "BUY - Falló ejecución (fondos insuficientes)"
        elif action == 'SELL':
            if success:
                trade = execution_result.get('trade', {})
                profit_pct = trade.get('profit_pct', 0)
                if profit_pct > 0:
                    return f"SELL - Ganancia de {profit_pct:.2f}%"
                else:
                    return f"SELL - Pérdida de {profit_pct:.2f}%"
            else:
                return "SELL - Falló ejecución (sin posición)"
        
        return "Resultado desconocido"

    def safe_get_column(self, df, row, col_name, default=0.0):
        """Extraer columna OHLCV de forma robusta"""
        if col_name in df.columns:
            return float(row[col_name])
        matching = [col for col in df.columns if col_name in str(col)]
        if matching:
            return float(row[matching[0]])
        return float(default)

    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calcular indicadores técnicos avanzados - V3.0 Hybrid"""
        if len(df) < 2:
            return self._empty_indicators()

        try:
            close = df.apply(lambda row: self.safe_get_column(df, row, 'Close'), axis=1)
            high = df.apply(lambda row: self.safe_get_column(df, row, 'High'), axis=1)
            low = df.apply(lambda row: self.safe_get_column(df, row, 'Low'), axis=1)

            # EMA 12, 26 y 48 (NUEVO: EMA48 del consenso)
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            ema48 = close.ewm(span=48, adjust=False).mean()  # NUEVO

            # MACD
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_histogram = macd_line - signal_line

            # Bollinger Bands
            sma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            bb_upper = sma20 + (std20 * 2)
            bb_lower = sma20 - (std20 * 2)

            # ATR
            high_low = high - low
            high_close = abs(high - close.shift())
            low_close = abs(low - close.shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()

            # RSI (opcional)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return {
                'ema12': float(ema12.iloc[-1]),
                'ema26': float(ema26.iloc[-1]),
                'ema48': float(ema48.iloc[-1]),  # NUEVO
                'ema_cross': "⬆️ ALCISTA" if ema12.iloc[-1] > ema26.iloc[-1] else "⬇️ BAJISTA",
                'ema48_trend': "⬆️ ALCISTA" if close.iloc[-1] > ema48.iloc[-1] else "⬇️ BAJISTA",  # NUEVO
                'macd': float(macd_line.iloc[-1]),
                'macd_signal': float(signal_line.iloc[-1]),
                'macd_histogram': float(macd_histogram.iloc[-1]),
                'bb_upper': float(bb_upper.iloc[-1]),
                'bb_middle': float(sma20.iloc[-1]),
                'bb_lower': float(bb_lower.iloc[-1]),
                'bb_position': "⬆️ SOBRE BANDA SUPERIOR" if close.iloc[-1] > bb_upper.iloc[-1] else ("⬇️ BAJO BANDA INFERIOR" if close.iloc[-1] < bb_lower.iloc[-1] else "↔️ DENTRO DE BANDAS"),
                'atr': float(atr.iloc[-1]),
                'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
            }
        except Exception as e:
            print(f"⚠️ Error calculando indicadores: {e}")
            return self._empty_indicators()

    def _empty_indicators(self) -> Dict:
        """Indicadores vacíos por defecto"""
        return {
            'ema12': 0, 'ema26': 0, 'ema48': 0, 'ema_cross': 'N/A', 'ema48_trend': 'N/A',
            'macd': 0, 'macd_signal': 0, 'macd_histogram': 0,
            'bb_upper': 0, 'bb_middle': 0, 'bb_lower': 0, 'bb_position': 'N/A',
            'atr': 0, 'rsi': 50
        }

    def calculate_ema48_projections(self, df: pd.DataFrame) -> Tuple[float, float, float]:
        """Calcular EMA48 y proyecciones de 2 periodos - NUEVO en V3.0"""
        if len(df) < 48:
            return 0.0, 0.0, 0.0

        try:
            close = df.apply(lambda row: self.safe_get_column(df, row, 'Close'), axis=1)
            ema48_series = close.ewm(span=48, adjust=False).mean()

            ema48 = float(ema48_series.iloc[-1])

            # Proyección simple usando pendiente de últimos 2 periodos
            if len(ema48_series) >= 3:
                delta1 = ema48_series.iloc[-1] - ema48_series.iloc[-2]
                delta2 = ema48_series.iloc[-2] - ema48_series.iloc[-3]
                avg_delta = (delta1 + delta2) / 2
                ema48_proj_1 = ema48 + avg_delta
                ema48_proj_2 = ema48_proj_1 + avg_delta
            else:
                ema48_proj_1 = ema48
                ema48_proj_2 = ema48

            return ema48, ema48_proj_1, ema48_proj_2
        except Exception as e:
            print(f"⚠️ Error calculando EMA48: {e}")
            return 0.0, 0.0, 0.0

    def get_llm_decision(self, ticker: str, current_prices: Dict[str, float],
                        timestamp: datetime, historical_data: pd.DataFrame,
                        market_context: str) -> Dict:
        """
        Obtener decisión del LLM usando estructura Agno correcta - V3.0 Hybrid

        NUEVO: Incluye EMA48 con proyección del motor consenso
        """

        # Formatear timestamp para usar consistentemente
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M')

        # Calcular indicadores técnicos completos
        indicators = self.calculate_technical_indicators(historical_data)

        # Calcular EMA48 y proyecciones (NUEVO)
        ema48, ema48_proj_1, ema48_proj_2 = self.calculate_ema48_projections(historical_data)

        current_price = current_prices.get(ticker, 0)
        portfolio_value = self.simulator.get_portfolio_value(current_prices)

        # Información de posición actual
        position_info = ""
        if ticker in self.simulator.portfolio:
            pos = self.simulator.portfolio[ticker]
            unrealized_pnl = ((current_price - pos['avg_price']) / pos['avg_price']) * 100
            position_info = f"""
- Posición actual: {pos['shares']:.8f} BTC @ ${pos['avg_price']:.2f}
- Valor posición: ${pos['shares'] * current_price:.2f}
- P&L no realizado: {unrealized_pnl:+.2f}%
"""
        else:
            position_info = "- Sin posición abierta en BTC"

        # Calcular cambios de precio
        close_hist = historical_data.apply(lambda row: self.safe_get_column(historical_data, row, 'Close'), axis=1)
        if len(close_hist) >= 2:
            price_change_1h = ((close_hist.iloc[-1] - close_hist.iloc[-2]) / close_hist.iloc[-2]) * 100
        else:
            price_change_1h = 0

        if len(close_hist) >= 5:
            price_change_4h = ((close_hist.iloc[-1] - close_hist.iloc[-5]) / close_hist.iloc[-5]) * 100
        else:
            price_change_4h = 0

        # Volume ratio
        volume_hist = historical_data.apply(lambda row: self.safe_get_column(historical_data, row, 'Volume'), axis=1)
        if len(volume_hist) >= 10:
            avg_volume = volume_hist.rolling(10).mean().iloc[-1]
            current_volume = volume_hist.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        else:
            volume_ratio = 1.0

        # Position sizing dinámico basado en ATR
        atr = indicators['atr']
        if atr > 5000:
            max_risk = 0.20  # Alta volatilidad
        elif atr > 3000:
            max_risk = 0.30
        else:
            max_risk = 0.40  # Baja volatilidad
        max_investment = self.simulator.cash * max_risk

        # Determinar señales
        macd_signal = "⬆️ ALCISTA" if indicators['macd'] > indicators['macd_signal'] else "⬇️ BAJISTA"

        # ═══════════════════════════════════════════════════════════════════
        # CONTEXTO DINÁMICO - V3.0 HYBRID (EMA48 + Suite Completa)
        # ═══════════════════════════════════════════════════════════════════

        # Incluir historial de decisiones recientes para aprendizaje contextual
        decision_history_context = ""
        if self.decision_history:
            decision_history_context = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🧠 HISTORIAL DE DECISIONES RECIENTES (APRENDIZAJE):\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for i, entry in enumerate(self.decision_history[-3:], 1):  # Últimas 3 decisiones
                decision = entry['decision']
                outcome = entry['outcome']
                timestamp = entry['timestamp']
                decision_history_context += f"\n{i}. [{timestamp}] {decision.get('action', 'N/A')} - {outcome}"
                decision_history_context += f"\n   Estrategia: {decision.get('strategy', 'N/A')} | Confianza: {decision.get('confidence', 0):.2f}"
                decision_history_context += f"\n   Razón: {decision.get('reason', 'N/A')[:50]}..."
        else:
            decision_history_context = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🧠 HISTORIAL DE DECISIONES: (Primera decisión - sin historial previo)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        market_data_context = f"""
Analiza esta situación de trading y toma una decisión híbrida:

{market_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 INDICADORES TÉCNICOS COMPLETOS - V3.0 HYBRID:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 ANÁLISIS DE LARGO PLAZO (EMA48):
• EMA 48: ${ema48:.2f}
• EMA 48 Proy+1: ${ema48_proj_1:.2f}
• EMA 48 Proy+2: ${ema48_proj_2:.2f}
• Tendencia EMA48: {indicators['ema48_trend']}

📈 ANÁLISIS DE CORTO PLAZO:
• EMA 12: ${indicators['ema12']:.2f}
• EMA 26: ${indicators['ema26']:.2f}
• Cruce EMA: {indicators['ema_cross']}

• MACD: {indicators['macd']:.2f}
• MACD Signal: {indicators['macd_signal']:.2f}
• Histograma: {indicators['macd_histogram']:.2f} {macd_signal}

• Bollinger Superior: ${indicators['bb_upper']:.2f}
• Bollinger Medio: ${indicators['bb_middle']:.2f}
• Bollinger Inferior: ${indicators['bb_lower']:.2f}
• Estado: {indicators['bb_position']}

• ATR (Volatilidad): ${indicators['atr']:.2f}
• RSI: {indicators['rsi']:.1f}
• Cambio precio 1h: {price_change_1h:+.2f}%
• Cambio precio 4h: {price_change_4h:+.2f}%
• Volumen Ratio: {volume_ratio:.2f}x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 TU PORTFOLIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Capital total: ${portfolio_value:.2f}
- Efectivo disponible: ${self.simulator.cash:.2f}
- Máximo a invertir por operación: ${max_investment:.2f} ({max_risk*100:.0f}% del efectivo)
{position_info}

{decision_history_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ESTRATEGIA HÍBRIDA V3.0:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Considera la EMA48 como tu brújula de largo plazo
• Combina con indicadores de corto plazo para timing perfecto
• El momentum debe alinearse con la tendencia general
• Gestiona riesgo automáticamente con SL/TP
• APRENDE de tus últimas decisiones para mejorar el rendimiento

RESTRICCIONES DE MONTO:
- BUY: Entre $1000 y ${max_investment:.0f}
- SELL: Entre 25% y 100% de tu posición
- HOLD: amount = 0
"""

        try:
            # ═══════════════════════════════════════════════════════════════
            # EJECUTAR AGENTE - V3.0 HYBRID
            # ═══════════════════════════════════════════════════════════════

            response = self.agent.run(market_data_context)

            # response.content idealmente es un TradingDecision (Pydantic)
            decision = None
            raw = getattr(response, 'content', None)

            # 1) Si ya es TradingDecision lo usamos
            if isinstance(raw, TradingDecision):
                decision = raw
            else:
                # 2) Si es dict-like (JSON serializable) intentar construir TradingDecision
                try:
                    if isinstance(raw, dict):
                        decision = TradingDecision(**raw)
                    elif isinstance(raw, str):
                        # Intentar parsear JSON limpio
                        try:
                            parsed = json.loads(raw)
                            if isinstance(parsed, dict):
                                decision = TradingDecision(**parsed)
                        except Exception:
                            # Heurística simple: detectar palabras clave
                            low = raw.lower()
                            if 'buy' in low:
                                decision = TradingDecision(action='BUY', amount=0, reason=raw[:200], strategy='heuristic', confidence=0.5)
                            elif 'sell' in low:
                                decision = TradingDecision(action='SELL', amount=100, reason=raw[:200], strategy='heuristic', confidence=0.5)
                            else:
                                decision = TradingDecision(action='HOLD', amount=0, reason='Fallback: respuesta no parseable', strategy='heuristic', confidence=0.0)
                except Exception as e_inner:
                    print(f"⚠️ Error parseando respuesta bruta del agente: {e_inner}")
                    decision = TradingDecision(action='HOLD', amount=0, reason=f'Parse error: {e_inner}', strategy='heuristic', confidence=0.0)

            # Último recurso: si no pudimos producir un TradingDecision válido, usar HOLD fallback
            if decision is None:
                decision = TradingDecision(action='HOLD', amount=0, reason='Fallback: respuesta no proporcionada o no parseable', strategy='heuristic', confidence=0.0)

            # Calcular shares si es BUY
            shares = 0
            amount = decision.amount

            if decision.action == "BUY" and current_price > 0:
                # Si no especificó monto válido, usar valor entre 10-25% del efectivo
                if amount == 0 or amount < 100:
                    import random
                    pct = random.uniform(0.10, 0.25)
                    amount = self.simulator.cash * pct
                    print(f"[DEBUG] Monto auto-asignado: ${amount:.2f} ({pct*100:.1f}% del efectivo)")

                max_investment_limit = self.simulator.cash * 0.25
                min_investment = self.simulator.cash * 0.10
                amount = min(max(amount, min_investment), max_investment_limit)
                shares = amount / current_price
                amount = shares * current_price
                print(f"[DEBUG] BUY: {shares:.8f} shares @ ${current_price:.2f} = ${amount:.2f}")

            # Retornar decisión estructurada
            return {
                "action": decision.action,
                "amount": amount,
                "shares": shares,
                "reason": decision.reason,
                "strategy": decision.strategy,
                "confidence": decision.confidence,
                "ticker": ticker,
                "price": current_price,
                "date": timestamp_str,
                "indicators": indicators,  # NUEVO: incluir indicadores para análisis
                "ema48_projections": {  # NUEVO: incluir proyecciones EMA48
                    "ema48": ema48,
                    "proj_1": ema48_proj_1,
                    "proj_2": ema48_proj_2
                },
                "raw_response": str(decision)
            }

        except Exception as e:
            print(f"❌ Error obteniendo decisión LLM: {str(e)}")
            return {
                "action": "HOLD",
                "amount": 0,
                "shares": 0,
                "reason": f"Error: {str(e)}",
                "strategy": "",
                "confidence": 0.0,
                "ticker": ticker,
                "price": current_price,
                "date": timestamp_str,
                "indicators": self._empty_indicators(),
                "ema48_projections": {"ema48": 0, "proj_1": 0, "proj_2": 0}
            }

    def execute_decision(self, decision: Dict) -> Dict:
        """Ejecutar decisión del LLM"""
        action = decision['action']
        ticker = decision['ticker']

        if action == "HOLD":
            return {"success": True, "message": "HOLD - Sin operación"}

        elif action == "BUY":
            shares = decision['shares']
            if shares < 0.00000001:
                return {"success": False, "message": "Shares calculados muy pequeños"}

            return self.simulator.execute_buy(
                ticker=ticker,
                shares=shares,
                price=decision['price'],
                date=decision['date'],
                reason=decision['reason']
            )

        elif action == "SELL":
            if ticker not in self.simulator.portfolio:
                return {"success": False, "message": f"No tienes posición en {ticker}"}

            position = self.simulator.portfolio[ticker]
            amount = decision['amount']

            # amount es porcentaje (25-100)
            if amount < 25:
                amount = 25
            elif amount > 100:
                amount = 100

            shares_to_sell = position['shares'] * (amount / 100)

            return self.simulator.execute_sell(
                ticker=ticker,
                shares=shares_to_sell,
                price=decision['price'],
                date=decision['date'],
                reason=decision['reason']
            )

        return {"success": False, "message": "Acción no reconocida"}

def fetch_intraday_data(ticker: str = "BTC-USD", days: int = 7,
                       interval: str = "1h") -> pd.DataFrame:
    """
    Descargar datos intradía de Yahoo Finance - V3.0

    Args:
        ticker: Símbolo a operar
        days: Días históricos
        interval: Intervalo ('5m', '15m', '30m', '1h', '4h', '1d')
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Validar intervalos permitidos
    valid_intervals = ['5m', '15m', '30m', '1h', '4h', '1d']
    if interval not in valid_intervals:
        print(f"⚠️ Intervalo {interval} no válido. Usando '1h'")
        interval = '1h'

    try:
        print(f"📥 Descargando datos {interval} para {ticker} ({days} días)...")
        result = yf.download(ticker, start=start_date, end=end_date,
                           interval=interval, progress=False)

        if result is None or result.empty:
            print(f"⚠️ No se obtuvieron datos para {ticker}")
            return pd.DataFrame()

        df = result.reset_index()

        # Aplanar MultiIndex si existe - VERSIÓN DEFINITIVA
        if isinstance(df.columns, pd.MultiIndex):
            # Crear nuevas columnas completamente planas
            new_column_names = []
            for col in df.columns:
                if isinstance(col, tuple):
                    # Usar solo el primer elemento del tuple
                    new_column_names.append(col[0])
                else:
                    new_column_names.append(col)
            
            df.columns = new_column_names
        
        # Verificar que tenemos las columnas necesarias
        required_cols = ['Datetime', 'Close', 'High', 'Low', 'Open', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠️ Columnas faltantes: {missing_cols}")
            print(f"Columnas disponibles: {df.columns.tolist()}")

        print(f"✅ Columnas finales: {df.columns.tolist()}")
        print(f"✅ Descargados {len(df)} registros {interval} para {ticker}")
        return df
        print(f"✅ Descargados {len(df)} registros {interval} para {ticker}")
        return df

    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        return pd.DataFrame()

def run_hybrid_backtest_v3(ticker: str = "BTC-USD", days: int = 7,
                          interval: str = "1h", model_id: str = "deepseek-chat",
                          initial_capital: float = 10000.0,
                          decisions_interval: int = 1) -> Dict:
    """
    Ejecutar backtesting híbrido V3.0 completo

    Args:
        ticker: Símbolo a operar
        days: Días históricos
        interval: Intervalo de datos ('5m', '1h', etc.)
        model_id: ID del modelo LLM
        initial_capital: Capital inicial
        decisions_interval: Cada cuántos periodos tomar decisión
    """

    print("=" * 80)
    print("🚀 BACKTESTING HÍBRIDO V3.0 - EMA48 + TYPE SAFETY")
    print("=" * 80)
    print(f"📅 Período: {days} días")
    print(f"⏰ Intervalo de datos: {interval}")
    print(f"🎯 Intervalo de decisiones: Cada {decisions_interval} periodo(s)")
    print(f"💰 Capital inicial: ${initial_capital:,.2f}")
    print(f"🤖 Modelo: {model_id}")
    print(f"📊 Ticker: {ticker}")
    print("=" * 80)

    # Descargar datos
    df = fetch_intraday_data(ticker, days=days, interval=interval)

    if df.empty:
        return {"error": "No se pudieron descargar datos"}

    # Inicializar componentes
    simulator = TradingSimulatorV3(initial_capital=initial_capital)
    engine = BacktestEngineV3(simulator, model_id=model_id)

    print(f"\n🎯 Iniciando simulación con {len(df)} periodos de datos...")
    print(f"📊 Total de decisiones esperadas: ~{len(df) // decisions_interval}")

    decision_count = 0
    auto_close_count = 0

    # Procesar cada periodo
    for i in range(len(df)):
        row = df.iloc[i]

        # Extraer timestamp
        if 'Datetime' in df.columns:
            timestamp = row['Datetime']
        elif 'Date' in df.columns:
            timestamp = row['Date']
        else:
            timestamp = df.index[i]

        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

        # Extraer precio
        current_price = float(row['Close']) if 'Close' in df.columns else float(row.get('Close', 0))
        current_prices = {ticker: current_price}

        # Verificar stop loss / take profit
        auto_sales = simulator.check_risk_limits(current_prices, timestamp.strftime('%Y-%m-%d %H:%M'))
        for sale in auto_sales:
            auto_close_count += 1
            print(f"\n{'='*70}")
            print(f"🤖 AUTO-CIERRE #{auto_close_count} - {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"{'='*70}")
            print(f"Tipo: {sale['type']}")
            print(f"Ticker: {sale['ticker']}")
            print(f"P&L: {sale['pnl_pct']:+.2f}%")
            print(f"Efectivo después: ${simulator.cash:.2f}")
            simulator.auto_closes.append(sale)

        # Tomar decisión cada N periodos
        if i % decisions_interval == 0:
            decision_count += 1

            # Extraer High, Low, Volume
            high_price = float(row.get('High', current_price))
            low_price = float(row.get('Low', current_price))
            volume = float(row.get('Volume', 0))

            # Contexto de mercado
            market_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ TIMESTAMP: {timestamp.strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Precio actual {ticker}: ${current_price:,.2f}
📊 Volumen: {volume:,.0f}
📈 High: ${high_price:,.2f} | Low: ${low_price:,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            # Obtener decisión del LLM (V3.0 Hybrid)
            historical_slice = df.iloc[max(0, i-50):i+1]
            decision = engine.get_llm_decision(
                ticker=ticker,
                current_prices=current_prices,
                timestamp=timestamp,
                historical_data=historical_slice,
                market_context=market_context
            )

            # Ejecutar decisión
            result = engine.execute_decision(decision)

            # Agregar decisión al historial para aprendizaje contextual
            engine.add_decision_to_history(decision, result, timestamp)

            # Log
            print(f"\n{'='*70}")
            print(f"🤖 DECISIÓN #{decision_count} - {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"{'='*70}")
            print(f"Precio: ${current_price:,.2f}")
            print(f"Acción: {decision['action']}")
            print(f"Monto: ${decision['amount']:.2f}")
            print(f"Estrategia: {decision['strategy']}")
            print(f"Confianza: {decision['confidence']:.2f}")
            print(f"Razón: {decision['reason']}")
            print(f"Resultado: {result['message']}")

            portfolio_value = simulator.get_portfolio_value(current_prices)
            print(f"\n📊 Estado del Portfolio:")
            print(f"   - Efectivo: ${simulator.cash:.2f}")
            print(f"   - Valor total: ${portfolio_value:.2f}")
            print(f"   - Retorno: {((portfolio_value - initial_capital) / initial_capital * 100):+.2f}%")

            simulator.decisions_log.append(decision)

        # Registrar equity curve
        portfolio_value = simulator.get_portfolio_value(current_prices)
        simulator.equity_curve.append({
            'timestamp': timestamp,
            'portfolio_value': portfolio_value,
            'cash': simulator.cash,
            'price': current_price
        })

    # Calcular métricas finales
    # Usar el último precio disponible
    final_price = float(simulator.equity_curve[-1]['price']) if simulator.equity_curve else 0.0
    final_prices = {ticker: final_price}
    final_value = simulator.get_portfolio_value(final_prices)
    total_return = ((final_value - initial_capital) / initial_capital) * 100

    # Calcular win rate
    profitable_trades = [t for t in simulator.history if t['action'] == 'SELL' and t.get('profit', 0) > 0]
    total_trades = [t for t in simulator.history if t['action'] == 'SELL']
    win_rate = (len(profitable_trades) / len(total_trades) * 100) if total_trades else 0

    # Calcular max drawdown
    max_value = initial_capital
    max_drawdown = 0
    for point in simulator.equity_curve:
        if point['portfolio_value'] > max_value:
            max_value = point['portfolio_value']
        drawdown = ((point['portfolio_value'] - max_value) / max_value) * 100
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    results = {
        'version': '3.0 Hybrid',
        'ticker': ticker,
        'days': days,
        'interval': interval,
        'model': model_id,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return_pct': total_return,
        'total_trades': len(simulator.history),
        'buy_trades': len([t for t in simulator.history if t['action'] == 'BUY']),
        'sell_trades': len([t for t in simulator.history if t['action'] == 'SELL']),
        'win_rate': win_rate,
        'max_drawdown_pct': max_drawdown,
        'auto_closes': len(simulator.auto_closes),
        'stop_losses': len([a for a in simulator.auto_closes if a['type'] == 'STOP_LOSS']),
        'take_profits': len([a for a in simulator.auto_closes if a['type'] == 'TAKE_PROFIT']),
        'decisions_count': decision_count,
        'equity_curve': simulator.equity_curve,
        'history': simulator.history,
        'decisions_log': simulator.decisions_log,
        'auto_closes_log': simulator.auto_closes
    }

    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL - BACKTESTING HÍBRIDO V3.0")
    print("=" * 80)
    print(f"💰 Capital inicial: ${initial_capital:,.2f}")
    print(f"💵 Capital final: ${final_value:,.2f}")
    print(f"📈 Retorno total: {total_return:+.2f}%")
    print(f"🎯 Total operaciones: {len(simulator.history)}")
    print(f"   - Compras: {results['buy_trades']}")
    print(f"   - Ventas: {results['sell_trades']}")
    print(f"✅ Win Rate: {win_rate:.1f}%")
    print(f"📉 Max Drawdown: {max_drawdown:.2f}%")
    print(f"🤖 Auto-cierres: {len(simulator.auto_closes)}")
    print(f"   - Stop Loss: {results['stop_losses']}")
    print(f"   - Take Profit: {results['take_profits']}")
    print(f"🧠 Decisiones LLM: {decision_count}")
    print(f"⚡ Intervalo: {interval}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    import sys

    # Parámetros desde CLI
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    interval = sys.argv[2] if len(sys.argv) > 2 else "1h"
    decisions_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    # Ejecutar backtest híbrido V3.0
    results = run_hybrid_backtest_v3(
        ticker="BTC-USD",
        days=days,
        interval=interval,
        model_id="deepseek-chat",
        initial_capital=10000.0,
        decisions_interval=decisions_interval
    )

    # Guardar resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backtest_hybrid_v3_{interval}_{days}d_{decisions_interval}int_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Resultados guardados en: {filename}")
    print(f"\n✅ Para generar dashboard HTML ejecuta:")
    print(f"   python generate_dashboard.py {filename}")
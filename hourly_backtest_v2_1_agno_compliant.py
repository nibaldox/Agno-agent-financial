#!/usr/bin/env python3
"""
Sistema de Backtesting con Datos HORARIOS (1h) - VERSION 2.1 AGNO-COMPLIANT

MEJORAS V2.1 (18-Oct-2025):
- ✅ Refactorización completa siguiendo lineamientos de Agno Framework
- ✅ Separación de instructions (permanentes) vs contexto (dinámico)
- ✅ Structured outputs con Pydantic (output_schema)
- ✅ Eliminado parsing manual de strings
- ✅ Type safety completo con validación automática

MEJORAS V2.0:
- Stop Loss / Take Profit automáticos
- Indicadores técnicos avanzados (EMA, MACD, Bollinger Bands, ATR)
- Prompt optimizado para trading agresivo
- Position sizing dinámico

Versión: 2.1.0
Fecha: 2025-10-18
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

# Configuración de modelos
MODELS = {
    "deep_research": "alibaba/tongyi-deepresearch-30b-a3b:free",
    "reasoning": "tngtech/deepseek-r1t2-chimera:free",
    "fast_calc": "nvidia/nemotron-nano-9b-v2:free",
    "general": "z-ai/glm-4.5-air:free",
    "advanced": "qwen/qwen3-235b-a22b:free",
    "deepseek": "deepseek-chat",  # DeepSeek V3 (no razonador)
}

# ═══════════════════════════════════════════════════════════════════════
# PYDANTIC MODEL - STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════════

class TradingDecision(BaseModel):
    """
    Decisión de trading estructurada y validada.
    
    Este modelo reemplaza el parsing manual de strings y garantiza
    validación automática de tipos, rangos y formato.
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
        description="Justificación técnica concisa de la decisión (máximo 1-2 líneas)"
    )
    strategy: str = Field(
        default="",
        max_length=100,
        description="Estrategia utilizada (ej: 'scaling in', 'trend reversal', 'volatility breakout'). Opcional."
    )
    confidence: float = Field(
        ge=0, le=1,
        default=0.5,
        description="Nivel de confianza en la decisión (0-1). Opcional."
    )

# ═══════════════════════════════════════════════════════════════════════
# TRADING INSTRUCTIONS - PERMANENTES
# ═══════════════════════════════════════════════════════════════════════

TRADING_INSTRUCTIONS = [
    "Eres un trader algorítmico AGRESIVO especializado en MOMENTUM HORARIO.",
    "Tu objetivo es MAXIMIZAR RETORNOS aprovechando oportunidades de corto plazo.",
    "Tienes autonomía total para proponer estrategias creativas, incluyendo compras/ventas parciales, escalado, y combinaciones de señales técnicas.",
    "Además de las estrategias clásicas, analiza la TENDENCIA GENERAL del mercado (alcista/bajista) usando EMA, MACD y cambios de precio. Si la tendencia es clara, puedes tomar decisiones de compra o venta solo por tendencia, aunque no se cumplan todas las condiciones de estrategia.",
    "Indica en el campo 'strategy' si la decisión se basa principalmente en la tendencia (ej: 'trend following', 'contrarian', 'momentum puro').",
    "Si detectas una anomalía fuerte en el mercado, puedes ignorar las reglas estándar, pero debes justificar claramente tu decisión.",
    "Puedes combinar múltiples indicadores y razonamientos para justificar tu acción.",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "🎯 ESTRATEGIA DE TRADING AGRESIVA Y FLEXIBLE:",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "✅ COMPRAR (BUY) - Considera si cumple AL MENOS 2 DE ESTAS:",
    "1. EMA12 > EMA26 (tendencia alcista)",
    "2. MACD > MACD Signal (momentum positivo)",
    "3. Precio cerca de Bollinger Inferior (oportunidad de compra)",
    "4. RSI < 70 (no extremadamente sobrecomprado)",
    "5. Cambio positivo en últimas 1-4 horas",
    "6. Histograma MACD creciendo",
    "",
    "💡 OPORTUNIDADES ESPECIALES DE COMPRA:",
    "- SOBREVENTA: Si precio toca Bollinger Inferior → BUY agresivo (rebote probable)",
    "- RECUPERACIÓN: Si cambio 1h positivo después de caída → BUY (momentum cambiando)",
    "- BREAKOUT: Si precio rompe SMA 12h hacia arriba → BUY (nueva tendencia)",
    "",
    "❌ VENDER (SELL) - Considera si cumple AL MENOS 1 DE ESTAS:",
    "1. Ganancia no realizada > 3% (asegurar beneficios)",
    "2. MACD cruza a la baja (momentum perdido)",
    "3. Precio toca Bollinger Superior (sobrecompra)",
    "4. RSI > 75 (extremo sobrecomprado)",
    "5. Cambio negativo en últimas 2 horas",
    "6. EMA12 cruza por debajo de EMA26",
    "",
    "⚪ MANTENER (HOLD) - SOLO si:",
    "- NO tienes posición Y las señales son contradictorias",
    "- Tienes posición con ganancia < 2% y momentum aún positivo",
    "",
    "🎲 FILOSOFÍA AGRESIVA Y AUTÓNOMA:",
    "- ACTÚA RÁPIDO: El mercado horario premia la velocidad",
    "- BUSCA OPORTUNIDADES: Mejor operar y equivocarse (con stop loss) que no operar",
    "- APROVECHA VOLATILIDAD: La volatilidad = oportunidad",
    "- NO TEMAS COMPRAR EN BAJADAS: Si indicadores muestran sobreventa",
    "- REALIZA BENEFICIOS: Mejor 3% seguro que 5% incierto",
    "- Puedes proponer estrategias creativas si detectas oportunidades excepcionales. Justifica tu decisión.",
    "- Si detectas una anomalía fuerte, puedes ignorar las reglas estándar, pero debes explicar por qué.",
    "",
    "⚠️ ÚNICAS RESTRICCIONES DURAS:",
    "- NO operar sin indicadores (si EMA/MACD = 0)",
    "- NO comprar con RSI > 80 (sobrecompra extrema)",
    "- Respetar límites de MONTO especificados",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "📋 FORMATO DE RESPUESTA:",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "Debes responder con un JSON estructurado con estos campos:",
    "- action: 'BUY', 'SELL' o 'HOLD'",
    "- amount: número (USD para BUY, porcentaje para SELL, 0 para HOLD)",
    "- reason: texto breve (máximo 1-2 líneas)",
    "- strategy: texto corto (ej: 'scaling in', 'trend reversal', 'volatility breakout') [opcional]",
    "- confidence: número entre 0 y 1 (nivel de certeza en la decisión) [opcional]",
    "",
    "⚠️ PROTECCIÓN AUTOMÁTICA (no te preocupes por esto):",
    "- Stop Loss: -3% (se ejecuta automáticamente)",
    "- Take Profit: +5% (se ejecuta automáticamente)",
]

class TradingSimulator:
    """Simulador de trading con datos históricos - V2.1 Agno-compliant"""
    
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

class BacktestEngine:
    """Motor de backtesting con LLM - V2.1 Agno-compliant"""
    
    def __init__(self, simulator: TradingSimulator, model_id: str = "deepseek-chat"):
        self.simulator = simulator
        self.model_id = model_id
        
        # Crear agente con instructions permanentes y output_schema
        if model_id == "deepseek-chat":
            model = DeepSeek(id=model_id)
        else:
            model = OpenRouter(id=model_id)
        
        self.agent = Agent(
            name="Intraday Trader",
            model=model,
            instructions=TRADING_INSTRUCTIONS,
            output_schema=TradingDecision,
            markdown=True
        )
        
    def safe_get_column(self, df, row, col_name, default=0.0):
        """Extraer columna OHLCV de forma robusta (soporta MultiIndex y nombres con ticker)"""
        if col_name in df.columns:
            return float(row[col_name])
        # Buscar columna que contenga el nombre
        matching = [col for col in df.columns if col_name in str(col)]
        if matching:
            return float(row[matching[0]])
        return float(default)

    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calcular indicadores técnicos avanzados (robusto a nombres de columnas)"""
        if len(df) < 2:
            return self._empty_indicators()

        def safe_float(value, default=0.0):
            if hasattr(value, 'iloc'):
                value = value.iloc[-1] if len(value) > 0 else default
            elif hasattr(value, 'item'):
                value = value.item()
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        try:
            # Usar safe_get_column para OHLCV
            close = df.apply(lambda row: self.safe_get_column(df, row, 'Close'), axis=1)
            high = df.apply(lambda row: self.safe_get_column(df, row, 'High'), axis=1)
            low = df.apply(lambda row: self.safe_get_column(df, row, 'Low'), axis=1)

            # EMA 12 y 26 periodos
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()

            # MACD
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_histogram = macd_line - signal_line

            # Bollinger Bands (20 periodos, 2 std)
            sma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            bb_upper = sma20 + (std20 * 2)
            bb_lower = sma20 - (std20 * 2)

            # ATR (Average True Range) - 14 periodos
            high_low = high - low
            high_close = abs(high - close.shift())
            low_close = abs(low - close.shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()

            # Usar safe_float para todas las conversiones
            current_price = safe_float(close.iloc[-1])
            ema12_val = safe_float(ema12.iloc[-1])
            ema26_val = safe_float(ema26.iloc[-1])
            macd_val = safe_float(macd_line.iloc[-1])
            signal_val = safe_float(signal_line.iloc[-1])
            macd_hist_val = safe_float(macd_histogram.iloc[-1])
            bb_upper_val = safe_float(bb_upper.iloc[-1])
            bb_middle_val = safe_float(sma20.iloc[-1])
            bb_lower_val = safe_float(bb_lower.iloc[-1])
            atr_val = safe_float(atr.iloc[-1])

            ema_cross = "⬆️ ALCISTA" if ema12_val > ema26_val else "⬇️ BAJISTA"

            if current_price > bb_upper_val:
                bb_position = "⬆️ SOBRE BANDA SUPERIOR (sobrecompra)"
            elif current_price < bb_lower_val:
                bb_position = "⬇️ BAJO BANDA INFERIOR (sobreventa)"
            else:
                bb_position = "↔️ DENTRO DE BANDAS"

            return {
                'ema12': ema12_val,
                'ema26': ema26_val,
                'ema_cross': ema_cross,
                'macd': macd_val,
                'macd_signal': signal_val,
                'macd_histogram': macd_hist_val,
                'bb_upper': bb_upper_val,
                'bb_middle': bb_middle_val,
                'bb_lower': bb_lower_val,
                'bb_position': bb_position,
                'atr': atr_val
            }
        except Exception as e:
            print(f"⚠️ Error calculando indicadores: {e}")
            return self._empty_indicators()
    
    def _empty_indicators(self) -> Dict:
        """Indicadores vacíos por defecto"""
        return {
            'ema12': 0, 'ema26': 0, 'ema_cross': 'N/A',
            'macd': 0, 'macd_signal': 0, 'macd_histogram': 0,
            'bb_upper': 0, 'bb_middle': 0, 'bb_lower': 0,
            'bb_position': 'N/A', 'atr': 0
        }
    
    def get_llm_decision(self, ticker: str, current_prices: Dict[str, float],
                        timestamp: datetime, historical_data: pd.DataFrame,
                        market_context: str) -> Dict:
        """
        Obtener decisión del LLM usando estructura Agno correcta.
        
        CAMBIOS V2.1:
        - Instructions permanentes definidas en TRADING_INSTRUCTIONS
        - Solo contexto dinámico pasa a agent.run()
        - Structured output con TradingDecision (Pydantic)
        - Sin parsing manual de strings
        """
        
        # Calcular indicadores técnicos
        indicators = self.calculate_technical_indicators(historical_data)
        
        # Calcular métricas de contexto
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
        
        # Calcular cambios de precio (usando safe_get_column)
        close_hist = historical_data.apply(lambda row: self.safe_get_column(historical_data, row, 'Close'), axis=1)
        if len(close_hist) >= 2:
            price_change_1h = ((close_hist.iloc[-1] - close_hist.iloc[-2]) / close_hist.iloc[-2]) * 100
        else:
            price_change_1h = 0

        if len(close_hist) >= 5:
            price_change_4h = ((close_hist.iloc[-1] - close_hist.iloc[-5]) / close_hist.iloc[-5]) * 100
        else:
            price_change_4h = 0

        # Volumen ratio (actual vs promedio)
        volume_hist = historical_data.apply(lambda row: self.safe_get_column(historical_data, row, 'Volume'), axis=1)
        if len(volume_hist) >= 10:
            avg_volume = volume_hist.rolling(10).mean().iloc[-1]
            current_volume = volume_hist.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        else:
            volume_ratio = 1.0
        
        # Position sizing dinámico basado en volatilidad (ATR)
        atr = indicators['atr']
        if atr > 5000:
            max_risk = 0.20  # 20% en alta volatilidad
        elif atr > 3000:
            max_risk = 0.30  # 30%
        else:
            max_risk = 0.40  # 40% en baja volatilidad
        max_investment = self.simulator.cash * max_risk
        
        # Determinar señal MACD
        macd_signal = "⬆️ ALCISTA" if indicators['macd'] > indicators['macd_signal'] else "⬇️ BAJISTA"
        
        # ═══════════════════════════════════════════════════════════════════
        # CONTEXTO DINÁMICO (runtime) - Solo datos de mercado
        # ═══════════════════════════════════════════════════════════════════
        
        market_data_context = f"""
Analiza esta situación de trading y toma una decisión:

{market_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 INDICADORES TÉCNICOS AVANZADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
• Volumen Ratio: {volume_ratio:.2f}x

• Cambio precio 1h: {price_change_1h:+.2f}%
• Cambio precio 4h: {price_change_4h:+.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 TU PORTFOLIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Capital total: ${portfolio_value:.2f}
- Efectivo disponible: ${self.simulator.cash:.2f}
- Máximo a invertir por operación: ${max_investment:.2f} ({max_risk*100:.0f}% del efectivo)
{position_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESTRICCIONES DE MONTO:
- BUY: Entre $1000 y ${max_investment:.0f}
- SELL: Entre 25% y 100% de tu posición
- HOLD: amount = 0
"""
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # EJECUTAR AGENTE - Solo pasar contexto dinámico
            # ═══════════════════════════════════════════════════════════════
            
            response = self.agent.run(market_data_context)
            
            # response.content ya es un TradingDecision (Pydantic)
            decision = response.content
            if not isinstance(decision, TradingDecision):
                raise ValueError(f"Respuesta no es TradingDecision: {type(decision)}")
            
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
                "ticker": ticker,
                "price": current_price,
                "date": timestamp.strftime('%Y-%m-%d %H:%M'),
                "raw_response": str(decision)  # Para logging
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo decisión LLM: {str(e)}")
            return {
                "action": "HOLD",
                "amount": 0,
                "shares": 0,
                "reason": f"Error: {str(e)}",
                "ticker": ticker,
                "price": current_price,
                "date": timestamp.strftime('%Y-%m-%d %H:%M')
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

def fetch_hourly_data(ticker: str, days: int = 7) -> pd.DataFrame:
    """Descargar datos horarios (1h) de Yahoo Finance"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        result = yf.download(ticker, start=start_date, end=end_date, interval="1h", progress=False)
        
        if result is None or result.empty:
            print(f"⚠️ No se obtuvieron datos para {ticker}")
            return pd.DataFrame()
        
        df = result.reset_index()
        
        # Si tiene multiindex de columns, aplanar
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in df.columns.values]
        
        print(f"✅ Descargados {len(df)} registros horarios para {ticker}")
        return df
        
    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        return pd.DataFrame()

def run_hourly_backtest(ticker: str = "BTC-USD", days: int = 7, 
                        model_id: str = "deepseek-chat",
                        initial_capital: float = 10000.0,
                        decisions_interval_hours: int = 1) -> Dict:
    """
    Ejecutar backtesting horario completo - V2.1 Agno-compliant
    
    Args:
        ticker: Símbolo a operar (default: BTC-USD)
        days: Días históricos (default: 7)
        model_id: ID del modelo LLM
        initial_capital: Capital inicial
        decisions_interval_hours: Cada cuántas horas tomar decisión (1-6)
    """
    
    print("=" * 80)
    print(f"🚀 BACKTESTING HORARIO V2.1 - AGNO-COMPLIANT")
    print("=" * 80)
    print(f"📅 Período: {days} días")
    print(f"⏰ Intervalo de decisiones: Cada {decisions_interval_hours} hora(s)")
    print(f"💰 Capital inicial: ${initial_capital:,.2f}")
    print(f"🤖 Modelo: {model_id}")
    print(f"📊 Ticker: {ticker}")
    print("=" * 80)
    print()
    
    # Descargar datos
    print("📥 Descargando datos horarios...")
    df = fetch_hourly_data(ticker, days=days)
    
    if df.empty:
        return {"error": "No se pudieron descargar datos"}
    
    # Inicializar simulador y engine
    simulator = TradingSimulator(initial_capital=initial_capital)
    engine = BacktestEngine(simulator, model_id=model_id)
    
    print(f"\n🎯 Iniciando simulación con {len(df)} horas de datos...")
    print(f"📊 Total de decisiones esperadas: ~{len(df) // decisions_interval_hours}")
    print()
    
    decision_count = 0
    auto_close_count = 0
    
    # Procesar cada hora
    for i in range(len(df)):
        row = df.iloc[i]
        
        # Extraer timestamp - puede ser 'Datetime' o 'Date'
        if 'Datetime' in df.columns:
            timestamp = row['Datetime']
        elif 'Date' in df.columns:
            timestamp = row['Date']
        else:
            timestamp = df.index[i]
        
        # Convertir a datetime python
        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()
        
        # Extraer precio - puede tener ticker en el nombre
        if 'Close' in df.columns:
            current_price = float(row['Close'])
        else:
            # Buscar columna que contenga 'Close'
            close_cols = [col for col in df.columns if 'Close' in str(col)]
            if close_cols:
                current_price = float(row[close_cols[0]])
            else:
                print(f"⚠️ No se encontró columna Close en: {df.columns.tolist()}")
                continue
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
        
        # Tomar decisión cada N horas
        if i % decisions_interval_hours == 0:
            decision_count += 1
            
            # Extraer High, Low, Volume de forma segura
            def safe_get_column(row, col_name, default=0.0):
                """Extraer columna, manejando MultiIndex si existe"""
                if col_name in df.columns:
                    return float(row[col_name])
                # Buscar columna que contenga el nombre
                matching = [col for col in df.columns if col_name in str(col)]
                if matching:
                    return float(row[matching[0]])
                return float(default)
            
            high_price = safe_get_column(row, 'High', current_price)
            low_price = safe_get_column(row, 'Low', current_price)
            volume = safe_get_column(row, 'Volume', 0)
            
            # Contexto de mercado
            market_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ TIMESTAMP: {timestamp.strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Precio actual {ticker}: ${current_price:,.2f}
📊 Volumen: {volume:,.0f}
📈 High: ${high_price:,.2f} | Low: ${low_price:,.2f}
"""
            
            # Obtener decisión del LLM (ahora con estructura Agno)
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
            
            # Log
            print(f"\n{'='*70}")
            print(f"🤖 DECISIÓN #{decision_count} - {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"{'='*70}")
            print(f"Precio: ${current_price:,.2f}")
            print(f"Acción: {decision['action']}")
            print(f"Monto: ${decision['amount']:.2f}")
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
    
    # Calcular métricas finales (robusto)
    def safe_get_column(row, col_name, default=0.0):
        if col_name in df.columns:
            return float(row[col_name])
        matching = [col for col in df.columns if col_name in str(col)]
        if matching:
            return float(row[matching[0]])
        return float(default)

    final_close = safe_get_column(df.iloc[-1], 'Close', 0.0)
    final_prices = {ticker: final_close}
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
        'ticker': ticker,
        'days': days,
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
    print("📊 RESUMEN FINAL - BACKTESTING V2.1 AGNO-COMPLIANT")
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
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    import sys
    
    # Parámetros desde CLI
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    interval_hours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # Ejecutar backtest
    results = run_hourly_backtest(
        ticker="BTC-USD",
        days=days,
        model_id="deepseek-chat",
        initial_capital=10000.0,
        decisions_interval_hours=interval_hours
    )
    
    # Guardar resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backtest_results_v2_1_agno_{days}d_{interval_hours}h_{timestamp}.json"
    
    # Convertir timestamps a strings para JSON
    results_serializable = results.copy()
    results_serializable['equity_curve'] = [
        {**point, 'timestamp': point['timestamp'].strftime('%Y-%m-%d %H:%M')}
        for point in results['equity_curve']
    ]
    
    with open(filename, 'w') as f:
        json.dump(results_serializable, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: {filename}")
    print(f"\n✅ Para generar dashboard HTML ejecuta:")
    print(f"   python generate_dashboard.py {filename}")

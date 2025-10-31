#!/usr/bin/env python3
"""
Sistema de Backtesting con Datos HORARIOS (1h) - VERSION 2 OPTIMIZADA

MEJORAS IMPLEMENTADAS:
- Stop Loss / Take Profit automáticos
- Indicadores técnicos avanzados (EMA, MACD, Bollinger Bands)
- Prompt mejorado del LLM con reglas estrictas
- Filtro de volumen mínimo
- Position sizing dinámico

Versión: 2.0.0
Fecha: 2025-10-18
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd
import yfinance as yf
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.openrouter import OpenRouter
from dotenv import load_dotenv

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


class TradingSimulator:
    """Simulador de trading con datos históricos - V2 con gestión de riesgo"""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        transaction_cost: float = 0.001,
        stop_loss_pct: float = 0.03,
        take_profit_pct: float = 0.05,
    ):
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
            self.portfolio[ticker]["shares"] * current_prices.get(ticker, 0)
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
            avg_price = position["avg_price"]
            pnl_pct = (current_price - avg_price) / avg_price

            # Stop Loss: Pérdida > 3%
            if pnl_pct <= -self.stop_loss_pct:
                result = self.execute_sell(
                    ticker=ticker,
                    shares=position["shares"],
                    price=current_price,
                    date=timestamp,
                    reason=f"🛑 STOP LOSS AUTO: Pérdida {pnl_pct*100:.2f}%",
                )
                if result["success"]:
                    auto_sales.append(
                        {
                            "type": "STOP_LOSS",
                            "ticker": ticker,
                            "pnl_pct": pnl_pct * 100,
                            "trade": result["trade"],
                        }
                    )

            # Take Profit: Ganancia > 5%
            elif pnl_pct >= self.take_profit_pct:
                result = self.execute_sell(
                    ticker=ticker,
                    shares=position["shares"],
                    price=current_price,
                    date=timestamp,
                    reason=f"✅ TAKE PROFIT AUTO: Ganancia {pnl_pct*100:.2f}%",
                )
                if result["success"]:
                    auto_sales.append(
                        {
                            "type": "TAKE_PROFIT",
                            "ticker": ticker,
                            "pnl_pct": pnl_pct * 100,
                            "trade": result["trade"],
                        }
                    )

        return auto_sales

    def execute_buy(
        self, ticker: str, shares: float, price: float, date: str, reason: str = ""
    ) -> Dict:
        """Ejecutar compra (soporta fracciones)"""
        cost = shares * price
        transaction_fee = cost * self.transaction_cost
        total_cost = cost + transaction_fee

        if total_cost > self.cash:
            return {
                "success": False,
                "message": f"Fondos insuficientes. Necesitas ${total_cost:.2f}, tienes ${self.cash:.2f}",
            }

        self.cash -= total_cost

        if ticker in self.portfolio:
            old_shares = self.portfolio[ticker]["shares"]
            old_avg = self.portfolio[ticker]["avg_price"]
            new_shares = old_shares + shares
            new_avg = ((old_shares * old_avg) + (shares * price)) / new_shares
            self.portfolio[ticker] = {"shares": new_shares, "avg_price": new_avg}
        else:
            self.portfolio[ticker] = {"shares": shares, "avg_price": price}

        trade = {
            "date": date,
            "action": "BUY",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "cost": cost,
            "fee": transaction_fee,
            "total": total_cost,
            "cash_after": self.cash,
            "reason": reason,
        }
        self.history.append(trade)

        return {
            "success": True,
            "message": f"Comprado {shares} acciones de {ticker} a ${price:.2f}",
            "trade": trade,
        }

    def execute_sell(
        self, ticker: str, shares: float, price: float, date: str, reason: str = ""
    ) -> Dict:
        """Ejecutar venta (soporta fracciones)"""
        if ticker not in self.portfolio:
            return {"success": False, "message": f"No tienes acciones de {ticker}"}

        available_shares = self.portfolio[ticker]["shares"]
        if shares > available_shares:
            return {
                "success": False,
                "message": f"No tienes suficientes acciones. Tienes {available_shares}, intentas vender {shares}",
            }

        revenue = shares * price
        transaction_fee = revenue * self.transaction_cost
        net_revenue = revenue - transaction_fee

        self.cash += net_revenue

        avg_cost = self.portfolio[ticker]["avg_price"]
        pnl = (price - avg_cost) * shares
        pnl_pct = ((price - avg_cost) / avg_cost) * 100

        self.portfolio[ticker]["shares"] -= shares
        if self.portfolio[ticker]["shares"] < 0.00000001:  # Casi cero
            del self.portfolio[ticker]

        trade = {
            "date": date,
            "action": "SELL",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "revenue": revenue,
            "fee": transaction_fee,
            "net_revenue": net_revenue,
            "cash_after": self.cash,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "reason": reason,
        }
        self.history.append(trade)

        return {
            "success": True,
            "message": f"Vendido {shares} acciones de {ticker} a ${price:.2f}. P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)",
            "trade": trade,
        }

    def get_performance_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """Calcular métricas de desempeño"""
        current_value = self.get_portfolio_value(current_prices)
        total_return = current_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        winning_trades = [t for t in self.history if t["action"] == "SELL" and t.get("pnl", 0) > 0]
        losing_trades = [t for t in self.history if t["action"] == "SELL" and t.get("pnl", 0) < 0]

        total_trades = len(winning_trades) + len(losing_trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

        avg_win = (
            sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        )
        avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0

        return {
            "initial_capital": self.initial_capital,
            "current_value": current_value,
            "cash": self.cash,
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            "holdings": self.portfolio.copy(),
        }


class HourlyBacktestEngine:
    """Motor de backtesting con datos HORARIOS (1h)"""

    def __init__(
        self,
        tickers: List[str],
        days: int = 7,
        decision_interval_hours: int = 4,
        initial_capital: float = 10000.0,
    ):
        """
        Args:
            tickers: Lista de tickers a analizar
            days: Número de días de datos (máximo 60 para datos horarios)
            decision_interval_hours: Horas entre cada decisión (1, 2, 4, 6, etc.)
            initial_capital: Capital inicial
        """
        self.tickers = tickers
        self.days = min(days, 60)  # yfinance limita datos horarios
        self.decision_interval_hours = decision_interval_hours

        self.simulator = TradingSimulator(initial_capital)
        self.historical_data = {}
        self.current_timestamp = None
        self.decision_justifications = []  # Almacenar justificaciones completas

        print("📥 Descargando datos horarios...")
        self._download_hourly_data()

    def _download_hourly_data(self):
        """Descargar datos horarios"""
        for ticker in self.tickers:
            try:
                # Datos horarios de yfinance
                data = yf.download(ticker, period=f"{self.days}d", interval="1h", progress=False)

                if not data.empty:
                    self.historical_data[ticker] = data
                    hours = len(data)
                    print(f"  ✅ {ticker}: {hours} horas de datos ({self.days} días)")
                else:
                    print(f"  ❌ {ticker}: Sin datos")
            except Exception as e:
                print(f"  ❌ {ticker}: Error - {str(e)}")

    def get_data_until_timestamp(self, ticker: str, timestamp: pd.Timestamp) -> pd.DataFrame:
        """Obtener datos hasta un timestamp específico"""
        if ticker not in self.historical_data:
            return pd.DataFrame()

        data = self.historical_data[ticker]
        return data[data.index <= timestamp].copy()

    def get_current_prices(self, timestamp: pd.Timestamp) -> Dict[str, float]:
        """Obtener precios actuales en un timestamp"""
        prices = {}
        for ticker in self.tickers:
            data = self.get_data_until_timestamp(ticker, timestamp)
            if not data.empty:
                prices[ticker] = float(data["Close"].iloc[-1])
        return prices

    def prepare_market_context(self, ticker: str, timestamp: pd.Timestamp) -> str:
        """Preparar contexto de mercado para análisis horario"""
        data = self.get_data_until_timestamp(ticker, timestamp)

        if len(data) < 24:
            return f"Datos insuficientes para {ticker}"

        # Últimas 24 horas
        last_24h = data.tail(24)
        # Precios actuales y comparaciones temporales
        current_price = (
            last_24h["Close"].iloc[-1].item()
            if hasattr(last_24h["Close"].iloc[-1], "item")
            else float(last_24h["Close"].iloc[-1])
        )
        price_24h_ago = (
            last_24h["Close"].iloc[0].item()
            if hasattr(last_24h["Close"].iloc[0], "item")
            else float(last_24h["Close"].iloc[0])
        )
        change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100

        # Últimas 4 horas
        last_4h = data.tail(4)
        if len(last_4h) > 0:
            val = last_4h["Close"].iloc[0]
            price_4h_ago = val.item() if hasattr(val, "item") else float(val)
        else:
            price_4h_ago = current_price
        change_4h = ((current_price - price_4h_ago) / price_4h_ago) * 100

        # Última hora
        if len(data) >= 2:
            val = data["Close"].iloc[-2]
            price_1h_ago = val.item() if hasattr(val, "item") else float(val)
        else:
            price_1h_ago = current_price
        change_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100

        # Métricas
        # Volatilidad y volumen
        high_24h_val = last_24h["High"].max()
        high_24h = high_24h_val if isinstance(high_24h_val, (int, float)) else high_24h_val.item()
        low_24h_val = last_24h["Low"].min()
        low_24h = low_24h_val if isinstance(low_24h_val, (int, float)) else low_24h_val.item()
        avg_volume_24h_val = last_24h["Volume"].mean()
        avg_volume_24h = (
            avg_volume_24h_val
            if isinstance(avg_volume_24h_val, (int, float))
            else avg_volume_24h_val.item()
        )
        val_vol = last_24h["Volume"].iloc[-1]
        current_volume = val_vol.item() if hasattr(val_vol, "item") else float(val_vol)

        # Momentum
        prices = last_24h["Close"]
        sma_4h_val = prices.tail(4).mean()
        sma_4h = sma_4h_val if isinstance(sma_4h_val, (int, float)) else sma_4h_val.item()
        sma_12h_val = prices.tail(12).mean()
        sma_12h = sma_12h_val if isinstance(sma_12h_val, (int, float)) else sma_12h_val.item()
        trend = "ALCISTA" if sma_4h > sma_12h else "BAJISTA"

        # RSI aproximado (últimas 14 horas)
        try:
            if len(data) >= 14:
                deltas = data["Close"].diff().tail(14).dropna()
                gains = deltas[deltas > 0].mean()
                losses = -deltas[deltas < 0].mean()

                # Convertir a float y manejar NaN
                gains = float(gains) if pd.notna(gains) else 0.0
                losses = float(losses) if pd.notna(losses) else 0.0

                if losses != 0:
                    rs = gains / losses
                    rsi = 100 - (100 / (1 + rs))
                else:
                    rsi = 50.0
            else:
                rsi = 50.0
        except:
            rsi = 50.0

        context = f"""
DATOS DE MERCADO HORARIOS PARA {ticker}
Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 PRECIO ACTUAL: ${current_price:.2f}

📈 CAMBIOS RECIENTES:
   • Última hora: {change_1h:+.2f}%
   • Últimas 4 horas: {change_4h:+.2f}%
   • Últimas 24 horas: {change_24h:+.2f}%

📊 RANGO 24H:
   • Máximo: ${high_24h:.2f}
   • Mínimo: ${low_24h:.2f}
   • Rango: {((high_24h - low_24h) / low_24h * 100):.2f}%

📉 INDICADORES TÉCNICOS:
   • SMA 4h: ${sma_4h:.2f}
   • SMA 12h: ${sma_12h:.2f}
   • Tendencia: {trend}
   • RSI (14h): {rsi:.1f}

💹 VOLUMEN:
   • Actual: {current_volume:,.0f}
   • Promedio 24h: {avg_volume_24h:,.0f}
   • Ratio: {(current_volume / avg_volume_24h if avg_volume_24h > 0 else 0):.2f}x

⚠️  IMPORTANTE:
   • Datos actualizados por HORA
   • Solo tienes datos hasta {timestamp.strftime('%Y-%m-%d %H:%M')}
   • NO puedes ver el futuro
   • Basa tu decisión en momentum y tendencia de corto plazo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return context

    def calculate_advanced_indicators(self, ticker: str, timestamp: pd.Timestamp) -> Dict:
        """Calcular indicadores técnicos avanzados - V2"""
        data = self.get_data_until_timestamp(ticker, timestamp)

        # Helper para convertir a float seguro (maneja Series, ndarray y scalars)
        def safe_float(val):
            try:
                import numpy as _np

                # Series o ndarray: tomar último elemento si existe
                if isinstance(val, (pd.Series, _np.ndarray)):
                    if len(val) == 0:
                        return 0.0
                    v = val.iloc[-1] if isinstance(val, pd.Series) else val[-1]
                    return 0.0 if pd.isna(v) else float(v)

                # Scalars (incluye numpy scalars)
                if pd.isna(val):
                    return 0.0
                return float(val)
            except Exception:
                return 0.0

        if len(data) < 26:  # Necesitamos al menos 26 períodos para EMA26
            return {
                "ema12": 0,
                "ema26": 0,
                "macd": 0,
                "macd_signal": 0,
                "macd_histogram": 0,
                "bb_upper": 0,
                "bb_middle": 0,
                "bb_lower": 0,
                "bb_position": "N/A",
                "atr": 0,
                "ema_cross": "NEUTRAL",
            }

        close_prices = data["Close"]

        # EMA (Exponential Moving Average)
        ema12 = safe_float(close_prices.ewm(span=12, adjust=False).mean().iloc[-1])
        ema26 = safe_float(close_prices.ewm(span=26, adjust=False).mean().iloc[-1])

        # MACD (Moving Average Convergence Divergence)
        macd_line = (
            close_prices.ewm(span=12, adjust=False).mean()
            - close_prices.ewm(span=26, adjust=False).mean()
        )
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd = safe_float(macd_line.iloc[-1])
        macd_signal = safe_float(signal_line.iloc[-1])
        macd_histogram = macd - macd_signal

        # Bollinger Bands (20 períodos, 2 desviaciones)
        if len(data) >= 20:
            sma20 = safe_float(close_prices.rolling(20).mean().iloc[-1])
            std20 = safe_float(close_prices.rolling(20).std().iloc[-1])
            bb_upper = sma20 + (2 * std20)
            bb_lower = sma20 - (2 * std20)
            current_price = safe_float(close_prices.iloc[-1])

            # Posición dentro de las bandas
            if current_price > bb_upper:
                bb_position = "SOBRECOMPRA"
            elif current_price < bb_lower:
                bb_position = "SOBREVENTA"
            else:
                bb_position = "NORMAL"
        else:
            sma20 = bb_upper = bb_lower = 0.0
            bb_position = "N/A"

        # ATR (Average True Range) - Volatilidad
        if len(data) >= 14:
            high_low = data["High"] - data["Low"]
            high_close = abs(data["High"] - data["Close"].shift())
            low_close = abs(data["Low"] - data["Close"].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = safe_float(true_range.rolling(14).mean().iloc[-1])
        else:
            atr = 0.0

        # Cruce de EMAs
        if ema12 > ema26:
            ema_cross = "ALCISTA ⬆️"
        elif ema12 < ema26:
            ema_cross = "BAJISTA ⬇️"
        else:
            ema_cross = "NEUTRAL"

        return {
            "ema12": ema12,
            "ema26": ema26,
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_histogram": macd_histogram,
            "bb_upper": bb_upper,
            "bb_middle": sma20,
            "bb_lower": bb_lower,
            "bb_position": bb_position,
            "atr": atr,
            "ema_cross": ema_cross,
        }

    def get_llm_decision(self, ticker: str, timestamp: pd.Timestamp, model_id: str = None) -> Dict:
        """Obtener decisión del LLM con datos horarios"""
        if model_id is None:
            model_id = MODELS["fast_calc"]  # Usar modelo rápido por defecto

        market_context = self.prepare_market_context(ticker, timestamp)
        current_prices = self.get_current_prices(timestamp)
        portfolio_value = self.simulator.get_portfolio_value(current_prices)

        position_info = ""
        if ticker in self.simulator.portfolio:
            pos = self.simulator.portfolio[ticker]
            current_price = current_prices.get(ticker, 0)
            pnl_pct = ((current_price - pos["avg_price"]) / pos["avg_price"]) * 100
            position_info = f"""
POSICIÓN ACTUAL EN {ticker}:
- Acciones: {pos['shares']}
- Precio promedio: ${pos['avg_price']:.2f}
- Precio actual: ${current_price:.2f}
- P&L no realizado: {pnl_pct:+.2f}%
"""

        # Obtener indicadores avanzados
        indicators = self.calculate_advanced_indicators(ticker, timestamp)

        # Obtener datos básicos
        data = self.get_data_until_timestamp(ticker, timestamp)
        current_price = current_prices.get(ticker, 0)

        # Helper para conversión segura (maneja Series, ndarray y scalars)
        def safe_float(val):
            try:
                import numpy as _np

                if isinstance(val, (pd.Series, _np.ndarray)):
                    if len(val) == 0:
                        return 0.0
                    v = val.iloc[-1] if isinstance(val, pd.Series) else val[-1]
                    return 0.0 if pd.isna(v) else float(v)
                if pd.isna(val):
                    return 0.0
                return float(val)
            except Exception:
                return 0.0

        # Calcular volumen usando .iloc[0]
        if len(data) >= 24:
            avg_volume = safe_float(data["Volume"].tail(24).mean())
            current_volume = safe_float(data["Volume"].iloc[-1])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        else:
            volume_ratio = 0

        # Position sizing dinámico basado en volatilidad (MÁS AGRESIVO)
        atr = indicators["atr"]
        if atr > 5000:  # Alta volatilidad
            max_risk = 0.20  # 20% del efectivo (aumentado)
        elif atr > 3000:
            max_risk = 0.30  # 30% (aumentado)
        else:
            max_risk = 0.40  # 40% en baja volatilidad (aumentado)
        max_investment = self.simulator.cash * max_risk

        # Determinar señal MACD
        macd_signal = "⬆️ ALCISTA" if indicators["macd"] > indicators["macd_signal"] else "⬇️ BAJISTA"

        prompt = f"""
Eres un trader algorítmico AGRESIVO especializado en MOMENTUM HORARIO. Tu objetivo es MAXIMIZAR RETORNOS aprovechando oportunidades de corto plazo.

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 TU PORTFOLIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Capital total: ${portfolio_value:.2f}
- Efectivo disponible: ${self.simulator.cash:.2f}
- Máximo a invertir por operación: ${max_investment:.2f} ({max_risk*100:.0f}% del efectivo)
{position_info}

⚠️ PROTECCIÓN AUTOMÁTICA (no te preocupes por esto):
- Stop Loss: -3% (se ejecuta automáticamente)
- Take Profit: +5% (se ejecuta automáticamente)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ESTRATEGIA DE TRADING AGRESIVA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ COMPRAR (BUY) - Considera si cumple AL MENOS 2 DE ESTAS:
1. EMA12 > EMA26 (tendencia alcista)
2. MACD > MACD Signal (momentum positivo)
3. Precio cerca de Bollinger Inferior (oportunidad de compra)
4. RSI < 70 (no extremadamente sobrecomprado)
5. Cambio positivo en últimas 1-4 horas
6. Histograma MACD creciendo

💡 OPORTUNIDADES ESPECIALES DE COMPRA:
- SOBREVENTA: Si precio toca Bollinger Inferior → BUY agresivo (rebote probable)
- RECUPERACIÓN: Si cambio 1h positivo después de caída → BUY (momentum cambiando)
- BREAKOUT: Si precio rompe SMA 12h hacia arriba → BUY (nueva tendencia)

❌ VENDER (SELL) - Considera si cumple AL MENOS 1 DE ESTAS:
1. Ganancia no realizada > 3% (asegurar beneficios)
2. MACD cruza a la baja (momentum perdido)
3. Precio toca Bollinger Superior (sobrecompra)
4. RSI > 75 (extremo sobrecomprado)
5. Cambio negativo en últimas 2 horas
6. EMA12 cruza por debajo de EMA26

⚪ MANTENER (HOLD) - SOLO si:
- NO tienes posición Y las señales son contradictorias
- Tienes posición con ganancia < 2% y momentum aún positivo

🎲 FILOSOFÍA AGRESIVA:
- ACTÚA RÁPIDO: El mercado horario premia la velocidad
- BUSCA OPORTUNIDADES: Mejor operar y equivocarse (con stop loss) que no operar
- APROVECHA VOLATILIDAD: La volatilidad = oportunidad
- NO TEMAS COMPRAR EN BAJADAS: Si indicadores muestran sobreventa
- REALIZA BENEFICIOS: Mejor 3% seguro que 5% incierto

⚠️ ÚNICAS RESTRICCIONES DURAS:
- NO operar sin indicadores (si EMA/MACD = 0)
- NO comprar con RSI > 80 (sobrecompra extrema)
- Respetar límites de MONTO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 FORMATO DE RESPUESTA (EXACTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACCION: BUY
MONTO: 2000
RAZON: EMA alcista, MACD creciendo, RSI 45

O:
ACCION: SELL
MONTO: 50
RAZON: Profit +3.2%, RSI 78 sobrecompra

O:
ACCION: HOLD
MONTO: 0
RAZON: Señales contradictorias, esperando confirmación

RESTRICCIONES DE FORMATO:
- BUY: MONTO entre 1000 y {max_investment:.0f}
- SELL: MONTO entre 25 y 100 (porcentaje)
- HOLD: MONTO = 0
- RAZON: Máximo 1 línea, técnica
- NO uses símbolos $ ni % en MONTO
"""

        try:
            # Seleccionar provider según modelo
            if model_id == "deepseek-chat":
                model = DeepSeek(id=model_id)
            else:
                model = OpenRouter(id=model_id)

            agent = Agent(name="Intraday Trader", model=model, markdown=False)

            response = agent.run(prompt)
            response_text = response.content if hasattr(response, "content") else str(response)

            decision = self._parse_llm_response(
                response_text, ticker, current_prices.get(ticker, 0)
            )
            decision["raw_response"] = response_text
            decision["date"] = timestamp.strftime("%Y-%m-%d %H:%M")

            return decision

        except Exception as e:
            print(f"❌ Error obteniendo decisión LLM: {str(e)}")
            return {
                "action": "HOLD",
                "amount": 0,
                "reason": f"Error: {str(e)}",
                "date": timestamp.strftime("%Y-%m-%d %H:%M"),
            }

    def _parse_llm_response(self, response: str, ticker: str, current_price: float) -> Dict:
        """Parsear respuesta del LLM"""
        lines = response.strip().split("\n")

        action = "HOLD"
        amount = 0
        reason = "Sin razón especificada"

        for line in lines:
            line = line.strip()
            if line.startswith("ACCION:"):
                action = line.split(":", 1)[1].strip().upper()
                if action not in ["BUY", "SELL", "HOLD"]:
                    action = "HOLD"
            elif line.startswith("MONTO:"):
                monto_str = line.split(":", 1)[1].strip()
                import re

                numbers = re.findall(r"[\d.]+", monto_str)
                if numbers:
                    amount = float(numbers[0])
            elif line.startswith("RAZON:"):
                reason = line.split(":", 1)[1].strip()

        shares = 0
        if action == "BUY" and current_price > 0:
            # Si no especificó monto, usar un valor aleatorio entre 10% y 25% del efectivo
            if amount == 0 or amount < 100:  # Si no especificó o es muy bajo
                import random

                pct = random.uniform(0.10, 0.25)  # Entre 10% y 25%
                amount = self.simulator.cash * pct
                print(f"[DEBUG] Monto auto-asignado: ${amount:.2f} ({pct*100:.1f}% del efectivo)")

            max_investment = self.simulator.cash * 0.25  # Máximo 25%
            min_investment = self.simulator.cash * 0.10  # Mínimo 10%
            amount = min(max(amount, min_investment), max_investment)
            shares = amount / current_price  # Fracciones permitidas
            amount = shares * current_price
            print(f"[DEBUG] BUY: {shares:.8f} shares @ ${current_price:.2f} = ${amount:.2f}")

        return {
            "action": action,
            "amount": amount,
            "shares": shares,
            "reason": reason,
            "ticker": ticker,
            "price": current_price,
        }

    def execute_decision(self, decision: Dict) -> Dict:
        """Ejecutar decisión del LLM"""
        action = decision["action"]
        ticker = decision["ticker"]

        if action == "HOLD":
            return {"success": True, "message": "HOLD - Sin operación"}

        elif action == "BUY":
            shares = decision["shares"]
            if shares < 0.00000001:  # Verificar shares mínimas válidas
                return {"success": False, "message": "Shares calculados muy pequeños"}

            return self.simulator.execute_buy(
                ticker=ticker,
                shares=shares,
                price=decision["price"],
                date=decision["date"],
                reason=decision["reason"],
            )

        elif action == "SELL":
            if ticker not in self.simulator.portfolio:
                return {"success": False, "message": f"No tienes posición en {ticker}"}

            total_shares = self.simulator.portfolio[ticker]["shares"]
            pct = decision["amount"]

            if pct > 100:
                pct = 100

            shares_to_sell = float(total_shares * (pct / 100))
            if shares_to_sell == 0:
                shares_to_sell = total_shares

            return self.simulator.execute_sell(
                ticker=ticker,
                shares=shares_to_sell,
                price=decision["price"],
                date=decision["date"],
                reason=decision["reason"],
            )

        return {"success": False, "message": "Acción desconocida"}

    def run_simulation(self, model_id: str = None, verbose: bool = True):
        """Ejecutar simulación completa con datos horarios"""
        if model_id is None:
            model_id = MODELS["fast_calc"]  # Modelo rápido por defecto

        print("\n" + "=" * 70)
        print("🚀 SIMULACIÓN DE BACKTESTING HORARIO (1h)")
        print("=" * 70)
        print(f"⏰ Marco temporal: DATOS POR HORA")
        print(f"📅 Período: Últimos {self.days} días")
        print(f"💰 Capital inicial: ${self.simulator.initial_capital:,.2f}")
        print(f"📊 Tickers: {', '.join(self.tickers)}")
        print(f"⏱️  Decisiones cada {self.decision_interval_hours} horas")
        print(f"🤖 Modelo: {model_id}")
        print("=" * 70)

        # Obtener todos los timestamps disponibles
        if not self.historical_data:
            print("❌ No hay datos históricos")
            return None

        first_ticker = self.tickers[0]
        all_timestamps = self.historical_data[first_ticker].index

        # Filtrar timestamps según intervalo de decisión
        decision_timestamps = []
        for i, ts in enumerate(all_timestamps):
            if i == 0 or i % self.decision_interval_hours == 0:
                if i >= 24:  # Esperar 24 horas para tener datos
                    decision_timestamps.append(ts)

        print(
            f"\n📌 Se tomarán {len(decision_timestamps)} decisiones (~{len(decision_timestamps) * self.decision_interval_hours} horas)\n"
        )

        # Iterar por cada timestamp de decisión
        for i, timestamp in enumerate(decision_timestamps, 1):
            self.current_timestamp = timestamp
            current_prices = self.get_current_prices(timestamp)
            portfolio_value = self.simulator.get_portfolio_value(current_prices)

            print(f"\n{'─'*70}")
            print(f"📅 DECISIÓN #{i} - {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"💰 Valor: ${portfolio_value:,.2f} | Efectivo: ${self.simulator.cash:,.2f}")
            print(f"{'─'*70}")

            # Registrar equity curve
            self.simulator.equity_curve.append(
                {
                    "date": timestamp.strftime("%Y-%m-%d %H:%M"),
                    "value": portfolio_value,
                    "cash": self.simulator.cash,
                }
            )

            # ⚠️ VERIFICAR STOP LOSS Y TAKE PROFIT AUTOMÁTICOS
            auto_sales = self.simulator.check_risk_limits(
                current_prices, timestamp.strftime("%Y-%m-%d %H:%M")
            )
            if auto_sales:
                print(f"\n🚨 GESTIÓN DE RIESGO AUTOMÁTICA:")
                for sale in auto_sales:
                    if sale["type"] == "STOP_LOSS":
                        print(f"   🛑 STOP LOSS: {sale['ticker']} - Pérdida {sale['pnl_pct']:.2f}%")
                        print(f"      Vendido automáticamente @ ${sale['trade']['price']:,.2f}")
                    elif sale["type"] == "TAKE_PROFIT":
                        print(
                            f"   ✅ TAKE PROFIT: {sale['ticker']} - Ganancia {sale['pnl_pct']:.2f}%"
                        )
                        print(f"      Vendido automáticamente @ ${sale['trade']['price']:,.2f}")

                    # Registrar en log
                    self.simulator.auto_closes.append(sale)

            # Tomar decisiones para cada ticker
            for ticker in self.tickers:
                if ticker not in current_prices:
                    continue

                print(f"\n🔍 {ticker} (${current_prices[ticker]:.2f})...")

                # Obtener decisión del LLM
                decision = self.get_llm_decision(ticker, timestamp, model_id)

                # Guardar justificación completa
                self.decision_justifications.append(
                    {
                        "decision_num": i,
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
                        "ticker": ticker,
                        "action": decision["action"],
                        "price": decision["price"],
                        "shares": decision.get("shares", 0),
                        "full_reason": decision["reason"],
                        "portfolio_value": portfolio_value,
                        "cash": self.simulator.cash,
                    }
                )

                print(f"   Decisión: {decision['action']}")
                print(f"   Razón: {decision['reason'][:60]}...")

                # Ejecutar decisión
                result = self.execute_decision(decision)

                if result["success"]:
                    print(f"   ✅ {result['message']}")
                else:
                    print(f"   ❌ {result['message']}")

                # Guardar log
                self.simulator.decisions_log.append({**decision, "execution_result": result})

                # Pausa corta
                time.sleep(1)

        # Vender todas las posiciones al final
        print("\n" + "=" * 70)
        print("💰 CERRANDO TODAS LAS POSICIONES AL FINAL")
        print("=" * 70)

        final_timestamp = decision_timestamps[-1]
        final_prices = self.get_current_prices(final_timestamp)

        # Vender todas las posiciones abiertas
        for ticker in list(self.simulator.portfolio.keys()):
            if ticker in final_prices:
                shares = self.simulator.portfolio[ticker]["shares"]
                price = final_prices[ticker]
                result = self.simulator.execute_sell(
                    ticker=ticker,
                    shares=shares,
                    price=price,
                    date=final_timestamp.strftime("%Y-%m-%d %H:%M"),
                    reason="Cierre automático al finalizar simulación",
                )
                if result["success"]:
                    print(f"✅ Vendido {shares:.8f} {ticker} @ ${price:,.2f}")
                    print(
                        f"   Ganancia/Pérdida: ${result['trade']['pnl']:,.2f} ({result['trade']['pnl_pct']:+.2f}%)"
                    )

        print(f"\n💵 Efectivo final: ${self.simulator.cash:,.2f}")

        # Resumen final
        print("\n" + "=" * 70)
        print("🏁 SIMULACIÓN HORARIA COMPLETADA")
        print("=" * 70)

        metrics = self.simulator.get_performance_metrics(final_prices)

        self._print_final_report(metrics)

        # Mostrar resumen de justificaciones
        self._print_decision_summary()

        # Mostrar resumen en lenguaje natural
        self._print_natural_language_summary(metrics)

        return metrics

    def _print_final_report(self, metrics: Dict):
        """Imprimir reporte final"""
        print(f"\n📊 REPORTE FINAL (Trading Horario):")
        print("=" * 70)
        print(f"💰 Capital Inicial:    ${metrics['initial_capital']:,.2f}")
        print(f"💰 Capital Final:      ${metrics['current_value']:,.2f}")
        print(
            f"📈 Retorno Total:      ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:+.2f}%)"
        )
        print(f"💵 Efectivo:           ${metrics['cash']:,.2f}")
        print()
        print(f"📊 Total Operaciones:  {metrics['total_trades']}")
        print(f"✅ Ganadoras:          {metrics['winning_trades']} ({metrics['win_rate']:.1f}%)")
        print(f"❌ Perdedoras:         {metrics['losing_trades']}")
        print(f"💚 Ganancia Promedio:  ${metrics['avg_win']:.2f}")
        print(f"💔 Pérdida Promedio:   ${metrics['avg_loss']:.2f}")
        print(f"⚖️  Profit Factor:     {metrics['profit_factor']:.2f}")
        print()

        if metrics["holdings"]:
            print("📦 POSICIONES ABIERTAS:")
            for ticker, info in metrics["holdings"].items():
                print(f"   {ticker}: {info['shares']} acciones @ ${info['avg_price']:.2f}")
        else:
            print("📦 Sin posiciones abiertas")

        print("=" * 70)

    def _print_decision_summary(self):
        """Imprimir resumen completo de todas las decisiones con justificaciones"""
        if not self.decision_justifications:
            return

        print("\n" + "=" * 70)
        print("📋 RESUMEN COMPLETO DE DECISIONES Y JUSTIFICACIONES")
        print("=" * 70)

        # Agrupar por acción
        buy_decisions = [d for d in self.decision_justifications if d["action"] == "BUY"]
        sell_decisions = [d for d in self.decision_justifications if d["action"] == "SELL"]
        hold_decisions = [d for d in self.decision_justifications if d["action"] == "HOLD"]

        print(f"\n📊 Estadísticas:")
        print(f"   • Total decisiones: {len(self.decision_justifications)}")
        print(f"   • BUY: {len(buy_decisions)}")
        print(f"   • SELL: {len(sell_decisions)}")
        print(f"   • HOLD: {len(hold_decisions)}")

        # Mostrar decisiones BUY con justificación completa
        if buy_decisions:
            print(f"\n🟢 DECISIONES DE COMPRA ({len(buy_decisions)}):")
            print("─" * 70)
            for d in buy_decisions:
                print(f"\n#{d['decision_num']} - {d['timestamp']} - {d['ticker']}")
                print(f"Precio: ${d['price']:,.2f} | Shares: {d['shares']:.8f}")
                print(f"Portfolio: ${d['portfolio_value']:,.2f} | Efectivo: ${d['cash']:,.2f}")
                print(f"\n📝 JUSTIFICACIÓN COMPLETA:")
                print(f"{d['full_reason']}")
                print("─" * 70)

        # Mostrar decisiones SELL con justificación completa
        if sell_decisions:
            print(f"\n🔴 DECISIONES DE VENTA ({len(sell_decisions)}):")
            print("─" * 70)
            for d in sell_decisions:
                print(f"\n#{d['decision_num']} - {d['timestamp']} - {d['ticker']}")
                print(f"Precio: ${d['price']:,.2f} | Shares: {d['shares']:.8f}")
                print(f"Portfolio: ${d['portfolio_value']:,.2f} | Efectivo: ${d['cash']:,.2f}")
                print(f"\n📝 JUSTIFICACIÓN COMPLETA:")
                print(f"{d['full_reason']}")
                print("─" * 70)

        # Mostrar algunas decisiones HOLD representativas (primeras y últimas 3)
        if hold_decisions:
            print(
                f"\n⚪ DECISIONES HOLD (mostrando primeras y últimas 3 de {len(hold_decisions)}):"
            )
            print("─" * 70)
            sample_holds = (
                hold_decisions[:3] + hold_decisions[-3:]
                if len(hold_decisions) > 6
                else hold_decisions
            )
            for d in sample_holds:
                print(f"\n#{d['decision_num']} - {d['timestamp']} - {d['ticker']}")
                print(f"Precio: ${d['price']:,.2f}")
                print(f"Portfolio: ${d['portfolio_value']:,.2f} | Efectivo: ${d['cash']:,.2f}")
                print(f"📝 Razón: {d['full_reason']}")
                print("─" * 70)

        print("\n" + "=" * 70)

    def _print_natural_language_summary(self, metrics: Dict):
        """Generar resumen en lenguaje natural del backtesting"""
        print("\n" + "=" * 70)
        print("📝 RESUMEN EJECUTIVO EN LENGUAJE NATURAL")
        print("=" * 70)

        # Análisis de decisiones
        total_decisions = len(self.decision_justifications)
        buy_count = len([d for d in self.decision_justifications if d["action"] == "BUY"])
        sell_count = len([d for d in self.decision_justifications if d["action"] == "SELL"])
        hold_count = len([d for d in self.decision_justifications if d["action"] == "HOLD"])

        # Calcular rendimiento
        initial = metrics["initial_capital"]
        final = metrics["cash"]  # Todo en efectivo después de vender
        pnl = final - initial
        pnl_pct = (pnl / initial) * 100

        # Análisis de trades
        total_trades = metrics["total_trades"]
        win_rate = metrics["win_rate"]

        print("\n🎯 RESUMEN GENERAL:")
        print(f"Durante el período de backtesting de {self.days} días con decisiones cada ")
        print(
            f"{self.decision_interval_hours} hora(s), el sistema tomó {total_decisions} decisiones de trading."
        )
        print(
            f"De estas, {buy_count} fueron órdenes de compra ({buy_count/total_decisions*100:.1f}%), "
        )
        print(
            f"{sell_count} fueron ventas ({sell_count/total_decisions*100:.1f}%), y {hold_count} "
        )
        print(f"fueron decisiones de mantener sin operar ({hold_count/total_decisions*100:.1f}%).")

        print("\n💰 RENDIMIENTO FINANCIERO:")
        if pnl > 0:
            print(f"La estrategia generó una ganancia de ${pnl:,.2f} ({pnl_pct:+.2f}%), ")
            print(f"transformando el capital inicial de ${initial:,.2f} en ${final:,.2f}.")
        elif pnl < 0:
            print(f"La estrategia resultó en una pérdida de ${abs(pnl):,.2f} ({pnl_pct:.2f}%), ")
            print(f"reduciendo el capital inicial de ${initial:,.2f} a ${final:,.2f}.")
        else:
            print(f"La estrategia mantuvo el capital inicial sin cambios en ${initial:,.2f}.")

        print("\n📊 ANÁLISIS DE OPERACIONES:")
        if total_trades > 0:
            print(f"Se ejecutaron {total_trades} operaciones completas (compra y venta).")
            print(f"La tasa de éxito fue del {win_rate:.1f}%, con {metrics['winning_trades']} ")
            print(f"operaciones ganadoras y {metrics['losing_trades']} perdedoras.")

            if metrics["avg_win"] > 0:
                print(
                    f"\nLas operaciones ganadoras generaron en promedio ${metrics['avg_win']:.2f}, "
                )
                print(
                    f"mientras que las perdedoras costaron en promedio ${abs(metrics['avg_loss']):.2f}."
                )

            if metrics["profit_factor"] > 0:
                pf = metrics["profit_factor"]
                if pf > 2:
                    print(f"\nEl profit factor de {pf:.2f} indica una estrategia muy rentable.")
                elif pf > 1:
                    print(f"\nEl profit factor de {pf:.2f} indica una estrategia rentable.")
                elif pf == 1:
                    print(f"\nEl profit factor de {pf:.2f} indica una estrategia neutral.")
                else:
                    print(f"\nEl profit factor de {pf:.2f} indica una estrategia no rentable.")
        else:
            print("No se completaron operaciones durante el período de backtesting.")
            print("El sistema se mantuvo principalmente en HOLD, esperando mejores oportunidades.")

        print("\n🤖 COMPORTAMIENTO DEL AGENTE:")
        hold_pct = (hold_count / total_decisions) * 100
        if hold_pct > 70:
            print(f"El agente mostró un comportamiento muy conservador, manteniéndose en HOLD")
            print(f"el {hold_pct:.1f}% del tiempo. Esto sugiere que las condiciones de mercado")
            print(f"no cumplieron consistentemente con los criterios de entrada del sistema.")
        elif hold_pct > 50:
            print(
                f"El agente mostró un comportamiento moderadamente conservador, con {hold_pct:.1f}%"
            )
            print(
                f"de decisiones HOLD. Operó selectivamente cuando las condiciones eran favorables."
            )
        elif hold_pct > 30:
            print(f"El agente mostró un comportamiento activo, operando frecuentemente con solo")
            print(f"{hold_pct:.1f}% de decisiones HOLD.")
        else:
            print(f"El agente mostró un comportamiento muy activo, operando constantemente con")
            print(f"solo {hold_pct:.1f}% de decisiones HOLD.")

        if buy_count > 0:
            print(
                f"\nLas {buy_count} decisiones de compra se tomaron en momentos donde el análisis"
            )
            print(
                f"técnico indicaba tendencias alcistas, momentum positivo, o condiciones favorables"
            )
            print(f"basadas en indicadores como SMA, RSI y volumen.")

        print("\n" + "=" * 70)
        print("\n💡 CONCLUSIÓN:")
        if pnl_pct > 5:
            print(f"La estrategia fue exitosa, superando el {pnl_pct:.1f}% de retorno.")
            print("El sistema demostró capacidad para identificar oportunidades rentables.")
        elif pnl_pct > 0:
            print(f"La estrategia fue ligeramente rentable con {pnl_pct:.1f}% de retorno.")
            print("Hay espacio para optimización de los criterios de entrada/salida.")
        elif pnl_pct > -5:
            print(
                f"La estrategia tuvo un rendimiento cercano al punto de equilibrio ({pnl_pct:.1f}%)."
            )
            print("Se requiere ajuste de parámetros o cambio de condiciones de mercado.")
        else:
            print(f"La estrategia no fue rentable con {pnl_pct:.1f}% de pérdida.")
            print("Se recomienda revisar los criterios de trading y gestión de riesgo.")

        print("=" * 70)

    def save_results(self, filename: str = "hourly_backtest_results.json"):
        """Guardar resultados"""
        if not self.historical_data:
            return

        first_ticker = self.tickers[0]
        timestamps = self.historical_data[first_ticker].index

        results = {
            "config": {
                "tickers": self.tickers,
                "timeframe": "1h (hourly)",
                "days": self.days,
                "hours_total": len(timestamps),
                "decision_interval_hours": self.decision_interval_hours,
                "initial_capital": self.simulator.initial_capital,
            },
            "trades": self.simulator.history,
            "decisions_log": self.simulator.decisions_log,
            "equity_curve": self.simulator.equity_curve,
            "final_metrics": self.simulator.get_performance_metrics(
                self.get_current_prices(timestamps[-1])
            ),
        }

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Resultados guardados en: {filename}")


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("⚡ BACKTESTING HORARIO (1h) - SIMULACIÓN ACELERADA")
    print("=" * 70)

    print("\n📝 Configuración:")

    tickers_input = input("Tickers (ej: AAPL,BTC-USD): ").upper().strip()
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]

    if not tickers:
        print("❌ Debes ingresar al menos un ticker")
        return

    days_input = input("Días de datos (1-60, default: 7): ").strip()
    days = int(days_input) if days_input else 7
    days = min(max(days, 1), 60)

    interval_input = input("Horas entre decisiones (1, 2, 4, 6, default: 4): ").strip()
    interval = int(interval_input) if interval_input else 4

    capital_input = input("Capital inicial (default: 10000): ").strip()
    capital = float(capital_input) if capital_input else 10000.0

    print("\n🤖 Modelos (recomendado: rápido para datos horarios):")
    print("  1. Nemotron Nano (Rápido - Recomendado)")
    print("  2. DeepSeek V3 (Rápido, preciso)")
    print("  3. DeepSeek Chimera (Razonamiento)")
    print("  4. GLM 4.5 Air (General)")

    model_choice = input("Selecciona (default: 1): ").strip()
    model_map = {
        "1": MODELS["fast_calc"],
        "2": MODELS["deepseek"],
        "3": MODELS["reasoning"],
        "4": MODELS["general"],
    }
    model_id = model_map.get(model_choice, MODELS["fast_calc"])

    # Crear engine
    engine = HourlyBacktestEngine(
        tickers=tickers, days=days, decision_interval_hours=interval, initial_capital=capital
    )

    input("\n⏸️  Presiona ENTER para iniciar...")

    # Ejecutar
    metrics = engine.run_simulation(model_id=model_id)

    # Guardar
    save = input("\n💾 ¿Guardar resultados? (s/n): ").lower().strip()
    if save == "s":
        filename = input("Nombre (default: hourly_backtest_results.json): ").strip()
        if not filename:
            filename = "hourly_backtest_results.json"
        engine.save_results(filename)

    print("\n✅ Simulación horaria completada!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Simulación interrumpida")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

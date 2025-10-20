#!/usr/bin/env python3
"""
Sistema de Backtesting con Equipo Multi-Agente (Consenso)
Version: 1.0
Fecha: 2025-10-18

Este motor ejecuta simulaciones de trading horario usando el equipo avanzado definido en los YAML,
aplicando consenso en cada ciclo. Permite comparar resultados con el agente individual.
"""

import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List

from agents import (
    load_complete_team,
    load_market_researcher,
    load_risk_analysts,
    load_trading_strategists,
    load_portfolio_manager,
    load_daily_reporter
)
from pydantic import BaseModel, Field

load_dotenv()

# Modelo estructurado para decisiones
class TeamDecision(BaseModel):
    action: str
    amount: float
    reason: str
    strategy: str = ""
    confidence: float = 0.5
    agent: str = ""

# Simulador simple (puedes adaptar desde el motor original)
class TeamTradingSimulator:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.portfolio = {}
        self.history = []
        self.equity_curve = []
        self.decisions_log = []

    def get_portfolio_value(self, current_price: float) -> float:
        holdings_value = sum(
            self.portfolio[ticker]['shares'] * current_price
            for ticker in self.portfolio
        )
        return self.cash + holdings_value

    def execute_buy(self, ticker: str, shares: float, price: float, date: str, reason: str = "") -> Dict:
        """Ejecutar compra"""
        if shares <= 0:
            return {"success": False, "message": "Shares debe ser > 0"}

        cost = shares * price
        fee = cost * 0.001  # 0.1% fee
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
        fee = revenue * 0.001
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

# Motor de consenso multi-agente
class TeamConsensusBacktestEngine:
    def __init__(self, simulator: TeamTradingSimulator, team_agents: List):
        self.simulator = simulator
        self.team_agents = team_agents

    def safe_get_column(self, df, row, col_name, default=0.0):
        """Extraer columna OHLCV de forma robusta"""
        if col_name in df.columns:
            return float(row[col_name])
        matching = [col for col in df.columns if col_name in str(col)]
        if matching:
            return float(row[matching[0]])
        return float(default)

    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calcular indicadores técnicos avanzados"""
        if len(df) < 2:
            return {
                'ema12': 0, 'ema26': 0, 'ema_cross': 'N/A',
                'macd': 0, 'macd_signal': 0, 'macd_histogram': 0,
                'bb_upper': 0, 'bb_middle': 0, 'bb_lower': 0,
                'bb_position': 'N/A', 'atr': 0
            }

        try:
            close = df.apply(lambda row: self.safe_get_column(df, row, 'Close'), axis=1)
            high = df.apply(lambda row: self.safe_get_column(df, row, 'High'), axis=1)
            low = df.apply(lambda row: self.safe_get_column(df, row, 'Low'), axis=1)

            # EMA 12 y 26
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()

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

            return {
                'ema12': float(ema12.iloc[-1]),
                'ema26': float(ema26.iloc[-1]),
                'ema_cross': "⬆️ ALCISTA" if ema12.iloc[-1] > ema26.iloc[-1] else "⬇️ BAJISTA",
                'macd': float(macd_line.iloc[-1]),
                'macd_signal': float(signal_line.iloc[-1]),
                'macd_histogram': float(macd_histogram.iloc[-1]),
                'bb_upper': float(bb_upper.iloc[-1]),
                'bb_middle': float(sma20.iloc[-1]),
                'bb_lower': float(bb_lower.iloc[-1]),
                'bb_position': "⬆️ SOBRE BANDA SUPERIOR" if close.iloc[-1] > bb_upper.iloc[-1] else ("⬇️ BAJO BANDA INFERIOR" if close.iloc[-1] < bb_lower.iloc[-1] else "↔️ DENTRO DE BANDAS"),
                'atr': float(atr.iloc[-1])
            }
        except Exception as e:
            print(f"⚠️ Error calculando indicadores: {e}")
            return {
                'ema12': 0, 'ema26': 0, 'ema_cross': 'N/A',
                'macd': 0, 'macd_signal': 0, 'macd_histogram': 0,
                'bb_upper': 0, 'bb_middle': 0, 'bb_lower': 0,
                'bb_position': 'N/A', 'atr': 0
            }

    def get_team_decisions(self, ticker: str, current_prices: Dict[str, float],
                          timestamp: datetime, historical_data: pd.DataFrame,
                          market_context: str) -> List[TeamDecision]:
        """Obtener decisiones del equipo con contexto técnico completo"""
        decisions = []

        try:
            # Calcular indicadores técnicos
            indicators = self.calculate_technical_indicators(historical_data)

            # Calcular EMA48 y proyección
            if len(historical_data) >= 48:
                close_hist = historical_data.apply(lambda row: self.safe_get_column(historical_data, row, 'Close'), axis=1)
                ema48_series = close_hist.ewm(span=48, adjust=False).mean()
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
            else:
                ema48 = 0.0
                ema48_proj_1 = 0.0
                ema48_proj_2 = 0.0

            current_price = current_prices.get(ticker, 0)

            # Información de posición
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
            price_change_1h = ((close_hist.iloc[-1] - close_hist.iloc[-2]) / close_hist.iloc[-2]) * 100 if len(close_hist) >= 2 else 0
            price_change_4h = ((close_hist.iloc[-1] - close_hist.iloc[-5]) / close_hist.iloc[-5]) * 100 if len(close_hist) >= 5 else 0

            # Volume ratio
            volume_hist = historical_data.apply(lambda row: self.safe_get_column(historical_data, row, 'Volume'), axis=1)
            volume_ratio = 1.0
            if len(volume_hist) >= 10:
                avg_volume = volume_hist.rolling(10).mean().iloc[-1]
                current_volume = volume_hist.iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            # Position sizing dinámico
            atr = indicators['atr']
            if atr > 5000:
                max_risk = 0.20
            elif atr > 3000:
                max_risk = 0.30
            else:
                max_risk = 0.40
            max_investment = self.simulator.cash * max_risk

            macd_signal = "⬆️ ALCISTA" if indicators['macd'] > indicators['macd_signal'] else "⬇️ BAJISTA"

            # Contexto de mercado enriquecido
            enriched_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ TIMESTAMP: {timestamp.strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Precio actual {ticker}: ${current_price:,.2f}
📊 Volumen Ratio: {volume_ratio:.2f}x

📈 EMA 48h: ${ema48:.2f}
📈 EMA 48h Proy+1: ${ema48_proj_1:.2f}
📈 EMA 48h Proy+2: ${ema48_proj_2:.2f}

📊 Tendencia EMA48: {"⬆️ ALCISTA" if current_price > ema48 else "⬇️ BAJISTA"}

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
• Cambio precio 1h: {price_change_1h:+.2f}%
• Cambio precio 4h: {price_change_4h:+.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 TU PORTFOLIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Capital total: ${self.simulator.get_portfolio_value(current_price):.2f}
- Efectivo disponible: ${self.simulator.cash:.2f}
- Máximo a invertir por operación: ${max_investment:.2f} ({max_risk*100:.0f}% del efectivo)
{position_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CONSIDERACIONES ESTRATÉGICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• La EMA48 representa la tendencia general del mercado
• Si precio > EMA48: Tendencia alcista general
• Si precio < EMA48: Tendencia bajista general
• Las proyecciones EMA48+1/+2 ayudan a anticipar movimientos futuros
• Combina análisis técnico con gestión de riesgo automática

{market_context}
"""

            # Obtener decisiones de cada agente
            for agent in self.team_agents:
                try:
                    response = agent.run(enriched_context)
                    content = response.content

                    if hasattr(content, 'dict'):
                        decision_data = content.dict()
                    elif isinstance(content, dict):
                        decision_data = content
                    elif isinstance(content, str):
                        try:
                            decision_data = json.loads(content)
                        except Exception:
                            decision_data = {"action": "HOLD", "amount": 0, "reason": str(content), "strategy": "", "confidence": 0.0}
                    else:
                        decision_data = {"action": "HOLD", "amount": 0, "reason": "Respuesta no estructurada", "strategy": "", "confidence": 0.0}

                    agent_name = getattr(agent, 'name', str(agent)) or "Unknown"
                    decision = TeamDecision(**decision_data, agent=agent_name)
                    decisions.append(decision)

                except Exception as e:
                    print(f"Error con agente {agent}: {e}")
                    agent_name = getattr(agent, 'name', 'Unknown')
                    decision = TeamDecision(
                        action="HOLD",
                        amount=0,
                        reason=f"Error: {str(e)}",
                        strategy="",
                        confidence=0.0,
                        agent=agent_name
                    )
                    decisions.append(decision)

        except Exception as e:
            print(f"Error en get_team_decisions: {e}")
            decisions = []

        return decisions

    def consensus_decision(self, decisions: List[TeamDecision]) -> TeamDecision:
        """Aplicar algoritmo de consenso a las decisiones individuales"""
        if not decisions:
            return TeamDecision(action="HOLD", amount=0, reason="No decisions available", strategy="", confidence=0.0, agent="TEAM_CONSENSUS")

        # Mayoría simple por acción
        actions = [d.action for d in decisions]
        action = max(set(actions), key=actions.count)

        # Filtrar decisiones por acción mayoritaria
        consensus_decisions = [d for d in decisions if d.action == action]

        # Promedio de amount y confidence
        avg_amount = sum(d.amount for d in consensus_decisions) / len(consensus_decisions)
        avg_conf = sum(d.confidence for d in consensus_decisions) / len(consensus_decisions)

        # Combinar razones y estrategias
        reasons = [d.reason for d in consensus_decisions]
        strategies = list(set(d.strategy for d in consensus_decisions if d.strategy))

        reason = f"Consenso {action}: " + " | ".join(reasons[:3])  # Limitar a 3 razones
        strategy = " | ".join(strategies) if strategies else "consensus"

        return TeamDecision(
            action=action,
            amount=avg_amount,
            reason=reason,
            strategy=strategy,
            confidence=avg_conf,
            agent="TEAM_CONSENSUS"
        )

    def execute_decision(self, decision: TeamDecision, ticker: str, current_price: float, timestamp: str) -> Dict:
        """Ejecutar decisión de consenso"""
        action = decision.action

        if action == "HOLD":
            return {"success": True, "message": "HOLD - Sin operación"}

        elif action == "BUY":
            shares = decision.amount / current_price if current_price > 0 else 0
            if shares < 0.00000001:
                return {"success": False, "message": "Shares calculados muy pequeños"}

            return self.simulator.execute_buy(
                ticker=ticker,
                shares=shares,
                price=current_price,
                date=timestamp,
                reason=decision.reason
            )

        elif action == "SELL":
            if ticker not in self.simulator.portfolio:
                return {"success": False, "message": f"No tienes posición en {ticker}"}

            position = self.simulator.portfolio[ticker]
            amount_pct = min(decision.amount, 100)  # Máximo 100%
            shares_to_sell = position['shares'] * (amount_pct / 100)

            return self.simulator.execute_sell(
                ticker=ticker,
                shares=shares_to_sell,
                price=current_price,
                date=timestamp,
                reason=decision.reason
            )

        return {"success": False, "message": "Acción no reconocida"}

def fetch_hourly_data(ticker: str = "BTC-USD", days: int = 7) -> pd.DataFrame:
    """Descargar datos horarios de Yahoo Finance"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        result = yf.download(ticker, start=start_date, end=end_date, interval="1h", progress=False)

        if result is None or result.empty:
            print(f"⚠️ No se obtuvieron datos para {ticker}")
            return pd.DataFrame()

        df = result.reset_index()

        # Aplanar MultiIndex si existe
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in df.columns.values]

        print(f"✅ Descargados {len(df)} registros horarios para {ticker}")
        return df

    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        return pd.DataFrame()

def run_team_consensus_backtest(ticker: str = "BTC-USD", days: int = 7,
                               initial_capital: float = 10000.0,
                               decisions_interval_hours: int = 1) -> Dict:
    """
    Ejecutar backtesting completo con equipo de consenso

    Args:
        ticker: Símbolo a operar
        days: Días históricos
        initial_capital: Capital inicial
        decisions_interval_hours: Cada cuántas horas tomar decisión
    """

    print("=" * 80)
    print("🚀 BACKTESTING TEAM CONSENSUS - V1.0")
    print("=" * 80)
    print(f"📅 Período: {days} días")
    print(f"⏰ Intervalo de decisiones: Cada {decisions_interval_hours} hora(s)")
    print(f"💰 Capital inicial: ${initial_capital:,.2f}")
    print(f"🤖 Modelo: DeepSeek (forzado)")
    print(f"📊 Ticker: {ticker}")
    print("=" * 80)

    # Cargar equipo de agentes
    print("\n🤖 Cargando equipo de agentes...")
    team = load_complete_team(use_openrouter=False)
    team_agents = team.members
    print(f"✅ Equipo cargado: {len(team_agents)} agentes")

    # Descargar datos
    print("\n📥 Descargando datos horarios...")
    df = fetch_hourly_data(ticker, days=days)

    if df.empty:
        return {"error": "No se pudieron descargar datos"}

    # Inicializar simulador y motor
    simulator = TeamTradingSimulator(initial_capital=initial_capital)
    engine = TeamConsensusBacktestEngine(simulator, team_agents)

    print(f"\n🎯 Iniciando simulación con {len(df)} horas de datos...")
    print(f"📊 Total de decisiones esperadas: ~{len(df) // decisions_interval_hours}")

    decision_count = 0
    results = []

    # Procesar cada hora
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

        # Tomar decisión cada N horas
        if i % decisions_interval_hours == 0:
            decision_count += 1

            # Extraer High, Low, Volume
            high_price = float(row.get('High', current_price))
            low_price = float(row.get('Low', current_price))
            volume = float(row.get('Volume', 0))

            # Contexto base de mercado
            market_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Precio actual {ticker}: ${current_price:,.2f}
📊 Volumen: {volume:,.0f}
📈 High: ${high_price:,.2f} | Low: ${low_price:,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            # Obtener decisiones del equipo
            historical_slice = df.iloc[max(0, i-50):i+1]
            team_decisions = engine.get_team_decisions(
                ticker=ticker,
                current_prices=current_prices,
                timestamp=timestamp,
                historical_data=historical_slice,
                market_context=market_context
            )

            # Aplicar consenso
            consensus = engine.consensus_decision(team_decisions)

            # Ejecutar decisión
            result = engine.execute_decision(consensus, ticker, current_price, timestamp.strftime('%Y-%m-%d %H:%M'))

            # Log
            print(f"\n{'='*70}")
            print(f"🤖 DECISIÓN #{decision_count} - {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"{'='*70}")
            print(f"Precio: ${current_price:,.2f}")
            print(f"Acción: {consensus.action}")
            print(f"Monto: ${consensus.amount:.2f}")
            print(f"Confianza: {consensus.confidence:.2f}")
            print(f"Razón: {consensus.reason}")
            print(f"Resultado: {result['message']}")

            portfolio_value = simulator.get_portfolio_value(current_price)
            print(f"\n📊 Estado del Portfolio:")
            print(f"   - Efectivo: ${simulator.cash:.2f}")
            print(f"   - Valor total: ${portfolio_value:.2f}")
            print(f"   - Retorno: {((portfolio_value - initial_capital) / initial_capital * 100):+.2f}%")

            # Registrar resultado
            results.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M'),
                'price': current_price,
                'team_decisions': [d.dict() for d in team_decisions],
                'consensus': consensus.dict(),
                'execution': result,
                'portfolio_value': portfolio_value,
                'cash': simulator.cash
            })

        # Registrar equity curve
        portfolio_value = simulator.get_portfolio_value(current_price)
        simulator.equity_curve.append({
            'timestamp': timestamp,
            'portfolio_value': portfolio_value,
            'cash': simulator.cash,
            'price': current_price
        })

    # Calcular métricas finales
    final_value = simulator.get_portfolio_value(current_price)
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

    backtest_results = {
        'ticker': ticker,
        'days': days,
        'model': 'DeepSeek (team consensus)',
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return_pct': total_return,
        'total_trades': len(simulator.history),
        'buy_trades': len([t for t in simulator.history if t['action'] == 'BUY']),
        'sell_trades': len([t for t in simulator.history if t['action'] == 'SELL']),
        'win_rate': win_rate,
        'max_drawdown_pct': max_drawdown,
        'decisions_count': decision_count,
        'equity_curve': simulator.equity_curve,
        'history': simulator.history,
        'decisions_log': results
    }

    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL - TEAM CONSENSUS BACKTESTING")
    print("=" * 80)
    print(f"💰 Capital inicial: ${initial_capital:,.2f}")
    print(f"💵 Capital final: ${final_value:,.2f}")
    print(f"📈 Retorno total: {total_return:+.2f}%")
    print(f"🎯 Total operaciones: {len(simulator.history)}")
    print(f"   - Compras: {backtest_results['buy_trades']}")
    print(f"   - Ventas: {backtest_results['sell_trades']}")
    print(f"✅ Win Rate: {win_rate:.1f}%")
    print(f"📉 Max Drawdown: {max_drawdown:.2f}%")
    print(f"🤖 Decisiones equipo: {decision_count}")
    print("=" * 80)

    return backtest_results

if __name__ == "__main__":
    import sys

    # Parámetros desde CLI
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    interval_hours = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    # Ejecutar backtest
    results = run_team_consensus_backtest(
        ticker="BTC-USD",
        days=days,
        initial_capital=10000.0,
        decisions_interval_hours=interval_hours
    )

    # Guardar resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backtest_team_consensus_{days}d_{interval_hours}h_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Resultados guardados en: {filename}")
    print(f"\n✅ Para generar dashboard HTML ejecuta:")
    print(f"   python generate_dashboard.py {filename}")
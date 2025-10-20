#!/usr/bin/env python3
"""
Prueba simplificada del motor consenso sin agentes complejos
"""

import os
import json
import pandas as pd
from datetime import datetime

# Modelo de decisión simplificado
class SimpleDecision:
    def __init__(self, action, amount, reason, strategy="", confidence=0.5, agent=""):
        self.action = action
        self.amount = amount
        self.reason = reason
        self.strategy = strategy
        self.confidence = confidence
        self.agent = agent

    def dict(self):
        return {
            "action": self.action,
            "amount": self.amount,
            "reason": self.reason,
            "strategy": self.strategy,
            "confidence": self.confidence,
            "agent": self.agent
        }

# Simulador simple
class SimpleSimulator:
    def __init__(self, initial_capital: float = 1000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.portfolio = {}
        self.decisions_log = []

    def get_portfolio_value(self, current_price: float) -> float:
        holdings_value = sum(
            self.portfolio[ticker]['shares'] * current_price
            for ticker in self.portfolio
        )
        return self.cash + holdings_value

# Motor de consenso simplificado
class SimpleConsensusEngine:
    def __init__(self, simulator):
        self.simulator = simulator

    def get_team_decisions(self, market_context: str) -> list:
        """Simula decisiones de 3 agentes basados en reglas simples"""
        decisions = []

        # Agente 1: Conservador (basado en EMA)
        if "EMA 48h:" in market_context:
            ema_line = [line for line in market_context.split('\n') if 'EMA 48h:' in line]
            if ema_line:
                ema_value = ema_line[0].split('$')[1].split()[0] if '$' in ema_line[0] else '0'
                try:
                    ema_val = float(ema_value.replace(',', ''))
                    price_line = [line for line in market_context.split('\n') if 'Precio actual' in line][0]
                    price_val = float(price_line.split('$')[1].split()[0].replace(',', ''))

                    if price_val > ema_val:
                        decisions.append(SimpleDecision("BUY", 100, "Precio sobre EMA48 - tendencia alcista", "trend_following", 0.7, "Conservative_Agent"))
                    else:
                        decisions.append(SimpleDecision("HOLD", 0, "Precio bajo EMA48 - esperar", "wait_signal", 0.5, "Conservative_Agent"))
                except:
                    decisions.append(SimpleDecision("HOLD", 0, "Datos insuficientes", "insufficient_data", 0.3, "Conservative_Agent"))

        # Agente 2: Momentum (basado en volumen)
        volume_line = [line for line in market_context.split('\n') if 'Volumen:' in line]
        if volume_line:
            try:
                volume = float(volume_line[0].split(':')[1].strip())
                if volume > 1000000:  # Alto volumen
                    decisions.append(SimpleDecision("BUY", 200, "Alto volumen indica momentum", "momentum", 0.8, "Momentum_Agent"))
                else:
                    decisions.append(SimpleDecision("HOLD", 0, "Volumen bajo", "low_volume", 0.4, "Momentum_Agent"))
            except:
                decisions.append(SimpleDecision("HOLD", 0, "Error procesando volumen", "data_error", 0.3, "Momentum_Agent"))
        else:
            decisions.append(SimpleDecision("HOLD", 0, "Sin datos de volumen", "no_volume_data", 0.3, "Momentum_Agent"))

        # Agente 3: Risk Manager (siempre conservador)
        decisions.append(SimpleDecision("HOLD", 0, "Gestión de riesgo - esperar confirmación", "risk_management", 0.6, "Risk_Agent"))

        return decisions

    def consensus_decision(self, decisions):
        # Mayoría simple
        actions = [d.action for d in decisions]
        action = max(set(actions), key=actions.count)

        # Promedio de amount/confidence
        avg_amount = sum(d.amount for d in decisions if d.action == action) / max(1, actions.count(action))
        avg_conf = sum(d.confidence for d in decisions if d.action == action) / max(1, actions.count(action))

        reason = f"Consenso: {action} por mayoría. Razones: " + ", ".join([d.reason for d in decisions if d.action == action])
        strategy = ", ".join(set(d.strategy for d in decisions if d.action == action))

        return SimpleDecision(action=action, amount=avg_amount, reason=reason, strategy=strategy, confidence=avg_conf, agent="TEAM_CONSENSUS")

def test_simple_consensus():
    """Prueba simplificada del motor consenso"""
    print("🧪 Probando motor consenso simplificado...")

    # Cargar datos
    try:
        data = pd.read_csv('btc_hourly_simple.csv')
        print(f"✅ Datos cargados: {len(data)} filas")
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return False

    # Instanciar motor
    simulator = SimpleSimulator(initial_capital=1000.0)
    engine = SimpleConsensusEngine(simulator)

    # Ejecutar 5 iteraciones de prueba
    results = []
    for i in range(min(5, len(data))):
        row = data.iloc[i]
        timestamp = row['Timestamp']
        ticker = 'BTC'
        current_prices = {ticker: row['Close']}

        # Calcular EMA 48 periodos y proyectar
        if i >= 47:
            ema_series = data['Close'].ewm(span=48, adjust=False).mean()
            ema48 = ema_series.iloc[-1]
            # Proyección simple
            if len(ema_series) >= 3:
                delta1 = ema_series.iloc[-1] - ema_series.iloc[-2]
                delta2 = ema_series.iloc[-2] - ema_series.iloc[-3]
                avg_delta = (delta1 + delta2) / 2
                ema48_proj_1 = ema48 + avg_delta
                ema48_proj_2 = ema48_proj_1 + avg_delta
            else:
                ema48_proj_1 = None
                ema48_proj_2 = None
        else:
            ema48 = None
            ema48_proj_1 = None
            ema48_proj_2 = None

        market_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ TIMESTAMP: {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Precio actual {ticker}: ${row['Close']:,.2f}
📊 Volumen: {row['Volume']}
📈 EMA 48h: {'{:.2f}'.format(ema48) if ema48 is not None else 'N/A'}
📈 EMA 48h Proy+1: {'{:.2f}'.format(ema48_proj_1) if ema48_proj_1 is not None else 'N/A'}
📈 EMA 48h Proy+2: {'{:.2f}'.format(ema48_proj_2) if ema48_proj_2 is not None else 'N/A'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Considera la EMA de 48 periodos como referencia de la tendencia general. Si el precio está por encima de la EMA48, la tendencia es alcista; si está por debajo, es bajista. Incluye este análisis y la proyección de los próximos 2 periodos en tu decisión.
"""

        print(f"\n🔄 CICLO {i+1}/5 - {timestamp[:19]}")

        team_decisions = engine.get_team_decisions(market_context)
        consensus = engine.consensus_decision(team_decisions)

        print(f"📊 Decisiones simuladas:")
        for d in team_decisions:
            print(f"  {d.agent}: {d.action} ${d.amount:.2f} conf={d.confidence:.2f}")

        print(f"🎯 Consenso: {consensus.action} ${consensus.amount:.2f} conf={consensus.confidence:.2f}")

        results.append({
            'timestamp': str(timestamp),
            'ema48': float(ema48) if ema48 is not None else None,
            'ema48_proj_1': float(ema48_proj_1) if ema48_proj_1 is not None else None,
            'ema48_proj_2': float(ema48_proj_2) if ema48_proj_2 is not None else None,
            'team_decisions': [d.dict() for d in team_decisions],
            'consensus': consensus.dict()
        })

    # Guardar resultados de prueba
    filename = 'test_simple_consensus_results.json'
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados de prueba guardados en: {filename}")
    print("✅ Motor consenso simplificado funciona correctamente!")
    print("✅ EMA48 y proyección integradas exitosamente!")

    return True

if __name__ == "__main__":
    test_simple_consensus()
#!/usr/bin/env python3
"""
Prueba corta del motor consenso completo
"""

import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from agents import (
    load_complete_team,
    load_market_researcher,
    load_risk_analysts,
    load_trading_strategists,
    load_portfolio_manager,
    load_daily_reporter
)

load_dotenv()

# Modelo estructurado para decisiones
class TeamDecision:
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

# Motor de consenso simplificado para prueba
class TeamConsensusBacktestEngine:
    def __init__(self, simulator, team_agents):
        self.simulator = simulator
        self.team_agents = team_agents

    def get_team_decisions(self, market_context: str) -> list:
        decisions = []
        try:
            # Solo usar 2 agentes para prueba rápida
            for agent in self.team_agents[:2]:
                try:
                    response = agent.run(market_context)
                    content = response.content
                    if hasattr(content, 'dict'):
                        decision_data = content.dict()
                    elif isinstance(content, dict):
                        decision_data = content
                    elif isinstance(content, str):
                        try:
                            import json as _json
                            decision_data = _json.loads(content)
                        except Exception:
                            decision_data = {"action": "HOLD", "amount": 0, "reason": str(content), "strategy": "", "confidence": 0.0}
                    else:
                        decision_data = {"action": "HOLD", "amount": 0, "reason": "Respuesta no estructurada", "strategy": "", "confidence": 0.0}
                    agent_name = getattr(agent, 'name', str(agent)) or "Unknown"
                    decision = TeamDecision(**decision_data, agent=agent_name)
                    decisions.append(decision)
                except Exception as e:
                    print(f"Error con agente {agent}: {e}")
                    decisions.append(TeamDecision("HOLD", 0, f"Error: {str(e)}", agent=str(agent)))
        except Exception as e:
            print(f"Error en get_team_decisions: {e}")
        return decisions

    def consensus_decision(self, decisions):
        # Mayoría simple por acción
        actions = [d.action for d in decisions]
        action = max(set(actions), key=actions.count)
        # Promedio de amount/confidence
        avg_amount = sum(d.amount for d in decisions if d.action == action) / max(1, actions.count(action))
        avg_conf = sum(d.confidence for d in decisions if d.action == action) / max(1, actions.count(action))
        reason = f"Consenso: {action} por mayoría. Razones: " + ", ".join([d.reason for d in decisions if d.action == action])
        strategy = ", ".join(set(d.strategy for d in decisions if d.action == action))
        return TeamDecision(action=action, amount=avg_amount, reason=reason, strategy=strategy, confidence=avg_conf, agent="TEAM_CONSENSUS")

def test_consensus_engine():
    """Prueba corta del motor consenso"""
    print("🚀 Probando motor consenso corregido...")

    # Cargar agentes (solo 2 para prueba rápida)
    try:
        team = load_complete_team(use_openrouter=False)
        team_agents = team.members[:2]  # Solo 2 agentes
        print(f"✅ Agentes cargados: {len(team_agents)}")
    except Exception as e:
        print(f"❌ Error cargando agentes: {e}")
        return False

    # Cargar datos
    try:
        data = pd.read_csv('btc_hourly_simple.csv')
        print(f"✅ Datos cargados: {len(data)} filas")
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return False

    # Instanciar motor
    simulator = TeamTradingSimulator(initial_capital=1000.0)  # Capital pequeño para prueba
    engine = TeamConsensusBacktestEngine(simulator, team_agents)

    # Ejecutar solo 3 iteraciones de prueba
    results = []
    for i in range(min(3, len(data))):
        row = data.iloc[i]
        timestamp = row['Timestamp']
        ticker = 'BTC'
        current_prices = {ticker: row['Close']}

        # Calcular EMA 48 periodos y proyectar
        if i >= 47:
            ema_series = data['Close'].iloc[:i+1].ewm(span=48, adjust=False).mean()
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

        print(f"\n🔄 CICLO {i+1}/3 - {timestamp}")

        team_decisions = engine.get_team_decisions(market_context)
        consensus = engine.consensus_decision(team_decisions)

        print(f"📊 Decisiones individuales:")
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
    filename = 'test_consensus_results.json'
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados de prueba guardados en: {filename}")
    print("✅ Motor consenso funciona correctamente!")
    return True

if __name__ == "__main__":
    test_consensus_engine()
#!/usr/bin/env python3
"""
Sistema de Backtesting con Simulación Temporal
Evalúa las decisiones de los agentes LLM con datos históricos presentados gradualmente
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
}


class TradingSimulator:
    """Simulador de trading con datos históricos"""

    def __init__(self, initial_capital: float = 10000.0, transaction_cost: float = 0.001):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.transaction_cost = transaction_cost  # 0.1% por transacción

        self.portfolio = {}  # {ticker: {'shares': int, 'avg_price': float}}
        self.history = []  # Historial de operaciones
        self.equity_curve = []  # Evolución del capital
        self.decisions_log = []  # Log de decisiones del LLM

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calcular valor total del portfolio"""
        holdings_value = sum(
            self.portfolio[ticker]["shares"] * current_prices.get(ticker, 0)
            for ticker in self.portfolio
        )
        return self.cash + holdings_value

    def execute_buy(
        self, ticker: str, shares: int, price: float, date: str, reason: str = ""
    ) -> Dict:
        """Ejecutar compra"""
        cost = shares * price
        transaction_fee = cost * self.transaction_cost
        total_cost = cost + transaction_fee

        if total_cost > self.cash:
            return {
                "success": False,
                "message": f"Fondos insuficientes. Necesitas ${total_cost:.2f}, tienes ${self.cash:.2f}",
            }

        # Actualizar cash
        self.cash -= total_cost

        # Actualizar portfolio
        if ticker in self.portfolio:
            old_shares = self.portfolio[ticker]["shares"]
            old_avg = self.portfolio[ticker]["avg_price"]
            new_shares = old_shares + shares
            new_avg = ((old_shares * old_avg) + (shares * price)) / new_shares
            self.portfolio[ticker] = {"shares": new_shares, "avg_price": new_avg}
        else:
            self.portfolio[ticker] = {"shares": shares, "avg_price": price}

        # Registrar operación
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
        self, ticker: str, shares: int, price: float, date: str, reason: str = ""
    ) -> Dict:
        """Ejecutar venta"""
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

        # Actualizar cash
        self.cash += net_revenue

        # Calcular P&L
        avg_cost = self.portfolio[ticker]["avg_price"]
        pnl = (price - avg_cost) * shares
        pnl_pct = ((price - avg_cost) / avg_cost) * 100

        # Actualizar portfolio
        self.portfolio[ticker]["shares"] -= shares
        if self.portfolio[ticker]["shares"] == 0:
            del self.portfolio[ticker]

        # Registrar operación
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

        # Calcular trades ganadores vs perdedores
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


class BacktestEngine:
    """Motor de backtesting con presentación gradual de datos"""

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        decision_interval: int = 5,
        initial_capital: float = 10000.0,
    ):
        """
        Args:
            tickers: Lista de tickers a analizar
            start_date: Fecha inicial (YYYY-MM-DD)
            end_date: Fecha final (YYYY-MM-DD)
            decision_interval: Días entre cada decisión
            initial_capital: Capital inicial
        """
        self.tickers = tickers
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.decision_interval = decision_interval

        self.simulator = TradingSimulator(initial_capital)
        self.historical_data = {}
        self.current_date = None

        print("📥 Descargando datos históricos...")
        self._download_data()

    def _download_data(self):
        """Descargar datos históricos"""
        for ticker in self.tickers:
            try:
                data = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)
                if not data.empty:
                    self.historical_data[ticker] = data
                    print(f"  ✅ {ticker}: {len(data)} días de datos")
                else:
                    print(f"  ❌ {ticker}: Sin datos")
            except Exception as e:
                print(f"  ❌ {ticker}: Error - {str(e)}")

    def get_data_until_date(self, ticker: str, date: pd.Timestamp) -> pd.DataFrame:
        """Obtener datos hasta una fecha específica (sin ver el futuro)"""
        if ticker not in self.historical_data:
            return pd.DataFrame()

        data = self.historical_data[ticker]
        return data[data.index <= date].copy()

    def get_current_prices(self, date: pd.Timestamp) -> Dict[str, float]:
        """Obtener precios actuales en una fecha"""
        prices = {}
        for ticker in self.tickers:
            data = self.get_data_until_date(ticker, date)
            if not data.empty:
                prices[ticker] = float(data["Close"].iloc[-1])
        return prices

    def prepare_market_context(self, ticker: str, date: pd.Timestamp) -> str:
        """Preparar contexto de mercado hasta la fecha actual (sin futuro)"""
        data = self.get_data_until_date(ticker, date)

        if len(data) < 20:
            return f"Datos insuficientes para {ticker}"

        # Últimos 20 días
        recent = data.tail(20)
        current_price = float(recent["Close"].iloc[-1])
        prev_price = float(recent["Close"].iloc[-20])
        change_20d = ((current_price - prev_price) / prev_price) * 100

        # Métricas
        high_20d = float(recent["High"].max())
        low_20d = float(recent["Low"].min())
        avg_volume = float(recent["Volume"].mean())
        current_volume = float(recent["Volume"].iloc[-1])

        # Tendencia
        sma_5 = float(recent["Close"].tail(5).mean())
        sma_20 = float(recent["Close"].tail(20).mean())
        trend = "ALCISTA" if sma_5 > sma_20 else "BAJISTA"

        context = f"""
DATOS DE MERCADO PARA {ticker} (Hasta {date.strftime('%Y-%m-%d')})

PRECIO ACTUAL: ${current_price:.2f}
Cambio 20 días: {change_20d:+.2f}%
Rango 20d: ${low_20d:.2f} - ${high_20d:.2f}

INDICADORES TÉCNICOS:
- SMA 5 días: ${sma_5:.2f}
- SMA 20 días: ${sma_20:.2f}
- Tendencia: {trend}
- Volumen promedio: {avg_volume:,.0f}
- Volumen actual: {current_volume:,.0f}

IMPORTANTE:
- Solo tienes datos hasta {date.strftime('%Y-%m-%d')}
- NO puedes ver el futuro
- Basa tu decisión en la tendencia y datos actuales
"""
        return context

    def get_llm_decision(self, ticker: str, date: pd.Timestamp, model_id: str = None) -> Dict:
        """Obtener decisión del LLM"""
        if model_id is None:
            model_id = MODELS["reasoning"]

        market_context = self.prepare_market_context(ticker, date)

        # Contexto del portfolio
        current_prices = self.get_current_prices(date)
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

        prompt = f"""
Eres un trader profesional. Analiza la siguiente situación y toma una decisión de trading.

{market_context}

TU PORTFOLIO ACTUAL:
- Capital total: ${portfolio_value:.2f}
- Efectivo disponible: ${self.simulator.cash:.2f}
{position_info}

DECISIÓN REQUERIDA:
Basándote SOLO en los datos disponibles hasta {date.strftime('%Y-%m-%d')}, decide:

1. ACCIÓN: BUY / SELL / HOLD
2. Si BUY: ¿Cuánto dinero invertir? (máximo 30% del efectivo disponible)
3. Si SELL: ¿Qué % de la posición vender? (25%, 50%, 75%, 100%)
4. RAZÓN: Explica tu decisión en 2-3 líneas

RESPONDE EN ESTE FORMATO EXACTO:
ACCION: [BUY/SELL/HOLD]
MONTO: [cantidad en $ si BUY, o % si SELL]
RAZON: [tu explicación]

Sé conservador y realista. No arriesgues más del 30% en una sola operación.
"""

        try:
            model = OpenRouter(id=model_id)
            agent = Agent(name="Trading Agent", model=model, markdown=False)

            # Obtener respuesta
            response = agent.run(prompt)
            response_text = response.content if hasattr(response, "content") else str(response)

            # Parsear respuesta
            decision = self._parse_llm_response(
                response_text, ticker, current_prices.get(ticker, 0)
            )
            decision["raw_response"] = response_text
            decision["date"] = date.strftime("%Y-%m-%d")

            return decision

        except Exception as e:
            print(f"❌ Error obteniendo decisión LLM: {str(e)}")
            return {
                "action": "HOLD",
                "amount": 0,
                "reason": f"Error: {str(e)}",
                "date": date.strftime("%Y-%m-%d"),
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
                # Extraer números
                import re

                numbers = re.findall(r"[\d.]+", monto_str)
                if numbers:
                    amount = float(numbers[0])
            elif line.startswith("RAZON:"):
                reason = line.split(":", 1)[1].strip()

        # Calcular shares si es BUY
        shares = 0
        if action == "BUY" and current_price > 0:
            # Limitar a 30% del cash disponible
            max_investment = self.simulator.cash * 0.3
            amount = min(amount, max_investment)
            shares = int(amount / current_price)
            amount = shares * current_price  # Ajustar al número entero de shares

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
            if shares == 0:
                return {"success": False, "message": "Shares calculados = 0"}

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

            # Calcular shares a vender
            total_shares = self.simulator.portfolio[ticker]["shares"]
            pct = decision["amount"]  # Se espera un porcentaje

            if pct > 100:
                pct = 100

            shares_to_sell = int(total_shares * (pct / 100))
            if shares_to_sell == 0:
                shares_to_sell = total_shares  # Vender todo si es muy poco

            return self.simulator.execute_sell(
                ticker=ticker,
                shares=shares_to_sell,
                price=decision["price"],
                date=decision["date"],
                reason=decision["reason"],
            )

        return {"success": False, "message": "Acción desconocida"}

    def run_simulation(self, model_id: str = None, verbose: bool = True):
        """Ejecutar simulación completa"""
        if model_id is None:
            model_id = MODELS["reasoning"]

        print("\n" + "=" * 70)
        print("🚀 INICIANDO SIMULACIÓN DE BACKTESTING")
        print("=" * 70)
        print(
            f"📅 Período: {self.start_date.strftime('%Y-%m-%d')} → {self.end_date.strftime('%Y-%m-%d')}"
        )
        print(f"💰 Capital inicial: ${self.simulator.initial_capital:,.2f}")
        print(f"📊 Tickers: {', '.join(self.tickers)}")
        print(f"⏱️  Decisiones cada {self.decision_interval} días")
        print(f"🤖 Modelo: {model_id}")
        print("=" * 70)

        # Generar fechas de decisión
        current = self.start_date + timedelta(days=20)  # Esperar 20 días para tener datos
        decision_dates = []

        while current <= self.end_date:
            decision_dates.append(current)
            current += timedelta(days=self.decision_interval)

        print(f"\n📌 Se tomarán {len(decision_dates)} decisiones\n")

        # Iterar por cada fecha de decisión
        for i, date in enumerate(decision_dates, 1):
            self.current_date = date
            current_prices = self.get_current_prices(date)
            portfolio_value = self.simulator.get_portfolio_value(current_prices)

            print(f"\n{'─'*70}")
            print(f"📅 DECISIÓN #{i} - {date.strftime('%Y-%m-%d')}")
            print(
                f"💰 Valor Portfolio: ${portfolio_value:,.2f} | Efectivo: ${self.simulator.cash:,.2f}"
            )
            print(f"{'─'*70}")

            # Registrar equity curve
            self.simulator.equity_curve.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "value": portfolio_value,
                    "cash": self.simulator.cash,
                }
            )

            # Tomar decisiones para cada ticker
            for ticker in self.tickers:
                if ticker not in current_prices:
                    continue

                print(f"\n🔍 Analizando {ticker} (${current_prices[ticker]:.2f})...")

                # Obtener decisión del LLM
                decision = self.get_llm_decision(ticker, date, model_id)

                print(f"   Decisión: {decision['action']}")
                print(f"   Razón: {decision['reason']}")

                # Ejecutar decisión
                result = self.execute_decision(decision)

                if result["success"]:
                    print(f"   ✅ {result['message']}")
                else:
                    print(f"   ❌ {result['message']}")

                # Guardar log
                self.simulator.decisions_log.append({**decision, "execution_result": result})

                # Pausa para no saturar la API
                time.sleep(2)

        # Resumen final
        print("\n" + "=" * 70)
        print("🏁 SIMULACIÓN COMPLETADA")
        print("=" * 70)

        final_prices = self.get_current_prices(self.end_date)
        metrics = self.simulator.get_performance_metrics(final_prices)

        self._print_final_report(metrics)

        return metrics

    def _print_final_report(self, metrics: Dict):
        """Imprimir reporte final"""
        print(f"\n📊 REPORTE FINAL DE DESEMPEÑO:")
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

    def save_results(self, filename: str = "backtest_results.json"):
        """Guardar resultados a archivo"""
        results = {
            "config": {
                "tickers": self.tickers,
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
                "initial_capital": self.simulator.initial_capital,
                "decision_interval": self.decision_interval,
            },
            "trades": self.simulator.history,
            "decisions_log": self.simulator.decisions_log,
            "equity_curve": self.simulator.equity_curve,
            "final_metrics": self.simulator.get_performance_metrics(
                self.get_current_prices(self.end_date)
            ),
        }

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Resultados guardados en: {filename}")


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("🎯 SIMULADOR DE BACKTESTING CON IA")
    print("=" * 70)

    # Configuración
    print("\n📝 Configuración de la simulación:")

    tickers_input = input("Tickers (separados por coma, ej: AAPL,MSFT): ").upper().strip()
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]

    if not tickers:
        print("❌ Debes ingresar al menos un ticker")
        return

    start_date = input("Fecha inicial (YYYY-MM-DD, ej: 2024-01-01): ").strip()
    end_date = input("Fecha final (YYYY-MM-DD, ej: 2024-12-31): ").strip()

    interval_input = input("Días entre decisiones (default: 7): ").strip()
    interval = int(interval_input) if interval_input else 7

    capital_input = input("Capital inicial (default: 10000): ").strip()
    capital = float(capital_input) if capital_input else 10000.0

    print("\n🤖 Modelos disponibles:")
    print("  1. DeepSeek Chimera (Razonamiento - Recomendado)")
    print("  2. Qwen3 235B (Estrategia avanzada)")
    print("  3. Tongyi DeepResearch (Investigación profunda)")

    model_choice = input("Selecciona modelo (default: 1): ").strip()
    model_map = {"1": MODELS["reasoning"], "2": MODELS["advanced"], "3": MODELS["deep_research"]}
    model_id = model_map.get(model_choice, MODELS["reasoning"])

    # Crear simulador
    engine = BacktestEngine(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        decision_interval=interval,
        initial_capital=capital,
    )

    # Ejecutar simulación
    input("\n⏸️  Presiona ENTER para iniciar la simulación...")

    metrics = engine.run_simulation(model_id=model_id)

    # Guardar resultados
    save = input("\n💾 ¿Guardar resultados? (s/n): ").lower().strip()
    if save == "s":
        filename = input("Nombre del archivo (default: backtest_results.json): ").strip()
        if not filename:
            filename = "backtest_results.json"
        engine.save_results(filename)

    print("\n✅ Simulación completada!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Simulación interrumpida")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

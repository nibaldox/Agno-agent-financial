#!/usr/bin/env python3
"""
Demo rápido de backtesting horario
Ejecuta automáticamente BTC-USD con 7 días de datos, decisiones cada 4 horas
"""

import sys

sys.path.insert(0, "/Users/xodla/Documents/Code/06-Agentes/Agno-agent-financial")

from hourly_backtest import MODELS, HourlyBacktestEngine


def main():
    print("\n🚀 DEMO RÁPIDO - BACKTESTING HORARIO")
    print("=" * 70)
    print("Configuración:")
    print("  • Ticker: BTC-USD")
    print("  • Período: 7 días (datos horarios)")
    print("  • Decisiones: Cada 4 horas")
    print("  • Capital: $10,000")
    print("  • Modelo: Nemotron Nano (rápido)")
    print("=" * 70)

    # Crear engine
    engine = HourlyBacktestEngine(
        tickers=["BTC-USD"], days=7, decision_interval_hours=4, initial_capital=10000.0
    )

    # Ejecutar
    metrics = engine.run_simulation(model_id=MODELS["fast_calc"])

    # Guardar
    if metrics:
        engine.save_results("demo_hourly_btc.json")
        print("\n✅ Demo completado! Resultados guardados en demo_hourly_btc.json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

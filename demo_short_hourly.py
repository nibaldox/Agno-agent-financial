#!/usr/bin/env python3
"""
Demo corto: 7 días, decisiones cada 6 horas para BTC
"""
import sys

sys.path.insert(0, "/Users/xodla/Documents/Code/06-Agentes/Agno-agent-financial")

from hourly_backtest import MODELS, HourlyBacktestEngine


def main():
    print("\n🚀 DEMO CORTO - BTC 7 días, decisiones cada 6h")
    print("=" * 70)

    engine = HourlyBacktestEngine(
        tickers=["BTC-USD"],
        days=7,
        decision_interval_hours=6,  # Solo ~28 decisiones
        initial_capital=10000.0,
    )

    print("\n⚡ Iniciando simulación...")
    metrics = engine.run_simulation(model_id=MODELS["fast_calc"])

    if metrics:
        engine.save_results("btc_7d_6h.json")
        print("\n✅ Resultados en: btc_7d_6h.json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

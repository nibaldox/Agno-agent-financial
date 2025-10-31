#!/usr/bin/env python3
"""
Backtesting automático: BTC-USD, 30 días, decisiones cada 4 horas con DeepSeek V3
"""
import sys

sys.path.insert(0, "/Users/xodla/Documents/Code/06-Agentes/Agno-agent-financial")

from hourly_backtest import MODELS, HourlyBacktestEngine


def main():
    # Configuración
    tickers = ["BTC-USD"]
    days = 60  # Período más extenso
    decision_interval_hours = 1  # Decisiones cada hora
    initial_capital = 10000.0

    print("\n" + "=" * 70)
    print("🚀 BACKTESTING AUTOMÁTICO - BTC CON DEEPSEEK V3")
    print("=" * 70)
    print("📊 Configuración:")
    print(f"  • Ticker: {tickers[0]}")
    print(f"  • Período: {days} días (datos horarios)")
    print(
        f"  • Decisiones: Cada {decision_interval_hours} hora(s) (~{(days*24)//decision_interval_hours} decisiones)"
    )
    print(f"  • Capital inicial: ${initial_capital:,.0f}")
    print("  • Modelo: DeepSeek V3 (rápido y preciso)")
    print("=" * 70)
    print("\n⏱️  Tiempo estimado: 1-2 horas (1,440 decisiones)\n")

    print("\n🚀 Iniciando simulación...\n")

    # Crear engine
    engine = HourlyBacktestEngine(tickers, days, decision_interval_hours, initial_capital)

    # Ejecutar con DeepSeek V3
    metrics = engine.run_simulation(model_id=MODELS["deepseek"])

    # Guardar resultados
    if metrics:
        filename = "btc_30d_4h_deepseek.json"
        engine.save_results(filename)
        print(f"\n✅ Resultados guardados en: {filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Simulación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

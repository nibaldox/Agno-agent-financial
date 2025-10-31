#!/usr/bin/env python3
"""
Demo del Sistema de Backtesting
Ejemplo simple y rápido para demostrar la funcionalidad
"""

import sys

from backtest_simulator import MODELS, BacktestEngine


def demo_simple():
    """Demo simple con AAPL - 1 mes"""
    print("\n" + "=" * 70)
    print("🎯 DEMO SIMPLE - Backtesting AAPL (1 mes)")
    print("=" * 70)
    print("\nEste demo:")
    print("  ✅ Descarga datos históricos de AAPL")
    print("  ✅ Simula 4 decisiones (1 por semana)")
    print("  ✅ Usa el modelo DeepSeek Chimera")
    print("  ✅ Capital inicial: $10,000")
    print("=" * 70)

    input("\n⏸️  Presiona ENTER para continuar...")

    # Crear motor de backtesting
    engine = BacktestEngine(
        tickers=["AAPL"],
        start_date="2024-09-01",
        end_date="2024-10-01",
        decision_interval=7,
        initial_capital=10000.0,
    )

    # Ejecutar simulación
    print("\n🚀 Iniciando simulación...")
    metrics = engine.run_simulation(model_id=MODELS["reasoning"])

    # Guardar resultados
    engine.save_results("demo_backtest_aapl.json")

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETADO")
    print("=" * 70)
    print("\n📝 Próximos pasos:")
    print("  1. Ver resultados: python3 visualize_backtest.py demo_backtest_aapl.json")
    print("  2. Probar con otro stock: edita este archivo")
    print("  3. Probar período más largo: cambia las fechas")
    print("  4. Comparar modelos: ejecuta con diferentes modelos")

    return metrics


def demo_comparison():
    """Demo comparando dos períodos"""
    print("\n" + "=" * 70)
    print("🎯 DEMO COMPARACIÓN - Mismo stock, diferentes períodos")
    print("=" * 70)

    # Período 1: Verano 2024
    print("\n📊 Ejecutando Período 1: Verano 2024...")
    engine1 = BacktestEngine(
        tickers=["AAPL"],
        start_date="2024-06-01",
        end_date="2024-08-01",
        decision_interval=7,
        initial_capital=10000.0,
    )
    metrics1 = engine1.run_simulation(model_id=MODELS["reasoning"], verbose=False)
    engine1.save_results("demo_summer_2024.json")

    # Período 2: Otoño 2024
    print("\n📊 Ejecutando Período 2: Otoño 2024...")
    engine2 = BacktestEngine(
        tickers=["AAPL"],
        start_date="2024-09-01",
        end_date="2024-10-01",
        decision_interval=7,
        initial_capital=10000.0,
    )
    metrics2 = engine2.run_simulation(model_id=MODELS["reasoning"], verbose=False)
    engine2.save_results("demo_fall_2024.json")

    # Comparar
    print("\n" + "=" * 70)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("=" * 70)
    print(f"\nVERANO 2024 (Jun-Ago):")
    print(f"  Retorno: ${metrics1['total_return']:.2f} ({metrics1['total_return_pct']:+.2f}%)")
    print(f"  Win Rate: {metrics1['win_rate']:.1f}%")
    print(f"  Trades: {metrics1['total_trades']}")

    print(f"\nOTOÑO 2024 (Sep-Oct):")
    print(f"  Retorno: ${metrics2['total_return']:.2f} ({metrics2['total_return_pct']:+.2f}%)")
    print(f"  Win Rate: {metrics2['win_rate']:.1f}%")
    print(f"  Trades: {metrics2['total_trades']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n🎯 SISTEMA DE BACKTESTING - DEMO")
    print("=" * 70)
    print("\n¿Qué demo quieres ejecutar?")
    print("\n1. Demo Simple (AAPL 1 mes) - ~2 minutos")
    print("2. Demo Comparación (2 períodos) - ~5 minutos")
    print("0. Salir")
    print("\n" + "=" * 70)

    choice = input("\n👉 Selecciona (1/2/0): ").strip()

    if choice == "1":
        demo_simple()
    elif choice == "2":
        demo_comparison()
    elif choice == "0":
        print("\n👋 Adiós!")
    else:
        print("\n❌ Opción inválida")
        print("💡 Usa: python3 demo_backtest.py")

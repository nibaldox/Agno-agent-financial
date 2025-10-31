#!/usr/bin/env python3
"""
Quick Backtest - Prueba rápida del sistema de backtesting
"""

from backtest_simulator import MODELS, BacktestEngine


def quick_test_single_stock():
    """Prueba rápida con un solo stock"""
    print("🚀 QUICK TEST - Backtesting de AAPL (3 meses)")
    print("=" * 70)

    engine = BacktestEngine(
        tickers=["AAPL"],
        start_date="2024-07-01",
        end_date="2024-10-01",
        decision_interval=7,  # Decisión cada semana
        initial_capital=10000.0,
    )

    print("\n▶️  Ejecutando simulación...")
    metrics = engine.run_simulation(model_id=MODELS["reasoning"])

    # Guardar resultados
    engine.save_results("backtest_aapl_quick.json")

    return metrics


def quick_test_portfolio():
    """Prueba con portfolio de múltiples stocks"""
    print("🚀 QUICK TEST - Portfolio FAANG (6 meses)")
    print("=" * 70)

    engine = BacktestEngine(
        tickers=["AAPL", "MSFT", "GOOGL"],
        start_date="2024-04-01",
        end_date="2024-10-01",
        decision_interval=14,  # Decisión cada 2 semanas
        initial_capital=20000.0,
    )

    print("\n▶️  Ejecutando simulación...")
    metrics = engine.run_simulation(model_id=MODELS["reasoning"])

    # Guardar resultados
    engine.save_results("backtest_portfolio_quick.json")

    return metrics


def compare_models():
    """Comparar diferentes modelos LLM"""
    print("🤖 COMPARACIÓN DE MODELOS")
    print("=" * 70)

    ticker = "AAPL"
    start = "2024-06-01"
    end = "2024-09-01"

    models_to_test = {
        "Reasoning (Chimera)": MODELS["reasoning"],
        "Advanced (Qwen 235B)": MODELS["advanced"],
    }

    results = {}

    for name, model_id in models_to_test.items():
        print(f"\n{'='*70}")
        print(f"🧪 Probando: {name}")
        print(f"{'='*70}")

        engine = BacktestEngine(
            tickers=[ticker],
            start_date=start,
            end_date=end,
            decision_interval=7,
            initial_capital=10000.0,
        )

        metrics = engine.run_simulation(model_id=model_id, verbose=False)
        results[name] = metrics

        engine.save_results(f"backtest_{name.lower().replace(' ', '_')}.json")

    # Comparar resultados
    print("\n" + "=" * 70)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("=" * 70)

    for name, metrics in results.items():
        print(f"\n🤖 {name}:")
        print(f"   Retorno: ${metrics['total_return']:.2f} ({metrics['total_return_pct']:+.2f}%)")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")

    return results


if __name__ == "__main__":
    import sys

    print("\n🎯 QUICK BACKTEST MENU")
    print("=" * 70)
    print("1. Test rápido AAPL (3 meses)")
    print("2. Test portfolio FAANG (6 meses)")
    print("3. Comparar modelos LLM")
    print("0. Salir")
    print("=" * 70)

    choice = input("\n👉 Selecciona: ").strip()

    if choice == "1":
        quick_test_single_stock()
    elif choice == "2":
        quick_test_portfolio()
    elif choice == "3":
        compare_models()
    elif choice == "0":
        print("👋 Adiós!")
    else:
        print("❌ Opción inválida")

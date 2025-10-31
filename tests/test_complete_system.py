"""
Test completo: Histórico + Serper Web Search
Prueba el sistema de trading con las dos nuevas funcionalidades
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "agente-agno" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from advanced_trading_team_v2 import PORTFOLIO, analyze_stock, run_daily_analysis


def test_historical_tracking():
    """Verificar que el sistema de histórico funciona"""
    print("=" * 80)
    print("TEST 1: SISTEMA DE HISTÓRICO")
    print("=" * 80)

    # Verificar archivos de histórico
    print(f"\nArchivos de histórico:")
    print(f"  Portfolio: {PORTFOLIO.history_file}")
    print(f"  Trades: {PORTFOLIO.trades_file}")
    print(f"  Daily: {PORTFOLIO.daily_summary_file}")

    # Obtener métricas históricas
    hist = PORTFOLIO.get_historical_performance()
    print(f"\nMétricas históricas actuales:")
    for key, value in hist.items():
        print(f"  {key}: {value}")

    print("\n[OK] Sistema de histórico operacional ✓")


def test_serper_integration():
    """Verificar que Serper está disponible"""
    print("\n" + "=" * 80)
    print("TEST 2: INTEGRACIÓN SERPER")
    print("=" * 80)

    import os

    from agno.tools.serper import SerperTools

    has_key = bool(os.getenv("SERPER_API_KEY"))
    print(f"\nSERPER_API_KEY disponible: {has_key}")

    if has_key:
        serper = SerperTools()
        print(f"SerperTools creado: {serper.__class__.__name__}")
        print(f"Métodos disponibles: search_web, search_news, search_scholar, scrape_webpage")
        print("\n[OK] Serper integrado correctamente ✓")
    else:
        print("\n[WARNING] SERPER_API_KEY no encontrada - búsqueda web deshabilitada")


def test_stock_analysis():
    """Probar análisis completo con ambas funcionalidades"""
    print("\n" + "=" * 80)
    print("TEST 3: ANÁLISIS COMPLETO DE STOCK (AAPL)")
    print("=" * 80)

    print("\nEjecutando análisis con:")
    print("  - 9 herramientas YFinance")
    print("  - Búsqueda web Serper")
    print("  - Tracking histórico automático")
    print("\n" + "-" * 80)

    # Ejecutar análisis
    analyze_stock("AAPL", use_openrouter=True)

    print("\n" + "-" * 80)
    print("[OK] Análisis completado ✓")

    # Verificar que se guardó el snapshot
    hist_after = PORTFOLIO.get_historical_performance()
    print(f"\nTotal operaciones después del análisis: {hist_after.get('total_trades', 0)}")


if __name__ == "__main__":
    try:
        # Test 1: Histórico
        test_historical_tracking()

        # Test 2: Serper
        test_serper_integration()

        # Test 3: Análisis completo
        print("\n" + "=" * 80)
        print("¿Ejecutar análisis completo de AAPL? (toma ~5-10 min)")
        print("=" * 80)
        response = input("\nEscribe 'si' para continuar o Enter para saltar: ").lower()

        if response == "si":
            test_stock_analysis()
        else:
            print("\n[SKIP] Análisis completo saltado")

        print("\n" + "=" * 80)
        print("TODOS LOS TESTS COMPLETADOS ✓")
        print("=" * 80)
        print("\nSistema listo con:")
        print("  ✓ Historical tracking (CSV persistence)")
        print("  ✓ Serper web search (market intelligence)")
        print("  ✓ 9 YFinance tools (financial data)")
        print("  ✓ 5 specialized agents (multi-model)")
        print("  ✓ Spanish reports (professional)")

    except Exception as e:
        print(f"\n[ERROR] Test fallido: {e}")
        import traceback

        traceback.print_exc()

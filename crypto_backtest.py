#!/usr/bin/env python3
"""
Sistema de Backtesting para CRIPTOMONEDAS
Soporta Bitcoin, Ethereum y otras criptos usando yfinance
"""

from backtest_simulator import BacktestEngine, MODELS
import sys

# Mapping de criptomonedas populares
CRYPTO_TICKERS = {
    "BTC": "BTC-USD",      # Bitcoin
    "ETH": "ETH-USD",      # Ethereum
    "BNB": "BNB-USD",      # Binance Coin
    "XRP": "XRP-USD",      # Ripple
    "ADA": "ADA-USD",      # Cardano
    "DOGE": "DOGE-USD",    # Dogecoin
    "SOL": "SOL-USD",      # Solana
    "MATIC": "MATIC-USD",  # Polygon
    "DOT": "DOT-USD",      # Polkadot
    "AVAX": "AVAX-USD",    # Avalanche
    "LINK": "LINK-USD",    # Chainlink
    "UNI": "UNI-USD",      # Uniswap
    "ATOM": "ATOM-USD",    # Cosmos
}

def show_available_cryptos():
    """Mostrar criptomonedas disponibles"""
    print("\n" + "="*70)
    print("💰 CRIPTOMONEDAS DISPONIBLES")
    print("="*70)
    
    print("\n🔝 Top Criptos:")
    print("  BTC  - Bitcoin")
    print("  ETH  - Ethereum")
    print("  BNB  - Binance Coin")
    print("  XRP  - Ripple")
    print("  ADA  - Cardano")
    print("  SOL  - Solana")
    
    print("\n🌟 Otras Criptos:")
    print("  DOGE - Dogecoin")
    print("  MATIC - Polygon")
    print("  DOT  - Polkadot")
    print("  AVAX - Avalanche")
    print("  LINK - Chainlink")
    print("  UNI  - Uniswap")
    print("  ATOM - Cosmos")
    
    print("\n💡 Tip: Usa el símbolo corto (ej: BTC, ETH)")
    print("="*70)

def parse_crypto_input(input_str: str) -> list:
    """Convertir input de usuario a tickers de Yahoo Finance"""
    symbols = [s.strip().upper() for s in input_str.split(",")]
    tickers = []
    
    for symbol in symbols:
        if symbol in CRYPTO_TICKERS:
            tickers.append(CRYPTO_TICKERS[symbol])
            print(f"  ✅ {symbol} → {CRYPTO_TICKERS[symbol]}")
        elif symbol.endswith("-USD"):
            tickers.append(symbol)
            print(f"  ✅ {symbol}")
        else:
            print(f"  ⚠️  {symbol} - No encontrado, intentando {symbol}-USD")
            tickers.append(f"{symbol}-USD")
    
    return tickers

def demo_bitcoin_quick():
    """Demo rápido con Bitcoin - 1 mes"""
    print("\n" + "="*70)
    print("₿ DEMO BITCOIN - Backtesting BTC (1 mes)")
    print("="*70)
    print("\nEste demo:")
    print("  ✅ Analiza Bitcoin (BTC-USD)")
    print("  ✅ Período: Septiembre 2024")
    print("  ✅ Decisiones cada 3 días (más frecuente por volatilidad)")
    print("  ✅ Capital inicial: $10,000")
    print("="*70)
    
    input("\n⏸️  Presiona ENTER para continuar...")
    
    engine = BacktestEngine(
        tickers=["BTC-USD"],
        start_date="2024-09-01",
        end_date="2024-10-01",
        decision_interval=3,  # Cada 3 días (crypto es más volátil)
        initial_capital=10000.0
    )
    
    print("\n🚀 Iniciando simulación de Bitcoin...")
    metrics = engine.run_simulation(model_id=MODELS["reasoning"])
    
    engine.save_results("crypto_backtest_btc.json")
    
    print("\n" + "="*70)
    print("✅ DEMO BITCOIN COMPLETADO")
    print("="*70)
    print(f"\n📊 Resultados finales:")
    print(f"   Retorno: ${metrics['total_return']:.2f} ({metrics['total_return_pct']:+.2f}%)")
    print(f"   Win Rate: {metrics['win_rate']:.1f}%")
    print(f"   Trades: {metrics['total_trades']}")
    
    print("\n📝 Archivo guardado: crypto_backtest_btc.json")
    print("👉 Visualizar: python3 visualize_backtest.py crypto_backtest_btc.json")

def demo_crypto_portfolio():
    """Demo con portfolio de criptos"""
    print("\n" + "="*70)
    print("🎯 DEMO PORTFOLIO CRYPTO - BTC + ETH + SOL")
    print("="*70)
    print("\nEste demo:")
    print("  ✅ Portfolio diversificado: BTC, ETH, SOL")
    print("  ✅ Período: 2 meses")
    print("  ✅ Decisiones cada 5 días")
    print("  ✅ Capital inicial: $15,000")
    print("="*70)
    
    input("\n⏸️  Presiona ENTER para continuar...")
    
    engine = BacktestEngine(
        tickers=["BTC-USD", "ETH-USD", "SOL-USD"],
        start_date="2024-08-01",
        end_date="2024-10-01",
        decision_interval=5,
        initial_capital=15000.0
    )
    
    print("\n🚀 Iniciando simulación de portfolio crypto...")
    metrics = engine.run_simulation(model_id=MODELS["reasoning"])
    
    engine.save_results("crypto_backtest_portfolio.json")
    
    print("\n" + "="*70)
    print("✅ DEMO PORTFOLIO COMPLETADO")
    print("="*70)
    print(f"\n📊 Resultados finales:")
    print(f"   Retorno: ${metrics['total_return']:.2f} ({metrics['total_return_pct']:+.2f}%)")
    print(f"   Win Rate: {metrics['win_rate']:.1f}%")
    print(f"   Trades: {metrics['total_trades']}")
    
    if metrics['holdings']:
        print(f"\n📦 Posiciones abiertas:")
        for ticker, info in metrics['holdings'].items():
            crypto_name = ticker.replace("-USD", "")
            print(f"   {crypto_name}: {info['shares']} unidades @ ${info['avg_price']:.2f}")

def custom_crypto_backtest():
    """Backtesting personalizado de criptomonedas"""
    print("\n" + "="*70)
    print("🎯 BACKTESTING PERSONALIZADO DE CRIPTOMONEDAS")
    print("="*70)
    
    show_available_cryptos()
    
    print("\n📝 Configuración:")
    
    # Criptomonedas
    crypto_input = input("\nCriptos (ej: BTC,ETH,SOL): ").strip()
    if not crypto_input:
        print("❌ Debes ingresar al menos una cripto")
        return
    
    tickers = parse_crypto_input(crypto_input)
    
    # Fechas
    print("\n📅 Período de análisis:")
    start_date = input("Fecha inicial (YYYY-MM-DD, default: 2024-07-01): ").strip()
    start_date = start_date if start_date else "2024-07-01"
    
    end_date = input("Fecha final (YYYY-MM-DD, default: 2024-10-01): ").strip()
    end_date = end_date if end_date else "2024-10-01"
    
    # Intervalo
    print("\n⏱️  Frecuencia de decisiones:")
    print("  Recomendado para crypto: 3-5 días (alta volatilidad)")
    interval_input = input("Días entre decisiones (default: 3): ").strip()
    interval = int(interval_input) if interval_input else 3
    
    # Capital
    capital_input = input("\n💰 Capital inicial (default: 10000): ").strip()
    capital = float(capital_input) if capital_input else 10000.0
    
    # Modelo
    print("\n🤖 Modelos disponibles:")
    print("  1. DeepSeek Chimera (Razonamiento - Recomendado)")
    print("  2. Qwen3 235B (Estrategia avanzada)")
    print("  3. Tongyi DeepResearch (Análisis profundo)")
    
    model_choice = input("Selecciona modelo (default: 1): ").strip()
    model_map = {
        "1": MODELS["reasoning"],
        "2": MODELS["advanced"],
        "3": MODELS["deep_research"]
    }
    model_id = model_map.get(model_choice, MODELS["reasoning"])
    
    # Confirmar
    print("\n" + "="*70)
    print("📋 RESUMEN DE CONFIGURACIÓN:")
    print("="*70)
    print(f"Criptos: {', '.join([t.replace('-USD', '') for t in tickers])}")
    print(f"Período: {start_date} → {end_date}")
    print(f"Decisiones cada: {interval} días")
    print(f"Capital inicial: ${capital:,.2f}")
    print("="*70)
    
    confirm = input("\n¿Continuar? (s/n): ").lower().strip()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # Ejecutar
    engine = BacktestEngine(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        decision_interval=interval,
        initial_capital=capital
    )
    
    print("\n🚀 Iniciando simulación...")
    metrics = engine.run_simulation(model_id=model_id)
    
    # Guardar
    filename = f"crypto_backtest_custom_{start_date}_{end_date}.json"
    engine.save_results(filename)
    
    print(f"\n💾 Resultados guardados: {filename}")
    print(f"👉 Visualizar: python3 visualize_backtest.py {filename}")

def compare_crypto_vs_stock():
    """Comparar performance crypto vs stock tradicional"""
    print("\n" + "="*70)
    print("⚖️  CRYPTO vs STOCK - Comparación")
    print("="*70)
    print("\nComparar rendimiento de:")
    print("  • Bitcoin (BTC-USD)")
    print("  • Apple (AAPL)")
    print("\nMismo período, mismo capital, mismo modelo")
    print("="*70)
    
    input("\n⏸️  Presiona ENTER para continuar...")
    
    period_start = "2024-07-01"
    period_end = "2024-10-01"
    capital = 10000.0
    
    # Test Bitcoin
    print("\n" + "="*70)
    print("₿ Simulación 1: BITCOIN")
    print("="*70)
    
    engine_btc = BacktestEngine(
        tickers=["BTC-USD"],
        start_date=period_start,
        end_date=period_end,
        decision_interval=5,
        initial_capital=capital
    )
    metrics_btc = engine_btc.run_simulation(model_id=MODELS["reasoning"], verbose=False)
    engine_btc.save_results("comparison_btc.json")
    
    # Test Apple
    print("\n" + "="*70)
    print("🍎 Simulación 2: APPLE")
    print("="*70)
    
    engine_aapl = BacktestEngine(
        tickers=["AAPL"],
        start_date=period_start,
        end_date=period_end,
        decision_interval=5,
        initial_capital=capital
    )
    metrics_aapl = engine_aapl.run_simulation(model_id=MODELS["reasoning"], verbose=False)
    engine_aapl.save_results("comparison_aapl.json")
    
    # Comparar
    print("\n" + "="*70)
    print("📊 RESULTADOS DE COMPARACIÓN")
    print("="*70)
    
    print(f"\n₿ BITCOIN (BTC-USD):")
    print(f"   Capital Final: ${metrics_btc['current_value']:,.2f}")
    print(f"   Retorno: ${metrics_btc['total_return']:,.2f} ({metrics_btc['total_return_pct']:+.2f}%)")
    print(f"   Win Rate: {metrics_btc['win_rate']:.1f}%")
    print(f"   Profit Factor: {metrics_btc['profit_factor']:.2f}")
    print(f"   Total Trades: {metrics_btc['total_trades']}")
    
    print(f"\n🍎 APPLE (AAPL):")
    print(f"   Capital Final: ${metrics_aapl['current_value']:,.2f}")
    print(f"   Retorno: ${metrics_aapl['total_return']:,.2f} ({metrics_aapl['total_return_pct']:+.2f}%)")
    print(f"   Win Rate: {metrics_aapl['win_rate']:.1f}%")
    print(f"   Profit Factor: {metrics_aapl['profit_factor']:.2f}")
    print(f"   Total Trades: {metrics_aapl['total_trades']}")
    
    # Ganador
    print("\n" + "="*70)
    if metrics_btc['total_return'] > metrics_aapl['total_return']:
        print("🏆 GANADOR: BITCOIN")
        diff = metrics_btc['total_return'] - metrics_aapl['total_return']
        print(f"   Diferencia: +${diff:.2f}")
    else:
        print("🏆 GANADOR: APPLE")
        diff = metrics_aapl['total_return'] - metrics_btc['total_return']
        print(f"   Diferencia: +${diff:.2f}")
    print("="*70)
    
    print("\n💾 Archivos guardados:")
    print("   • comparison_btc.json")
    print("   • comparison_aapl.json")
    print("\n👉 Comparar visualmente:")
    print("   python3 visualize_backtest.py compare comparison_*.json")

def main():
    """Menú principal"""
    print("\n" + "="*70)
    print("💰 SISTEMA DE BACKTESTING PARA CRIPTOMONEDAS")
    print("="*70)
    print("\n📋 MENÚ:")
    print("─"*70)
    print("  1. 🚀 Demo Rápido - Bitcoin (1 mes)")
    print("  2. 📊 Demo Portfolio - BTC + ETH + SOL (2 meses)")
    print("  3. 🎯 Backtesting Personalizado")
    print("  4. ⚖️  Comparar Crypto vs Stock")
    print("  5. 💡 Ver Criptos Disponibles")
    print("  0. 🚪 Salir")
    print("─"*70)
    
    choice = input("\n👉 Selecciona opción: ").strip()
    
    if choice == "1":
        demo_bitcoin_quick()
    elif choice == "2":
        demo_crypto_portfolio()
    elif choice == "3":
        custom_crypto_backtest()
    elif choice == "4":
        compare_crypto_vs_stock()
    elif choice == "5":
        show_available_cryptos()
        input("\n⏸️  Presiona ENTER para volver...")
        main()
    elif choice == "0":
        print("\n👋 ¡Hasta luego!")
    else:
        print("\n❌ Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Backtesting automático V2 OPTIMIZADO: BTC-USD con parámetros configurables

MEJORAS IMPLEMENTADAS:
- Stop Loss automático: -3%
- Take Profit automático: +5%
- Indicadores avanzados: EMA, MACD, Bollinger Bands, ATR
- Prompt mejorado con reglas estrictas
- Position sizing dinámico
- Filtro de volumen mínimo

Versión: 2.0.0

USO:
    python3 btc_deepseek_auto_v2.py [días] [intervalo_horas]
    
EJEMPLOS:
    python3 btc_deepseek_auto_v2.py           # 60 días, 1 hora (default)
    python3 btc_deepseek_auto_v2.py 30 4      # 30 días, 4 horas
    python3 btc_deepseek_auto_v2.py 7 1       # 7 días, 1 hora (test rápido)
"""
import sys
import traceback
sys.path.insert(0, '/Users/xodla/Documents/Code/06-Agentes/Agno-agent-financial')

from hourly_backtest_v2_optimized import HourlyBacktestEngine, MODELS

def main():
    # Configuración desde argumentos de línea de comandos
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    decision_interval_hours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # Validaciones
    if days > 60:
        print("⚠️  Advertencia: yfinance limita datos horarios a 60 días. Usando 60.")
        days = 60
    
    if decision_interval_hours < 1:
        print("⚠️  Advertencia: Intervalo mínimo es 1 hora. Usando 1.")
        decision_interval_hours = 1
    
    # Configuración fija
    tickers = ["BTC-USD"]
    initial_capital = 10000.0
    
    print("\n" + "="*70)
    print("🚀 BACKTESTING AUTOMÁTICO V2 - BTC CON DEEPSEEK V3 OPTIMIZADO")
    print("="*70)
    print("📊 Configuración:")
    print(f"  • Ticker: {tickers[0]}")
    print(f"  • Período: {days} días (datos horarios)")
    print(f"  • Decisiones: Cada {decision_interval_hours} hora(s)")
    
    # Calcular número aproximado de decisiones
    total_hours = days * 24
    approx_decisions = total_hours // decision_interval_hours
    print(f"  • Decisiones aproximadas: ~{approx_decisions}")
    print(f"  • Capital inicial: ${initial_capital:,.0f}")
    print("  • Modelo: DeepSeek V3 (rápido y preciso)")
    print("\n🎯 MEJORAS V2:")
    print("  ✅ Stop Loss automático: -3%")
    print("  ✅ Take Profit automático: +5%")
    print("  ✅ Indicadores avanzados: EMA, MACD, Bollinger, ATR")
    print("  ✅ Reglas de trading estrictas")
    print("  ✅ Position sizing dinámico")
    print("  ✅ Filtro de volumen mínimo")
    print("="*70)
    
    # Estimar tiempo
    if approx_decisions < 100:
        tiempo_estimado = "5-15 minutos"
    elif approx_decisions < 500:
        tiempo_estimado = "15-45 minutos"
    elif approx_decisions < 1000:
        tiempo_estimado = "45-90 minutos"
    else:
        tiempo_estimado = "1-2 horas"
    
    print(f"\n⏱️  Tiempo estimado: {tiempo_estimado}\n")
    
    print("\n🚀 Iniciando simulación...\n")
    
    # Crear engine
    engine = HourlyBacktestEngine(tickers, days, decision_interval_hours, initial_capital)
    
    # Ejecutar con DeepSeek V3
    metrics = engine.run_simulation(model_id=MODELS["deepseek"])
    
    # Guardar resultados
    if metrics:
        filename = f"btc_{days}d_{decision_interval_hours}h_deepseek_v2.json"
        engine.save_results(filename)
        print(f"\n✅ Resultados guardados en: {filename}")
        print(f"\n💡 Para visualizar dashboard interactivo:")
        print(f"   python3 generate_dashboard.py {filename}")

if __name__ == "__main__":
    try:
        # Mostrar ayuda si se solicita
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
            print(__doc__)
            sys.exit(0)
        
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Simulación interrumpida por el usuario")
    except ValueError as e:
        print(f"\n❌ Error en parámetros: {str(e)}")
        print("\nUso correcto:")
        print("  python3 btc_deepseek_auto_v2.py [días] [intervalo_horas]")
        print("\nEjemplos:")
        print("  python3 btc_deepseek_auto_v2.py           # 60 días, 1 hora")
        print("  python3 btc_deepseek_auto_v2.py 30 4      # 30 días, 4 horas")
        print("  python3 btc_deepseek_auto_v2.py 7 1       # 7 días, 1 hora")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

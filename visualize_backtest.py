#!/usr/bin/env python3
"""
Visualizador de Resultados de Backtesting
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def load_results(filename: str) -> dict:
    """Cargar resultados de archivo JSON"""
    with open(filename, 'r') as f:
        return json.load(f)

def plot_equity_curve(results: dict, filename: str = "equity_curve.png"):
    """Graficar curva de equity"""
    equity_data = results['equity_curve']
    
    if not equity_data:
        print("❌ No hay datos de equity curve")
        return
    
    df = pd.DataFrame(equity_data)
    df['date'] = pd.to_datetime(df['date'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['value'], linewidth=2, label='Portfolio Value')
    plt.axhline(y=results['config']['initial_capital'], color='r', linestyle='--', label='Initial Capital')
    
    plt.title('Portfolio Equity Curve', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(filename, dpi=150)
    print(f"📊 Gráfico guardado: {filename}")
    plt.close()

def plot_trades_distribution(results: dict, filename: str = "trades_dist.png"):
    """Graficar distribución de trades"""
    trades = [t for t in results['trades'] if t['action'] == 'SELL']
    
    if not trades:
        print("❌ No hay trades cerrados")
        return
    
    pnls = [t['pnl'] for t in trades]
    
    plt.figure(figsize=(10, 6))
    plt.hist(pnls, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break Even')
    
    plt.title('P&L Distribution of Closed Trades', fontsize=14, fontweight='bold')
    plt.xlabel('P&L ($)')
    plt.ylabel('Number of Trades')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    plt.savefig(filename, dpi=150)
    print(f"📊 Gráfico guardado: {filename}")
    plt.close()

def print_detailed_report(results: dict):
    """Imprimir reporte detallado"""
    print("\n" + "="*80)
    print("📈 REPORTE DETALLADO DE BACKTESTING")
    print("="*80)
    
    # Configuración
    config = results['config']
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"   Tickers: {', '.join(config['tickers'])}")
    print(f"   Período: {config['days']} días ({config.get('timeframe', 'hourly')})")
    print(f"   Capital Inicial: ${config['initial_capital']:,.2f}")
    print(f"   Intervalo de decisiones: {config['decision_interval_hours']} hora(s)")
    
    # Métricas finales
    metrics = results['final_metrics']
    print(f"\n💰 RESULTADOS FINALES:")
    print(f"   Capital Final: ${metrics['current_value']:,.2f}")
    print(f"   Retorno Total: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
    print(f"   Efectivo: ${metrics['cash']:,.2f}")
    
    print(f"\n📊 ESTADÍSTICAS DE TRADING:")
    print(f"   Total Operaciones: {metrics['total_trades']}")
    print(f"   Operaciones Ganadoras: {metrics['winning_trades']}")
    print(f"   Operaciones Perdedoras: {metrics['losing_trades']}")
    print(f"   Win Rate: {metrics['win_rate']:.1f}%")
    print(f"   Ganancia Promedio: ${metrics['avg_win']:.2f}")
    print(f"   Pérdida Promedio: ${metrics['avg_loss']:.2f}")
    print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
    
    # Posiciones abiertas
    if metrics['holdings']:
        print(f"\n📦 POSICIONES ABIERTAS:")
        for ticker, info in metrics['holdings'].items():
            print(f"   {ticker}: {info['shares']} acciones @ ${info['avg_price']:.2f}")
    
    # Historial de trades
    print(f"\n📜 HISTORIAL DE TRADES:")
    print("─"*80)
    
    for i, trade in enumerate(results['trades'][:10], 1):  # Primeros 10
        action_emoji = "🟢" if trade['action'] == "BUY" else "🔴"
        print(f"{action_emoji} {trade['date']}: {trade['action']} {trade['shares']} {trade['ticker']} @ ${trade['price']:.2f}")
        
        if trade['action'] == 'SELL':
            pnl = trade.get('pnl', 0)
            pnl_pct = trade.get('pnl_pct', 0)
            pnl_emoji = "💚" if pnl > 0 else "💔"
            print(f"   {pnl_emoji} P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
        
        print(f"   Razón: {trade.get('reason', 'N/A')[:60]}...")
        print("─"*80)
    
    if len(results['trades']) > 10:
        print(f"... y {len(results['trades']) - 10} trades más")
    
    print()

def compare_results(filenames: list):
    """Comparar múltiples resultados"""
    results_list = []
    
    for filename in filenames:
        try:
            results = load_results(filename)
            results_list.append((filename, results))
        except Exception as e:
            print(f"❌ Error cargando {filename}: {e}")
    
    if not results_list:
        print("❌ No se pudieron cargar resultados")
        return
    
    print("\n" + "="*80)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("="*80)
    
    # Tabla comparativa
    print(f"\n{'Archivo':<30} | {'Retorno %':>12} | {'Win Rate':>10} | {'Profit Factor':>15}")
    print("─"*80)
    
    for filename, results in results_list:
        metrics = results['final_metrics']
        print(f"{filename:<30} | {metrics['total_return_pct']:>11.2f}% | {metrics['win_rate']:>9.1f}% | {metrics['profit_factor']:>15.2f}")
    
    print("="*80)

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("📊 VISUALIZADOR DE RESULTADOS DE BACKTESTING")
        print("="*80)
        print("\nUso:")
        print("  python visualize_backtest.py <archivo.json>")
        print("  python visualize_backtest.py compare <archivo1.json> <archivo2.json> ...")
        print("\nEjemplos:")
        print("  python visualize_backtest.py backtest_results.json")
        print("  python visualize_backtest.py compare backtest_*.json")
        return
    
    if sys.argv[1] == "compare":
        filenames = sys.argv[2:]
        compare_results(filenames)
    else:
        filename = sys.argv[1]
        
        try:
            results = load_results(filename)
            
            # Reporte detallado
            print_detailed_report(results)
            
            # Gráficos
            plot_equity_curve(results, filename.replace('.json', '_equity.png'))
            plot_trades_distribution(results, filename.replace('.json', '_trades.png'))
            
            print("\n✅ Análisis completado!")
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {filename}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generador de Dashboard HTML interactivo para resultados de backtesting
Visualización avanzada con gráficos interactivos usando Plotly
"""
import json
from datetime import datetime
from pathlib import Path


def generate_dashboard(json_file: str):
    """Generar dashboard HTML completo desde JSON"""

    # Cargar datos
    with open(json_file, "r") as f:
        data = json.load(f)

    config = data["config"]
    trades = data["trades"]
    decisions = data["decisions_log"]

    # Calcular métricas
    buy_decisions = [d for d in decisions if d["action"] == "BUY"]
    sell_decisions = [d for d in decisions if d["action"] == "SELL"]
    hold_decisions = [d for d in decisions if d["action"] == "HOLD"]

    # Reconstruir evolución del capital
    capital_history = []
    cash = config["initial_capital"]
    btc_held = 0.0

    for decision in decisions:
        result = decision.get("execution_result", {})
        price = decision["price"]

        if result.get("success") and "trade" in result:
            trade = result["trade"]
            if trade["action"] == "BUY":
                cash = trade["cash_after"]
                btc_held += trade["shares"]
            elif trade["action"] == "SELL":
                cash = trade["cash_after"]
                btc_held -= trade["shares"]

        btc_value = btc_held * price
        total_value = cash + btc_value

        capital_history.append(
            {
                "date": decision["date"],
                "price": price,
                "cash": cash,
                "btc_value": btc_value,
                "total": total_value,
                "btc_held": btc_held,
                "action": decision["action"],
            }
        )

    # Calcular métricas finales
    initial_capital = config["initial_capital"]
    final_capital = capital_history[-1]["total"] if capital_history else initial_capital
    total_return = final_capital - initial_capital
    return_pct = (total_return / initial_capital) * 100

    # Datos para gráficos (formato JavaScript)
    dates_js = [f"'{h['date']}'" for h in capital_history]
    prices_js = [h["price"] for h in capital_history]
    portfolio_js = [h["total"] for h in capital_history]

    # Marcar BUYs y SELLs
    buy_dates = [f"'{d['date']}'" for d in buy_decisions]
    buy_prices = [d["price"] for d in buy_decisions]
    sell_dates = [f"'{d['date']}'" for d in sell_decisions]
    sell_prices = [d["price"] for d in sell_decisions]

    # Generar HTML
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Backtesting - {config['tickers'][0]}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
        }}

        .card-title {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .card-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}

        .card-subtitle {{
            font-size: 1.1em;
            color: #999;
        }}

        .positive {{
            color: #10b981;
        }}

        .negative {{
            color: #ef4444;
        }}

        .neutral {{
            color: #6b7280;
        }}

        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .chart-title {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}

        .stat-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}

        .trades-table {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}

        tr:hover {{
            background: #f9fafb;
        }}

        .buy-action {{
            background: #d1fae5;
            color: #065f46;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}

        .sell-action {{
            background: #fee2e2;
            color: #991b1b;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}

        .profit {{
            color: #10b981;
            font-weight: bold;
        }}

        .loss {{
            color: #ef4444;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard de Backtesting - {config['tickers'][0]}</h1>

        <!-- KPIs Principales -->
        <div class="dashboard">
            <div class="card">
                <div class="card-title">Capital Final</div>
                <div class="card-value {'positive' if total_return >= 0 else 'negative'}">
                    ${final_capital:,.2f}
                </div>
                <div class="card-subtitle">Inicial: ${initial_capital:,.2f}</div>
            </div>

            <div class="card">
                <div class="card-title">Retorno Total</div>
                <div class="card-value {'positive' if total_return >= 0 else 'negative'}">
                    {return_pct:+.2f}%
                </div>
                <div class="card-subtitle">${total_return:+,.2f}</div>
            </div>

            <div class="card">
                <div class="card-title">Total Operaciones</div>
                <div class="card-value neutral">{len(trades)}</div>
                <div class="card-subtitle">
                    Ganadoras: {len([t for t in trades if t.get('pnl', 0) > 0])}
                </div>
            </div>

            <div class="card">
                <div class="card-title">Decisiones</div>
                <div class="card-value neutral">{len(decisions)}</div>
                <div class="card-subtitle">
                    BUY: {len(buy_decisions)} | SELL: {len(sell_decisions)} | HOLD: {len(hold_decisions)}
                </div>
            </div>
        </div>

        <!-- Estadísticas Adicionales -->
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-label">Período</div>
                <div class="stat-value">{config['days']} días</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Intervalo</div>
                <div class="stat-value">{config['decision_interval_hours']}h</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Win Rate</div>
                <div class="stat-value">
                    {(len([t for t in trades if t.get('pnl', 0) > 0]) / len(trades) * 100) if trades else 0:.1f}%
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Efectivo Final</div>
                <div class="stat-value">${capital_history[-1]['cash']:,.2f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">BTC Acumulado</div>
                <div class="stat-value">{capital_history[-1]['btc_held']:.8f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Tasa BUY</div>
                <div class="stat-value">{len(buy_decisions)/len(decisions)*100:.1f}%</div>
            </div>
        </div>

        <!-- Gráfico 1: Evolución del Portfolio -->
        <div class="chart-container">
            <div class="chart-title">📈 Evolución del Valor del Portfolio</div>
            <div id="portfolioChart"></div>
        </div>

        <!-- Gráfico 2: Precio BTC con Señales -->
        <div class="chart-container">
            <div class="chart-title">💹 Precio de BTC con Señales de Trading</div>
            <div id="priceChart"></div>
        </div>

        <!-- Gráfico 3: Distribución de Decisiones -->
        <div class="chart-container">
            <div class="chart-title">🎯 Distribución de Decisiones</div>
            <div id="decisionsChart"></div>
        </div>

        <!-- Tabla de Trades -->
        <div class="trades-table">
            <div class="chart-title">📋 Historial de Operaciones</div>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Acción</th>
                        <th>Precio</th>
                        <th>Cantidad</th>
                        <th>Monto</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                        <th>Razón</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Agregar filas de trades
    for trade in trades[-50:]:  # Últimas 50 operaciones
        action_class = "buy-action" if trade["action"] == "BUY" else "sell-action"
        pnl = trade.get("pnl", 0)
        pnl_pct = trade.get("pnl_pct", 0)
        pnl_class = "profit" if pnl > 0 else "loss" if pnl < 0 else ""

        html += f"""
                    <tr>
                        <td>{trade['date']}</td>
                        <td><span class="{action_class}">{trade['action']}</span></td>
                        <td>${trade['price']:,.2f}</td>
                        <td>{trade['shares']:.8f}</td>
                        <td>${trade.get('cost', trade.get('revenue', 0)):,.2f}</td>
                        <td class="{pnl_class}">${pnl:+,.2f}</td>
                        <td class="{pnl_class}">{pnl_pct:+.2f}%</td>
                        <td>{trade.get('reason', 'N/A')[:50]}...</td>
                    </tr>
"""

    html += f"""
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Gráfico 1: Evolución del Portfolio
        var portfolioTrace = {{
            x: [{', '.join(dates_js)}],
            y: {portfolio_js},
            type: 'scatter',
            mode: 'lines',
            name: 'Valor Portfolio',
            line: {{
                color: '#667eea',
                width: 3
            }},
            fill: 'tonexty'
        }};

        var initialLine = {{
            x: [{', '.join(dates_js)}],
            y: Array({len(dates_js)}).fill({initial_capital}),
            type: 'scatter',
            mode: 'lines',
            name: 'Capital Inicial',
            line: {{
                color: '#ef4444',
                width: 2,
                dash: 'dash'
            }}
        }};

        var portfolioLayout = {{
            xaxis: {{
                title: 'Fecha',
                gridcolor: '#e5e7eb'
            }},
            yaxis: {{
                title: 'Valor ($)',
                gridcolor: '#e5e7eb'
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 20, b: 60, l: 80 }}
        }};

        Plotly.newPlot('portfolioChart', [initialLine, portfolioTrace], portfolioLayout, {{responsive: true}});

        // Gráfico 2: Precio BTC con señales
        var priceTrace = {{
            x: [{', '.join(dates_js)}],
            y: {prices_js},
            type: 'scatter',
            mode: 'lines',
            name: 'Precio BTC',
            line: {{
                color: '#f59e0b',
                width: 2
            }}
        }};

        var buyTrace = {{
            x: [{', '.join(buy_dates)}],
            y: {buy_prices},
            type: 'scatter',
            mode: 'markers',
            name: 'BUY',
            marker: {{
                color: '#10b981',
                size: 12,
                symbol: 'triangle-up',
                line: {{
                    color: '#065f46',
                    width: 2
                }}
            }}
        }};

        var sellTrace = {{
            x: [{', '.join(sell_dates)}],
            y: {sell_prices},
            type: 'scatter',
            mode: 'markers',
            name: 'SELL',
            marker: {{
                color: '#ef4444',
                size: 12,
                symbol: 'triangle-down',
                line: {{
                    color: '#991b1b',
                    width: 2
                }}
            }}
        }};

        var priceLayout = {{
            xaxis: {{
                title: 'Fecha',
                gridcolor: '#e5e7eb'
            }},
            yaxis: {{
                title: 'Precio BTC ($)',
                gridcolor: '#e5e7eb'
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 20, b: 60, l: 80 }}
        }};

        Plotly.newPlot('priceChart', [priceTrace, buyTrace, sellTrace], priceLayout, {{responsive: true}});

        // Gráfico 3: Distribución de decisiones
        var decisionsData = [{{
            values: [{len(buy_decisions)}, {len(sell_decisions)}, {len(hold_decisions)}],
            labels: ['BUY', 'SELL', 'HOLD'],
            type: 'pie',
            marker: {{
                colors: ['#10b981', '#ef4444', '#6b7280']
            }},
            textinfo: 'label+percent',
            textposition: 'outside',
            hole: 0.4
        }}];

        var decisionsLayout = {{
            margin: {{ t: 20, r: 20, b: 20, l: 20 }},
            paper_bgcolor: 'white',
            showlegend: true
        }};

        Plotly.newPlot('decisionsChart', decisionsData, decisionsLayout, {{responsive: true}});
    </script>
</body>
</html>
"""

    # Guardar HTML
    output_file = json_file.replace(".json", "_dashboard.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Dashboard generado: {output_file}")
    print(f"📊 Abre el archivo en tu navegador para ver el reporte interactivo\n")

    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "btc_30d_4h_deepseek.json"

    print(f"\n🚀 Generando dashboard desde: {json_file}")
    generate_dashboard(json_file)

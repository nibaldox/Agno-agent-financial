# 🤖 Integración de FASE 2 con Agentes Agno

## Descripción General

Este sistema combina:
- **9 Agentes de Trading** (Agno framework) para decisiones inteligentes
- **FASE 2 Analytics** (métricas avanzadas + visualizaciones + AI insights)

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣ ANÁLISIS (9 Agentes Agno)                              │
│     ├─ Market Researcher (noticias, datos)                 │
│     ├─ 3 Risk Analysts (conservador, moderado, agresivo)   │
│     ├─ 3 Trading Strategists (técnico, fundamental, momentum)│
│     ├─ Portfolio Manager (decisión final)                  │
│     └─ Daily Reporter (resumen diario)                     │
│                                                             │
│  ⬇️                                                          │
│                                                             │
│  2️⃣ EJECUCIÓN DE TRADES                                     │
│     └─ trading_script.py (buy/sell/update CSVs)            │
│                                                             │
│  ⬇️                                                          │
│                                                             │
│  3️⃣ ANALYTICS AVANZADOS (FASE 2)                            │
│     ├─ MetricsCalculator (Sharpe, Sortino, Beta, Alpha)   │
│     ├─ InteractiveVisualizationGenerator (6 gráficos)     │
│     ├─ LLMInsightsGenerator (AI analysis)                 │
│     └─ HTMLReportGenerator (reporte profesional)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Opción 1: Workflow Completo (Recomendado)

```powershell
# Ejecutar análisis + generación de reporte
python agente-agno/scripts/advanced_reporting_workflow.py --data-dir "Scripts and CSV Files"
```

Esto ejecuta:
1. ✅ Carga estado del portafolio
2. ✅ (Opcional) Ejecuta 9 agentes para análisis
3. ✅ Genera reporte FASE 2 completo

### Opción 2: Solo Reporte FASE 2

```powershell
# Solo generar reporte sin agentes
python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"
```

### Opción 3: Solo Agentes (Sin Reporte)

```python
from agents import load_complete_team

# Cargar equipo de 9 agentes
team = load_complete_team(use_openrouter=True)

# Consultar
query = "Analiza ABEO como inversión potencial"
team.print_response(query, stream=True)
```

## 📊 Componentes del Sistema

### 1. Agentes de Trading (Agno)

**Ubicación**: `agente-agno/agents/*.yaml`

| Agente | Archivo | Función |
|--------|---------|---------|
| Market Researcher | `market_researcher.yaml` | Investiga mercado, noticias, datos |
| Risk Analyst (3x) | `risk_analysts.yaml` | Evalúa riesgos (conservador, moderado, agresivo) |
| Trading Strategist (3x) | `trading_strategists.yaml` | Estrategias (técnico, fundamental, momentum) |
| Portfolio Manager | `portfolio_manager.yaml` | Toma decisión final de trading |
| Daily Reporter | `daily_reporter.yaml` | Genera resumen diario en español |
| **Advanced Reporter** | `advanced_reporter.yaml` | **NUEVO: Genera reporte FASE 2** |

### 2. FASE 2 Analytics

**Ubicación**: `agente-agno/core/`

| Módulo | Descripción |
|--------|-------------|
| `metrics.py` | Sharpe, Sortino, Beta, Alpha, Max Drawdown |
| `visualization_plotly.py` | 6 gráficos interactivos (Plotly) |
| `llm_insights.py` | AI insights con DeepSeek |
| `html_reports.py` | Generador de HTML profesional |

## 🔧 Uso Programático

### Cargar Advanced Reporter

```python
from agents import load_advanced_reporter

# Cargar agente de reportes avanzados
reporter = load_advanced_reporter(use_openrouter=True)

# El agente está listo para generar reportes
# (actualmente es una configuración YAML,
#  la ejecución usa fase2_example_interactive.py)
```

### Generar Reporte Completo

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "agente-agno"))

from fase2_example_interactive import (
    load_portfolio_data,
    calculate_equity_series,
    fetch_benchmark_data
)
from core import MetricsCalculator, HTMLReportGenerator
from core.visualization_plotly import InteractiveVisualizationGenerator
from core.llm_insights import create_insights_generator

# 1. Cargar datos
data_dir = Path("Scripts and CSV Files")
portfolio_df, trades_df = load_portfolio_data(data_dir)
equity, cash = calculate_equity_series(portfolio_df)

# 2. Benchmark
benchmark = fetch_benchmark_data(equity.index.min(), equity.index.max())

# 3. Métricas
calculator = MetricsCalculator(risk_free_rate=0.05)
metrics = calculator.calculate_all_metrics(
    equity_series=equity,
    trades_df=trades_df,
    benchmark_ticker='^GSPC'
)

# 4. AI Insights
llm_gen = create_insights_generator()
insights = llm_gen.generate_insights(
    portfolio_summary={'total_equity': equity.iloc[-1], ...},
    metrics=metrics,
    trades_summary={...}
)

# 5. Gráficos
viz = InteractiveVisualizationGenerator(output_dir="reports/charts")
chart_paths = viz.generate_all_plots(
    portfolio_equity=equity,
    trades_df=trades_df,
    cash_series=cash,
    benchmark_data=benchmark
)

# 6. HTML Report
reporter = HTMLReportGenerator()
reporter.generate_full_report(
    output_path="reports/report.html",
    portfolio_summary={...},
    metrics=metrics,
    chart_paths=chart_paths,
    llm_insights=insights
)
```

## 🎯 Casos de Uso

### Caso 1: Reporte Diario Automático

```powershell
# Ejecutar cada día después del cierre del mercado
python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"
```

**Output**: `reports/report_YYYYMMDD_HHMMSS.html`

### Caso 2: Análisis Pre-Trade

```python
from agents import load_complete_team

team = load_complete_team()

# Analizar antes de hacer trade
query = """
Portafolio actual: $83.19
Cash: $47.28
Posiciones: 3

¿Debería comprar más ABEO o cerrar posiciones?
"""

team.print_response(query, stream=True)
```

### Caso 3: Reporte Semanal Completo

```powershell
# Lunes: Generar reporte completo de la semana anterior
python agente-agno/scripts/advanced_reporting_workflow.py --data-dir "Scripts and CSV Files"
```

Incluye:
- ✅ Análisis de 9 agentes
- ✅ Métricas de rendimiento
- ✅ 6 gráficos interactivos
- ✅ AI insights

### Caso 4: Post-Trade Validation

```python
# Después de ejecutar trades
from trading_script import process_portfolio

# 1. Actualizar portfolio
portfolio_df = process_portfolio(data_dir="Scripts and CSV Files")

# 2. Generar reporte para ver impacto
import subprocess
subprocess.run([
    "python", "agente-agno/fase2_example_interactive.py",
    "--data-dir", "Scripts and CSV Files"
])
```

## 🔄 Workflow Típico

### Workflow Diario (Lunes a Viernes)

```
09:00 - Market Open
  └─ Cargar equipo de agentes

10:00 - Mid-morning Analysis
  ├─ Market Researcher: buscar noticias
  ├─ Risk Analysts: evaluar riesgos actuales
  └─ Trading Strategists: identificar oportunidades

14:00 - Pre-close Decision
  ├─ Portfolio Manager: tomar decisión
  └─ Ejecutar trades si es necesario

16:00 - Market Close
  ├─ Daily Reporter: resumen del día
  └─ Advanced Reporter: generar reporte FASE 2

17:00 - Review
  └─ Revisar reporte HTML con métricas y AI insights
```

### Workflow Semanal (Lunes)

```
Lunes AM:
  1. Generar reporte semanal completo (FASE 2)
  2. Revisar métricas: Sharpe, Max Drawdown, Win Rate
  3. Leer AI insights para ajustes estratégicos
  4. Planificar trades de la semana
```

## 📋 Salidas del Sistema

### 1. Reporte Diario (Daily Reporter)

**Formato**: Markdown/Text
**Contenido**:
- Rendimiento del portfolio
- Transacciones del día
- Cambios de posición
- Eventos clave del mercado
- Métricas de riesgo básicas

### 2. Reporte Avanzado (FASE 2)

**Formato**: HTML interactivo
**Contenido**:
- **Executive Summary**: Total Equity, Cash, ROI, P&L
- **Performance Metrics**: Sharpe (−0.59), Sortino, Beta (0.64), Alpha
- **Trade Statistics**: 30 trades, 61.5% win rate
- **Interactive Charts** (6):
  1. Daily Performance (Portfolio vs S&P 500)
  2. Drawdown Analysis (−38.4% max)
  3. Portfolio Composition (donut chart)
  4. Win/Loss Analysis (bar chart)
  5. Cash Position (stacked area)
  6. Performance vs Benchmark
- **AI Insights**:
  - 📋 Resumen Ejecutivo
  - 📊 Análisis de Rendimiento
  - ⚠️ Evaluación de Riesgos
  - 💡 Recomendaciones
  - ✅ Fortalezas Clave
  - 🔧 Áreas de Mejora

### 3. Análisis de Agentes

**Formato**: Conversación en stream
**Contenido**: Análisis detallado de cada agente (9 perspectivas)

## ⚙️ Configuración

### Variables de Entorno Requeridas

```env
# .env file
OPENROUTER_API_KEY=sk-or-v1-...  # Para AI insights
OPENAI_API_KEY=sk-proj-...       # Para agentes (opcional, puede usar OpenRouter)
SERPER_API_KEY=...               # Para web search (opcional)
```

### Dependencias

```bash
pip install -r requirements.txt

# Principales:
# - agno (framework de agentes)
# - openai (para LLM)
# - plotly (gráficos interactivos)
# - yfinance (datos de mercado)
# - pandas, numpy (análisis)
# - python-dotenv (variables de entorno)
```

## 🎨 Personalización

### Modificar Agentes

Edita archivos YAML en `agente-agno/agents/`:

```yaml
# advanced_reporter.yaml
model:
  provider: "openrouter"
  model_id: "deepseek/deepseek-chat"  # Cambiar modelo
  temperature: 0.3                     # Ajustar creatividad
```

### Modificar Métricas

Edita `agente-agno/core/metrics.py`:

```python
# Agregar nueva métrica
def calculate_custom_metric(self, equity_series):
    # Tu cálculo aquí
    return custom_value
```

### Modificar Visualizaciones

Edita `agente-agno/core/visualization_plotly.py`:

```python
# Agregar nuevo gráfico
def plot_custom_chart(self, data):
    fig = go.Figure()
    # Tu visualización aquí
    return self._save_chart(fig, 'custom_chart.html')
```

## 💰 Costos

| Componente | Costo por ejecución |
|------------|---------------------|
| 9 Agentes (OpenRouter) | ~$0.001-0.005 |
| Daily Reporter | ~$0.00005 |
| Advanced Reporter (FASE 2) | ~$0.0005 |
| AI Insights (DeepSeek) | ~$0.0005 |
| **Total workflow completo** | **~$0.002-0.006** |

**Costo mensual** (22 días trading): ~$0.04-0.13

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY not set"

```powershell
# PowerShell
$env:OPENROUTER_API_KEY="sk-or-v1-..."

# O agregar a .env
echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env
```

### "Plotly not installed"

```bash
pip install plotly
```

### "Benchmark data unavailable"

- Normal si fines de semana
- Sistema skip Beta/Alpha automáticamente
- Otras métricas siguen funcionando

### "AI insights failed"

- Verifica API key
- Sistema genera reporte sin insights
- No afecta otras secciones

## 📚 Referencias

- **Agno Framework**: `agente-agno/docs/AGNO_README.md`
- **FASE 2 Docs**: `agente-agno/FASE2_IMPLEMENTATION_SUMMARY.md`
- **Gráficos**: `agente-agno/GRAFICOS_INTERACTIVOS.md`
- **AI Insights**: `agente-agno/OPENROUTER_SETUP.md`
- **Changelog**: `agente-agno/CHANGELOG_v3.8.0.md`

## 🎯 Próximos Pasos

1. ✅ Ejecutar workflow example
2. ✅ Revisar reporte HTML generado
3. ✅ Configurar ejecución diaria (cron/task scheduler)
4. ✅ Personalizar agentes según tu estrategia
5. ✅ Agregar alertas automáticas

---

**Versión**: 2.1.0
**Última actualización**: Octubre 2025
**Mantenedor**: Agente Agno Team

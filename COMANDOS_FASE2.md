# COMANDOS PARA FASE 2 - EJECUCIÓN COMPLETA

## 📋 PREREQUISITOS

```powershell
# 1. Activar entorno virtual (SIEMPRE PRIMERO)
.venv\Scripts\Activate.ps1

# 2. Instalar matplotlib (nueva dependencia de Fase 2)
pip install matplotlib

# 3. Verificar instalaciones
pip list | Select-String "matplotlib|yfinance|pandas"
```

**Output esperado:**
```
matplotlib    3.x.x
pandas        2.x.x
yfinance      0.x.x
```

---

## 🧪 TESTING - FASE 2

### Ejecutar Suite Completa de Tests

```powershell
# Test completo de Fase 2 (metrics + visualizations + reports)
python agente-agno/test_phase2.py
```

**Resultado esperado:**
```
╔====================================================================╗
║               FASE 2 TEST SUITE - FULL RUN                        ║
╚====================================================================╝

TEST 1: MetricsCalculator
  ✅ Sharpe (period): X.XX
  ✅ Sharpe (annual): X.XX
  ✅ Sortino (period): X.XX
  ✅ Max Drawdown: -X.XX%
  ✅ Total Trades: XX
  ✅ Win Rate: XX.X%
✅ TEST 1 PASSED

TEST 2: VisualizationGenerator
  ✅ Created: test_output/charts/daily_performance.png
  ✅ Created: test_output/charts/drawdown_analysis.png
  ✅ Created: test_output/charts/composition.png
  ✅ Created: test_output/charts/win_loss_analysis.png
  ✅ Created: test_output/charts/cash_position.png
  ✅ Generated 5 plots
✅ TEST 2 PASSED

TEST 3: HTMLReportGenerator
  ✅ Executive summary HTML generated
  ✅ Performance metrics HTML generated
  ✅ Holdings table HTML generated
  ✅ Full report created: test_output/test_report.html
  ✅ File size: XXX,XXX bytes
  ✅ HTML structure validated
  ✅ Embedded images verified
✅ TEST 3 PASSED

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================
✅ PASS: Metrics Calculator
✅ PASS: Visualization Generator
✅ PASS: Html Reports

Total: 3/3 tests pasados (100.0%)

🎉 ¡TODOS LOS TESTS DE FASE 2 PASARON!

✅ FASE 2 COMPLETADA CON ÉXITO
   • MetricsCalculator: 100% funcional
   • VisualizationGenerator: 100% funcional
   • HTMLReportGenerator: 100% funcional
======================================================================
```

### Archivos Generados por Tests

```powershell
# Ver archivos de prueba generados
ls test_output/charts/
ls test_output/*.html
```

**Archivos creados:**
```
test_output/
├── charts/
│   ├── daily_performance.png
│   ├── drawdown_analysis.png
│   ├── composition.png
│   ├── win_loss_analysis.png
│   └── cash_position.png
└── test_report.html
```

---

## 🚀 EJEMPLO COMPLETO - FASE 2

### Opción 1: Datos de Ejemplo ("Start Your Own")

```powershell
# Generar reporte con datos de plantilla
python agente-agno/fase2_example.py --data-dir "Start Your Own"
```

### Opción 2: Datos Reales ("Scripts and CSV Files")

```powershell
# Generar reporte con datos reales del autor
python agente-agno/fase2_example.py --data-dir "Scripts and CSV Files"
```

### Opción 3: Custom Output Directory

```powershell
# Especificar directorio de salida personalizado
python agente-agno/fase2_example.py --data-dir "Start Your Own" --output "my_reports"
```

**Resultado esperado:**
```
======================================================================
FASE 2: ADVANCED ANALYTICS & REPORTING
======================================================================

[STEP 1] Loading portfolio data...
  ✅ Portfolio: XXX records
  ✅ Trades: XX records

[STEP 2] Calculating equity series...
  ✅ Equity range: $XXX.XX - $XXX.XX
  ✅ Current equity: $XXX.XX

[STEP 3] Fetching S&P 500 benchmark...
[INFO] Fetching S&P 500 data from YYYY-MM-DD to YYYY-MM-DD...
  ✅ Benchmark data: XX days

[STEP 4] Calculating advanced metrics...
  ✅ Sharpe Ratio (annual): X.XX
  ✅ Sortino Ratio (annual): X.XX
  ✅ Beta: X.XX
  ✅ Alpha (annual): XX.X%
  ✅ Max Drawdown: -X.X%
  ✅ Win Rate: XX.X%

[STEP 5] Generating visualizations...
  ✅ Daily performance chart
  ✅ Drawdown analysis chart
  ✅ Performance vs S&P 500 chart
  ✅ Portfolio composition chart
  ✅ Win/loss analysis chart
  ✅ Cash position chart

  📊 Generated 6 charts in: reports/charts

[STEP 6] Generating HTML report...
  ✅ HTML report saved to: reports/report_20250615_HHMMSS.html

======================================================================
✅ FASE 2 COMPLETE!
======================================================================

Generated Files:
  📊 Charts: 6 visualizations in reports/charts
  📄 Report: reports/report_20250615_HHMMSS.html

Key Metrics:
  • Total Equity: $XXX.XX
  • ROI: +XX.XX%
  • Sharpe Ratio: X.XX
  • Max Drawdown: -X.X%
  • Win Rate: XX.X%
```

### Ver Archivos Generados

```powershell
# Listar gráficos generados
ls reports/charts/

# Abrir reporte HTML en navegador
# (Reemplazar YYYYMMDD_HHMMSS con el timestamp real)
start reports/report_YYYYMMDD_HHMMSS.html
```

---

## 📊 USO PROGRAMÁTICO

### En Scripts Propios

```python
# ejemplo_uso.py
from pathlib import Path
import pandas as pd
from core import MetricsCalculator, VisualizationGenerator, HTMLReportGenerator

# 1. Cargar datos
portfolio_df = pd.read_csv("Start Your Own/chatgpt_portfolio_update.csv")
portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])

trades_df = pd.read_csv("Start Your Own/chatgpt_trade_log.csv")
trades_df['Date'] = pd.to_datetime(trades_df['Date'])

# 2. Calcular series
equity = portfolio_df.groupby('Date')['Total Equity'].last()
cash = portfolio_df.groupby('Date')['Cash Balance'].last()

# 3. Calcular métricas
calculator = MetricsCalculator(risk_free_rate=0.05)
metrics = calculator.calculate_all_metrics(equity, trades_df, "^GSPC")

# 4. Generar visualizaciones
viz = VisualizationGenerator(output_dir="mi_reporte/charts")
charts = viz.generate_all_plots(
    portfolio_equity=equity,
    trades_df=trades_df,
    cash_series=cash
)

# 5. Crear reporte HTML
reporter = HTMLReportGenerator()

portfolio_summary = {
    'total_equity': equity.iloc[-1],
    'cash_balance': cash.iloc[-1],
    'total_pnl': equity.iloc[-1] - equity.iloc[0],
    'roi_percent': ((equity.iloc[-1] / equity.iloc[0]) - 1) * 100,
    'num_positions': 3
}

report = reporter.generate_full_report(
    output_path="mi_reporte/informe.html",
    portfolio_summary=portfolio_summary,
    metrics=metrics,
    chart_paths=charts
)

print(f"Reporte generado: {report}")
```

**Ejecutar:**
```powershell
python ejemplo_uso.py
```

---

## 🔍 VERIFICACIÓN DE FASE 2

### Checklist de Funcionalidad

```powershell
# 1. Verificar módulos instalados
python -c "from core import MetricsCalculator, VisualizationGenerator, HTMLReportGenerator; print('✅ Imports OK')"

# 2. Verificar matplotlib
python -c "import matplotlib; print(f'✅ Matplotlib {matplotlib.__version__}')"

# 3. Ejecutar tests
python agente-agno/test_phase2.py

# 4. Generar reporte de ejemplo
python agente-agno/fase2_example.py --data-dir "Start Your Own"

# 5. Verificar archivos generados
ls reports/
ls reports/charts/
```

**Si todo funciona correctamente:**
```
✅ Imports OK
✅ Matplotlib 3.x.x
✅ 3/3 tests pasados (100.0%)
✅ Reporte generado en reports/report_*.html
✅ 6+ gráficos en reports/charts/
```

---

## 🐛 TROUBLESHOOTING

### Problema: matplotlib no instalado

```powershell
# Error: "No module named 'matplotlib'"
# Solución:
pip install matplotlib
```

### Problema: Sin datos de S&P 500

```
[WARNING] No S&P 500 data retrieved
⚠️  Benchmark data unavailable (will skip CAPM)
```

**Causa:** yfinance no pudo descargar datos.

**Solución:**
```powershell
# Verificar conexión a internet
# Reinstalar yfinance
pip install --upgrade yfinance
```

### Problema: CSV no encontrado

```
[ERROR] Portfolio file not found: Start Your Own/chatgpt_portfolio_update.csv
```

**Solución:**
```powershell
# Verificar que el directorio existe
ls "Start Your Own/"

# O usar ruta absoluta
python agente-agno/fase2_example.py --data-dir "d:\full\path\to\Start Your Own"
```

### Problema: Tests fallan

```powershell
# Ver detalles del error
python agente-agno/test_phase2.py

# Limpiar outputs de tests anteriores
rm -r test_output/
```

---

## 📈 MÉTRICAS CALCULADAS

### Sharpe Ratio
- **Qué es:** Retorno ajustado por riesgo
- **Fórmula:** (Return - Risk-free) / Volatility
- **Interpretación:**
  - < 0: Peor que risk-free
  - 0-1: Pobre
  - 1-2: Bueno
  - 2-3: Muy bueno
  - > 3: Excelente

### Sortino Ratio
- **Qué es:** Similar a Sharpe pero solo penaliza volatilidad negativa
- **Interpretación:** Valores más altos = mejor

### Beta
- **Qué es:** Sensibilidad al mercado (S&P 500)
- **Interpretación:**
  - β = 1: Mueve igual que el mercado
  - β > 1: Más volátil que el mercado
  - β < 1: Menos volátil que el mercado

### Alpha
- **Qué es:** Exceso de retorno vs benchmark
- **Interpretación:**
  - α > 0: Beating the market
  - α = 0: Matching the market
  - α < 0: Underperforming

### Max Drawdown
- **Qué es:** Máxima caída desde peak
- **Interpretación:** Más negativo = peor
- **Ejemplo:** -15% significa caída de 15% desde máximo histórico

### Win Rate
- **Qué es:** % de trades ganadores
- **Fórmula:** (Winning Trades / Total Trades) * 100
- **Interpretación:** > 50% es mejor que azar

---

## 📚 RECURSOS ADICIONALES

### Documentación Generada
- `FASE2_IMPLEMENTATION_SUMMARY.md` - Resumen completo de implementación
- Docstrings en cada módulo:
  - `core/metrics.py`
  - `core/visualization.py`
  - `core/html_reports.py`

### Archivos de Ejemplo
- `fase2_example.py` - Script completo con todos los pasos
- `test_phase2.py` - Suite de tests con datos sintéticos

### Archivos de Datos
- `Start Your Own/chatgpt_portfolio_update.csv` - Plantilla vacía
- `Scripts and CSV Files/chatgpt_portfolio_update.csv` - Datos reales

---

## 🎯 PRÓXIMOS PASOS DESPUÉS DE FASE 2

Una vez que FASE 2 funcione correctamente:

1. **Integrar con v3_ultra.py**
   ```powershell
   # Agregar flags para generar reportes
   python agente-agno/v3_ultra.py --generate-report
   ```

2. **Automatizar Reportes Diarios**
   ```powershell
   # Script que se ejecuta cada día
   python daily_report.py
   ```

3. **Continuar con FASE 3**
   - Backtesting engine
   - Interactive trading UI
   - LLM response logging

---

**Versión:** v3.4.0
**Última actualización:** 2025-06-XX
**Estado:** ✅ PRODUCTION READY

# Core Trading System Modules

Módulos reutilizables para el sistema de trading multi-agente.

## 📦 Componentes

### 1. `portfolio.py` - Portfolio Memory Manager
Gestión de portfolio en memoria con persistencia CSV.

**Características:**
- ✅ Tracking de posiciones en tiempo real
- ✅ Logging automático de trades
- ✅ Snapshots diarios persistentes
- ✅ Análisis de rendimiento histórico
- ✅ Gestión de cash y equity

**Uso:**
```python
from core import PortfolioMemoryManager

# Inicializar portfolio
portfolio = PortfolioMemoryManager(initial_cash=100.0)

# Añadir posición
portfolio.add_position("ABEO", 10.0, 5.50, "Initial buy")

# Obtener resumen
summary = portfolio.get_portfolio_summary()
print(f"ROI: {summary['roi']:.2f}%")

# Guardar snapshot diario
portfolio.save_daily_snapshot()
```

---

### 2. `validation.py` - Validation Handler
Lógica de validación centralizada con soporte intelligent dry-run.

**Características:**
- ✅ Validación micro-cap
- ✅ Validación de tamaño de posición
- ✅ Checks de cash reserve
- ✅ Modo dry-run vs live
- ✅ Resultados estructurados

**Uso:**
```python
from core import ValidationHandler

# Inicializar handler
validator = ValidationHandler()

# Validar stock (dry-run: permite continuar con warning)
result = validator.validate_stock("ABEO", dry_run=True)

if result['can_continue']:
    print("Continuando análisis...")
else:
    print(f"Bloqueado: {result['reason']}")

# Modo LIVE (bloquea si falla)
result = validator.validate_stock("NVDA", dry_run=False)
```

---

### 3. `analysis.py` - Stock Analyzer
Orquestación de análisis multi-agente.

**Características:**
- ✅ Carga equipo de 9 agentes desde YAML
- ✅ Construcción de queries contextuales
- ✅ Ejecución con streaming
- ✅ Soporte OpenRouter/DeepSeek

**Uso:**
```python
from core import StockAnalyzer

# Inicializar analyzer
analyzer = StockAnalyzer()

# Analizar stock
portfolio_summary = {
    'cash': 100.0,
    'total_equity': 100.0,
    'roi': 0.0,
    'num_positions': 0
}

analyzer.analyze(
    ticker="ABEO",
    portfolio_summary=portfolio_summary,
    use_openrouter=True,
    stream=True
)
```

---

### 4. `reporting.py` - Daily Reporter
Generación de reportes diarios.

**Características:**
- ✅ Carga Daily Reporter agent desde YAML
- ✅ Formateo de datos de portfolio
- ✅ Reportes comprensivos
- ✅ Soporte streaming

**Uso:**
```python
from core import DailyReporter

# Inicializar reporter
reporter = DailyReporter()

# Generar reporte
reporter.generate_report(
    portfolio_summary=summary,
    holdings_df=portfolio.holdings,
    trades_df=portfolio.trades,
    use_openrouter=True
)
```

---

## 🔄 Flujo Completo

```python
from core import (
    PortfolioMemoryManager,
    ValidationHandler,
    StockAnalyzer,
    DailyReporter
)

# 1. Inicializar componentes
portfolio = PortfolioMemoryManager(initial_cash=100.0)
validator = ValidationHandler()
analyzer = StockAnalyzer()
reporter = DailyReporter()

# 2. Validar stock
validation = validator.validate_stock("ABEO", dry_run=True)

if validation['can_continue']:
    # 3. Analizar con equipo multi-agente
    summary = portfolio.get_portfolio_summary()

    analyzer.analyze(
        ticker="ABEO",
        portfolio_summary=summary,
        holdings_df=portfolio.holdings
    )

    # 4. Generar reporte diario
    reporter.generate_report(
        portfolio_summary=summary,
        holdings_df=portfolio.holdings,
        trades_df=portfolio.trades
    )

    # 5. Guardar snapshot
    portfolio.save_daily_snapshot()
```

---

## 📊 Arquitectura

```
core/
├── __init__.py          # Exports principales
├── portfolio.py         # Gestión de portfolio
├── validation.py        # Validaciones
├── analysis.py          # Análisis multi-agente
└── reporting.py         # Generación de reportes
```

### Dependencias Externas

```python
# Portfolio
pandas >= 1.5.0

# Validation
validators.py           # Sistema original de validación
stop_loss_monitor.py   # Monitor de stop-loss

# Analysis & Reporting
agents/                # Sistema modular de agentes YAML
agno                   # Framework de agentes
```

---

## 🎯 Ventajas de Modularización

### Antes (v2 - Hardcoded):
```python
# 1 archivo monolítico: 1,129 líneas
# Portfolio + Validation + Analysis + Reporting mezclados
# Difícil de testear individualmente
# Alto acoplamiento
```

### Ahora (v3 - Modular):
```python
# 4 módulos separados: ~600 líneas totales
# Responsabilidad única por módulo
# Fácil de testear (imports individuales)
# Bajo acoplamiento
```

---

## 🧪 Testing Individual

```python
# Test Portfolio Manager
from core import PortfolioMemoryManager

portfolio = PortfolioMemoryManager(initial_cash=100.0)
portfolio.add_position("TEST", 1.0, 10.0, "Test trade")
assert portfolio.cash == 90.0

# Test Validation Handler
from core import ValidationHandler

validator = ValidationHandler()
result = validator.validate_stock("ABEO", dry_run=True)
assert result['can_continue'] == True

# Test Stock Analyzer
from core import StockAnalyzer

analyzer = StockAnalyzer()
query = analyzer.build_analysis_query("ABEO", {'cash': 100})
assert "ABEO" in query

# Test Daily Reporter
from core import DailyReporter

reporter = DailyReporter()
formatted = reporter.format_portfolio_summary({'cash': 100, 'roi': 5.2})
assert "5.2" in formatted
```

---

## 📝 Mejores Prácticas

### 1. Siempre usar contexto de portfolio
```python
# ✅ CORRECTO
summary = portfolio.get_portfolio_summary()
analyzer.analyze(ticker="ABEO", portfolio_summary=summary)

# ❌ INCORRECTO (sin contexto)
analyzer.analyze(ticker="ABEO")
```

### 2. Validar antes de analizar
```python
# ✅ CORRECTO
validation = validator.validate_stock("ABEO", dry_run=True)
if validation['can_continue']:
    analyzer.analyze(...)

# ❌ INCORRECTO (análisis sin validación)
analyzer.analyze("ABEO", ...)
```

### 3. Guardar snapshots periódicamente
```python
# ✅ CORRECTO (al final del día)
portfolio.save_daily_snapshot()

# ⚠️ OPCIONAL (después de cada trade)
portfolio.add_position(...)
portfolio.save_daily_snapshot()
```

### 4. Manejar errores gracefully
```python
# ✅ CORRECTO
try:
    analyzer.analyze(...)
except ImportError as e:
    print(f"Agentes no disponibles: {e}")
except Exception as e:
    print(f"Error en análisis: {e}")
```

---

## 🔧 Configuración

### Variables de Entorno
```bash
# OpenRouter API Key
OPENROUTER_API_KEY=your_key_here

# DeepSeek API Key (alternativa)
DEEPSEEK_API_KEY=your_key_here
```

### Directorios
```
agente-agno/
├── core/               # Módulos reutilizables
├── agents/            # Configuraciones YAML de agentes
├── history/           # Archivos CSV de historial
│   ├── portfolio_history.csv
│   ├── trades_history.csv
│   └── daily_summary.csv
└── scripts/           # Scripts ejecutables
    ├── advanced_trading_team_v2.py  # Versión hardcoded
    └── advanced_trading_team_v3.py  # Versión modular
```

---

## 🚀 Migración desde v2

### Paso 1: Import de módulos
```python
# v2 (hardcoded)
class PortfolioMemoryManager:
    # 200 líneas de código...

# v3 (modular)
from core import PortfolioMemoryManager
```

### Paso 2: Validación
```python
# v2 (inline)
validator = TradeValidator()
micro_cap_result = validator.micro_cap.validate(ticker)
if not micro_cap_result.valid:
    if dry_run:
        print("WARNING...")
    else:
        return

# v3 (modular)
from core import ValidationHandler
validator = ValidationHandler()
result = validator.validate_stock(ticker, dry_run=True)
if not result['can_continue']:
    return
```

### Paso 3: Análisis
```python
# v2 (hardcoded team creation)
team = create_trading_team(use_openrouter=True)
query = f"Analiza {ticker}..."
team.print_response(query)

# v3 (modular)
from core import StockAnalyzer
analyzer = StockAnalyzer()
analyzer.analyze(ticker, portfolio_summary, use_openrouter=True)
```

---

## 📚 Recursos Adicionales

- **Agents README**: `agents/README.md` - Documentación del sistema modular de agentes
- **Version Comparison**: `VERSION_COMPARISON.md` - Comparación detallada v2 vs v3
- **Validators**: `validators.py` - Sistema original de validación
- **Stop Loss Monitor**: `stop_loss_monitor.py` - Monitor automático de stop-loss

---

## 🎯 Próximos Pasos

1. ✅ Modularización completa de portfolio (HECHO)
2. ✅ Modularización de validación (HECHO)
3. ✅ Modularización de análisis (HECHO)
4. ✅ Modularización de reporting (HECHO)
5. ⏳ Tests unitarios para cada módulo
6. ⏳ Documentación de API completa
7. ⏳ Ejemplos de uso avanzados

---

**Versión:** 3.0.0
**Última actualización:** Octubre 2025
**Autor:** Romamo

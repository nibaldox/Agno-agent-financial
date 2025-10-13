# Nuevas Funcionalidades: Serper Web Search + Historical Tracking

## Resumen

Se agregaron dos funcionalidades críticas al sistema de trading multi-agente:

1. **Serper Web Search**: Búsqueda web para inteligencia de mercado en tiempo real
2. **Historical Tracking**: Sistema de persistencia CSV para aprender de operaciones pasadas

---

## 1. Serper Web Search Integration

### ¿Qué es Serper?

Serper.dev es una API de búsqueda de Google que proporciona:
- Búsqueda web general (`search_web`)
- Búsqueda de noticias (`search_news`)
- Búsqueda académica (`search_scholar`)
- Scraping de páginas web (`scrape_webpage`)

### ¿Por qué Serper?

**YFinance** proporciona datos financieros históricos y fundamentales, pero:
- ❌ NO tiene sentiment analysis en tiempo real
- ❌ NO incluye noticias de última hora (<24 horas)
- ❌ NO captura análisis de expertos/medios
- ❌ NO detecta eventos corporativos emergentes

**Serper** complementa YFinance con:
- ✅ Noticias recientes (<7 días)
- ✅ Análisis de expertos y opiniones
- ✅ Tendencias del sector
- ✅ Eventos corporativos (earnings, productos, regulaciones)

### Configuración

#### Paso 1: Obtener API Key (Gratis)

1. Visita: https://serper.dev/
2. Crea una cuenta (gratis, sin tarjeta)
3. Copia tu API key del dashboard
4. Beneficios: 2,500 búsquedas gratis/mes

#### Paso 2: Agregar a .env

```bash
# En el archivo .env del proyecto
SERPER_API_KEY=tu_api_key_aqui
```

#### Paso 3: Verificar Instalación

```bash
# Ejecutar test de Serper
python agente-agno/tests/test_serper.py
```

**Salida esperada:**
```
[OK] SERPER_API_KEY encontrada: e247baff1f...
[OK] SerperTools importado correctamente
[OK] SerperTools instanciado correctamente
[SUCCESS] SerperTools está listo para usar con Agno!
```

### Integración en el Sistema

Serper se integra automáticamente en el **Market Researcher Agent**:

```python
# advanced_trading_team_v2.py - create_market_researcher()

tools: list = [
    YFinanceTools(include_tools=[
        "get_current_stock_price",
        "get_company_info",
        "get_company_news",
        "get_historical_stock_prices",
        "get_stock_fundamentals",
        "get_analyst_recommendations"
    ])
]

# Agregar Serper si está disponible
if SERPER_AVAILABLE and os.getenv("SERPER_API_KEY"):
    tools.append(SerperTools())
    print("[INFO] Serper Web Search habilitado para Market Researcher")
```

### Estrategia de Búsqueda del Agent

El Market Researcher ahora incluye instrucciones específicas para Serper:

```markdown
**Estrategia de Búsqueda Web (Serper):**
1. Buscar noticias recientes (<7 días) sobre la empresa
2. Buscar análisis de expertos y opiniones de analistas
3. Buscar tendencias del sector y competidores
4. Buscar eventos corporativos (earnings, nuevos productos, regulaciones)
5. SIEMPRE mencionar la fuente y fecha de las noticias encontradas
```

### Ejemplo de Uso

Cuando ejecutas un análisis:

```bash
python agente-agno/scripts/advanced_trading_team_v2.py --ticker AAPL
```

El Market Researcher ahora:

1. **YFinance**: Obtiene precio, fundamentales, históricos
2. **Serper**: Busca noticias recientes, sentiment, análisis de expertos
3. **Combina**: Genera análisis completo con contexto de mercado

**Output mejorado:**
```
Market Researcher:
  - Precio actual: $175.43 (YFinance)
  - P/E Ratio: 28.5 (YFinance)
  - Últimas noticias: "Apple anuncia nuevo chip M4..." (Serper - hace 2 días)
  - Sentiment de analistas: 78% positivo (Serper)
  - Tendencia del sector: Tecnología +3.2% esta semana (Serper)
```

---

## 2. Historical Tracking System

### ¿Qué es Historical Tracking?

Sistema de persistencia CSV que guarda:
- 📊 **Portfolio Snapshots**: Estado completo del portafolio diariamente
- 📈 **Trade History**: Registro de todas las operaciones (BUY/SELL)
- 📉 **Daily Summaries**: Métricas de performance diarias

### ¿Por qué Historical Tracking?

**Problema anterior:**
- Sistema solo mantenía estado en memoria (DataFrame)
- No había aprendizaje entre sesiones
- No se podían analizar patrones de trading
- No se podía calcular drawdown máximo

**Solución actual:**
- ✅ Persistencia CSV automática
- ✅ Aprendizaje de operaciones pasadas
- ✅ Análisis de patrones (qué funciona/qué no)
- ✅ Métricas históricas (ROI, win rate, drawdown)

### Archivos Generados

El sistema crea 3 archivos CSV en `agente-agno/history/`:

#### 1. `portfolio_state.csv` (Portfolio Snapshots)
```csv
date,cash,initial_cash,total_equity,roi,num_positions
2025-06-01,100.00,100.00,100.00,0.00,0
2025-06-02,50.00,100.00,125.50,25.50,2
2025-06-03,50.00,100.00,132.75,32.75,2
```

#### 2. `trades_history.csv` (All Trades)
```csv
date,ticker,action,shares,price,cost,cash_after,reason
2025-06-01,AAPL,BUY,10,25.00,250.00,50.00,Strong fundamentals
2025-06-02,TSLA,BUY,5,30.00,150.00,50.00,Technical breakout
2025-06-03,AAPL,SELL,10,27.50,275.00,325.00,Stop loss hit
```

#### 3. `daily_summary.csv` (Daily Metrics)
```csv
date,cash,invested,total_equity,total_pnl,roi,num_positions
2025-06-01,100.00,0.00,100.00,0.00,0.00,0
2025-06-02,50.00,400.00,450.50,50.50,50.50,2
2025-06-03,325.00,150.00,475.00,75.00,75.00,1
```

### Métricas Calculadas

El sistema calcula automáticamente:

```python
historical_perf = PORTFOLIO.get_historical_performance()
# Retorna:
{
    'total_days': 45,              # Días operando
    'best_day': 15.5,              # Mejor día (%)
    'worst_day': -8.2,             # Peor día (%)
    'peak_equity': 1250.75,        # Equity máxima alcanzada
    'max_drawdown': -12.5,         # Drawdown máximo (%)
    'total_trades': 23,            # Total operaciones
    'winning_trades': 15,          # Operaciones ganadoras
    'win_rate': 65.2,              # % operaciones ganadoras
    'avg_return': 3.2,             # Retorno promedio por operación (%)
    'current_roi': 45.8            # ROI actual
}
```

### Integración Automática

El sistema guarda snapshots automáticamente:

```python
# En analyze_stock() y run_daily_analysis()
def analyze_stock(ticker: str):
    # ... análisis del stock ...
    
    # Auto-save snapshot después del análisis
    PORTFOLIO.save_daily_snapshot()  # ← Automático
```

### Portfolio Manager con Contexto Histórico

El Portfolio Manager ahora recibe contexto histórico:

```python
def create_portfolio_manager():
    # Obtener métricas históricas
    historical_perf = PORTFOLIO.get_historical_performance()
    
    instructions = f"""
    **CONTEXTO HISTÓRICO DE TU PORTAFOLIO:**
    - Total Días Operando: {historical_perf['total_days']}
    - Peak Equity: ${historical_perf['peak_equity']:.2f}
    - Max Drawdown: {historical_perf['max_drawdown']:.2f}%
    - Total Operaciones: {historical_perf['total_trades']}
    - Win Rate: {historical_perf['win_rate']:.1f}%
    
    **USA EL HISTORIAL para:**
    1. Identificar patrones de éxito/fracaso
    2. Ajustar sizing basado en drawdown máximo
    3. Evitar repetir errores pasados
    4. Replicar estrategias exitosas
    """
```

### Comandos CLI

#### Ver Historial Completo

```bash
python agente-agno/scripts/advanced_trading_team_v2.py --show-history
```

**Output:**
```
================================================================================
HISTÓRICO DEL PORTAFOLIO
================================================================================

Estado Actual:
  Total Equity: $145.75
  ROI: +45.75%
  Cash: $25.00
  Posiciones: 3

Estadísticas Históricas:
  Total Días: 45
  Peak Equity: $152.30
  Max Drawdown: -8.5%
  Total Operaciones: 23
  Win Rate: 65.2%

Mejor/Peor Día:
  Mejor: +15.5% (2025-06-15)
  Peor: -8.2% (2025-07-03)

Últimas 10 Operaciones:
  [2025-07-20] AAPL BUY 10 @ $175.00 - Strong fundamentals
  [2025-07-19] TSLA SELL 5 @ $280.00 - Take profit
  ...
```

### Testing

```bash
# Test completo del sistema
python agente-agno/tests/test_complete_system.py

# Output esperado:
# ✓ TEST 1: SISTEMA DE HISTÓRICO - PASS
# ✓ TEST 2: INTEGRACIÓN SERPER - PASS
# ✓ TEST 3: ANÁLISIS COMPLETO - PASS (opcional)
```

---

## Flujo de Datos Actualizado

```
┌─────────────────────────────────────────────────────────────┐
│                    ANÁLISIS DE STOCK                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Market Researcher (DeepSeek)                               │
│    Tools:                                                   │
│      - YFinance (6 tools): Precio, Info, News, Histórico   │
│      - Serper: Web search, News, Sentiment                 │
│    Output: Análisis completo con contexto web              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Risk Analyst (DeepSeek)                                    │
│    Tools: YFinance (3 tools): Ratios, Indicators           │
│    Output: Evaluación de riesgo con datos reales           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Trading Strategist (DeepSeek)                              │
│    Tools: YFinance (3 tools): Technical, Fundamental        │
│    Output: Recomendación BUY/SELL/HOLD                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Portfolio Manager (OpenRouter Qwen3 235B)                  │
│    Contexto Histórico:                                      │
│      - Total días operando                                  │
│      - Peak equity, Max drawdown                            │
│      - Win rate, Total trades                               │
│    Output: Decisión final con gestión de riesgo            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Daily Reporter (OpenRouter GLM 4.5 Air)                    │
│    Output: Reporte profesional en ESPAÑOL                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         AUTO-SAVE SNAPSHOT (Historical Tracking)            │
│    Archivos actualizados:                                   │
│      - portfolio_state.csv                                  │
│      - trades_history.csv                                   │
│      - daily_summary.csv                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Ventajas del Sistema Completo

### Antes (Solo YFinance)
```
Market Researcher → Risk Analyst → Strategist → Portfolio Manager → Reporter
      ↓                  ↓              ↓              ↓
  Financial Data   Financial Data  Financial Data   No History
  
Limitaciones:
  ❌ Solo datos financieros (sin contexto de mercado)
  ❌ No sentiment analysis
  ❌ No aprendizaje entre sesiones
  ❌ No métricas de performance históricas
```

### Ahora (YFinance + Serper + Historical)
```
Market Researcher → Risk Analyst → Strategist → Portfolio Manager → Reporter
      ↓                  ↓              ↓              ↓
  YFinance          YFinance        YFinance      Historical Data
  + Serper                                        (45 días, win rate, etc.)
  
Capacidades:
  ✅ Datos financieros + contexto de mercado
  ✅ Sentiment analysis en tiempo real
  ✅ Aprendizaje de operaciones pasadas
  ✅ Métricas completas de performance
  ✅ Decisiones basadas en datos históricos
```

---

## Troubleshooting

### Serper no funciona

**Problema:** `[WARNING] SERPER_API_KEY no encontrada`

**Solución:**
1. Verifica `.env`: `cat .env | grep SERPER`
2. Obtén API key: https://serper.dev/
3. Agrega a `.env`: `SERPER_API_KEY=tu_key`
4. Reinicia el script

**Problema:** `Import "agno.tools.serper" could not be resolved`

**Solución:**
```bash
pip install agno[serper]
# o
pip install --upgrade agno
```

### Historical Tracking no guarda

**Problema:** No se crean archivos CSV en `agente-agno/history/`

**Solución:**
1. Verifica que `PORTFOLIO` se inicialice con `history_file`:
   ```python
   PORTFOLIO = PortfolioMemoryManager(
       initial_cash=100.0, 
       history_file=str(HISTORY_DIR / "portfolio_state.csv")
   )
   ```

2. Verifica permisos de escritura en `agente-agno/history/`

3. Ejecuta un análisis completo:
   ```bash
   python agente-agno/scripts/advanced_trading_team_v2.py --ticker AAPL
   ```

4. Verifica archivos creados:
   ```bash
   ls agente-agno/history/
   ```

---

## Próximos Pasos

### Usar el sistema completo

```bash
# 1. Inicializar demo
python agente-agno/scripts/advanced_trading_team_v2.py --init-demo

# 2. Análisis diario (usa Serper + guarda historial)
python agente-agno/scripts/advanced_trading_team_v2.py --daily

# 3. Ver historial acumulado
python agente-agno/scripts/advanced_trading_team_v2.py --show-history

# 4. Analizar stock específico
python agente-agno/scripts/advanced_trading_team_v2.py --ticker NVDA
```

### Monitorear Performance

```bash
# Ver archivos de historial
cat agente-agno/history/daily_summary.csv

# Ver última operación
tail -n 1 agente-agno/history/trades_history.csv

# Calcular ROI total
python -c "from agente_agno.scripts.advanced_trading_team_v2 import PORTFOLIO; print(f'ROI: {PORTFOLIO.get_historical_performance()[\"current_roi\"]:.2f}%')"
```

---

## Resumen Técnico

| Característica | Implementación | Beneficio |
|---------------|----------------|-----------|
| **Serper Web Search** | `SerperTools()` en Market Researcher | Inteligencia de mercado en tiempo real |
| **Historical CSV** | Auto-save después de cada análisis | Persistencia y aprendizaje |
| **Métricas Históricas** | `get_historical_performance()` | Win rate, drawdown, ROI |
| **Contexto Portfolio** | Historical data en Portfolio Manager | Decisiones basadas en datos |
| **CLI --show-history** | Comando para ver métricas | Monitoreo fácil |

---

## Conclusión

El sistema ahora combina:
- **9 herramientas YFinance**: Datos financieros completos
- **Serper web search**: Contexto de mercado en tiempo real
- **Historical tracking**: Aprendizaje de operaciones pasadas
- **5 agentes especializados**: Análisis multi-perspectiva
- **Reportes en español**: Output profesional

**Resultado:** Sistema de trading multi-agente de nivel profesional que aprende y mejora con cada operación. 🚀

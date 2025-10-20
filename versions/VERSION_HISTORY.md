# 📚 Historial de Versiones - Sistema de Backtesting

## 📌 Versión 2.0.0 - OPTIMIZADA (2025-10-18)

### 🎯 Objetivos
Mejorar el rendimiento del sistema de backtesting mediante:
- Gestión de riesgo automática
- Indicadores técnicos avanzados
- Reglas de trading más estrictas
- Position sizing dinámico

### 🆕 Nuevas Características

#### 1. Stop Loss / Take Profit Automáticos
- **Stop Loss:** Cierre automático al alcanzar -3% de pérdida
- **Take Profit:** Cierre automático al alcanzar +5% de ganancia
- Se ejecutan ANTES de cada decisión del LLM
- Registrados en `auto_closes` para análisis

**Código:**
```python
# En TradingSimulator
self.stop_loss_pct = 0.03  # 3%
self.take_profit_pct = 0.05  # 5%

# Verificación automática
auto_sales = self.simulator.check_risk_limits(current_prices, timestamp)
```

#### 2. Indicadores Técnicos Avanzados
- **EMA (12, 26):** Exponential Moving Averages
- **MACD:** Moving Average Convergence Divergence
- **Bollinger Bands:** Bandas de 20 períodos, 2 desviaciones
- **ATR:** Average True Range para medir volatilidad

**Método:** `calculate_advanced_indicators()`

#### 3. Prompt Mejorado del LLM
- Reglas de trading estrictas y verificables
- Condiciones específicas para BUY/SELL/HOLD
- Prohibiciones explícitas (no operar con bajo volumen, RSI alto, etc.)
- Formato de respuesta más estructurado

**Reglas BUY:**
1. EMA12 > EMA26
2. MACD > MACD Signal
3. RSI entre 30-65
4. Precio > SMA 4h
5. Volumen > 0.5x promedio

**Reglas SELL:**
1. Pérdida > 2.5%
2. Ganancia > 4%
3. MACD cruce bajista
4. Precio < EMA 26

#### 4. Position Sizing Dinámico
Ajusta el tamaño de posición según volatilidad:
```python
if ATR > 5000:  max_risk = 15%
elif ATR > 3000:  max_risk = 20%
else:  max_risk = 25%
```

#### 5. Filtro de Volumen
- No opera si volumen < 0.3x promedio
- Evita trades en momentos de baja liquidez

### 📁 Archivos Modificados

**Nuevos:**
- `hourly_backtest_v2_optimized.py` - Engine con mejoras
- `btc_deepseek_auto_v2.py` - Script de ejecución V2
- `versions/VERSION_HISTORY.md` - Este archivo

**Mantenidos (V1):**
- `hourly_backtest.py` - Versión original sin cambios
- `btc_deepseek_auto.py` - Script original

### 🔬 Experimento de Comparación

**Configuración común:**
- Ticker: BTC-USD
- Período: 60 días
- Intervalo: 1 hora
- Capital: $10,000
- Modelo: DeepSeek V3

**Hipótesis:**
La V2 optimizada debería superar a V1 en:
- Retorno total (target: +10-15% vs -3%)
- Win rate (target: 55-60% vs 45%)
- Max drawdown (target: <10%)
- Sharpe ratio (target: >1.5)

### 📊 Cómo Ejecutar

```bash
# Versión 1 (Original)
python3 btc_deepseek_auto.py

# Versión 2 (Optimizada)
python3 btc_deepseek_auto_v2.py
```

### 📈 Generar Dashboard

```bash
# Para V1
python3 generate_dashboard.py btc_30d_4h_deepseek.json

# Para V2
python3 generate_dashboard.py btc_60d_1h_deepseek_v2_optimized.json
```

### 🔍 Análisis Esperado

**Métricas V1 (Baseline):**
- Retorno: -3.23%
- Win Rate: 45%
- Total Trades: ~40
- Comportamiento: Muy conservador, muchos HOLD

**Expectativas V2:**
- Retorno: +10-15%
- Win Rate: 55-60%
- Total Trades: 50-70
- Comportamiento: Más activo pero controlado
- Stop Loss triggered: 5-10 veces
- Take Profit triggered: 10-15 veces

---

## 📌 Versión 1.0.0 - BASELINE (2025-10-17)

### Características Base
- Datos horarios de yfinance
- Indicadores básicos: SMA, RSI, Volumen
- Soporte para fracciones de acciones
- Prompt genérico para LLM
- Sin gestión de riesgo automática
- Position size fijo (25% del efectivo)

### Archivos
- `hourly_backtest.py` - Engine original
- `btc_deepseek_auto.py` - Script de ejecución
- `visualize_backtest.py` - Visualización básica

### Resultados Conocidos
**Simulación 30d, 4h:**
- Capital inicial: $10,000
- Capital final: $9,677
- Retorno: -3.23%
- Win rate: ~45%
- Total decisiones: 173
- BUY: 40
- SELL: 38
- HOLD: 95 (54.9%)

**Problemas Identificados:**
1. Demasiado conservador (54.9% HOLD)
2. Sin gestión de riesgo
3. Indicadores limitados
4. Prompt ambiguo
5. Position sizing no optimizado
6. Opera con volumen cero

---

## 🔄 Roadmap Futuro

### Versión 2.1 (Próxima)
- [ ] Multi-timeframe analysis (1h + 4h + 1d)
- [ ] Trailing stop loss
- [ ] Profit factor optimization
- [ ] Backtesting con múltiples tickers simultáneos

### Versión 2.2
- [ ] ML para predecir win rate
- [ ] Optimización de parámetros (grid search)
- [ ] Paper trading en vivo
- [ ] Alertas en tiempo real

### Versión 3.0
- [ ] Estrategias alternativas (mean reversion, breakout)
- [ ] Portfolio diversificado
- [ ] Risk parity
- [ ] Backtesting con costos reales (slippage, spread)

---

## 📝 Notas de Desarrollo

### Lecciones Aprendidas V1 → V2

1. **LLMs necesitan reglas estrictas**: Prompts ambiguos → decisiones inconsistentes
2. **Gestión de riesgo es crítica**: Sin stop loss → pérdidas no controladas
3. **Indicadores simples no bastan**: SMA solo → señales tardías
4. **Volumen importa**: Operar sin liquidez → ejecución problemática
5. **Position sizing afecta rendimiento**: Tamaño fijo → no se adapta a condiciones

### Principios de Diseño

- **Documentar todo**: Cada versión debe ser reproducible
- **Comparación justa**: Mismos datos, mismo período
- **Separación de concerns**: Engine ≠ Estrategia ≠ Ejecución
- **Métricas claras**: Definir éxito antes de implementar
- **Iteración rápida**: Versiones pequeñas, testeo frecuente

---

## 🤝 Contribuciones

Para agregar nuevas versiones:

1. Copiar versión base: `cp hourly_backtest_v2.py hourly_backtest_v3.py`
2. Documentar cambios en este archivo
3. Actualizar número de versión en header
4. Ejecutar experimentos comparativos
5. Guardar resultados en `results/vX/`

---

**Última actualización:** 2025-10-18
**Autor:** Sistema de Backtesting Automatizado
**Licencia:** MIT

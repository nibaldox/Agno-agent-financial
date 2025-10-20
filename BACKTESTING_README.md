# 🎯 Sistema de Backtesting con IA - Simulación Temporal

Sistema avanzado de backtesting que simula trading con agentes LLM presentando datos históricos **gradualmente** para evitar sesgos de "ver el futuro".

## 🌟 Características Principales

- ✅ **Simulación temporal realista** - El LLM solo ve datos hasta la fecha actual
- ✅ **Sin sesgos de futuro** - Decisiones basadas en información disponible
- ✅ **Múltiples modelos LLM** - Compara diferentes estrategias
- ✅ **Gestión de portfolio completa** - Compra/venta con comisiones
- ✅ **Métricas profesionales** - Win rate, profit factor, drawdown
- ✅ **Visualización de resultados** - Gráficos de equity curve y distribución
- ✅ **Exportación de datos** - Resultados en JSON para análisis posterior

## 📦 Archivos del Sistema

```
backtest_simulator.py       # Motor principal de backtesting
quick_backtest.py           # Tests rápidos predefinidos
visualize_backtest.py       # Visualización de resultados
interactive_trading_agent.py # Sistema interactivo (complementario)
```

## 🚀 Quick Start

### 1. Ejecutar Test Rápido

```bash
python3 quick_backtest.py
```

Opciones disponibles:
- Test AAPL (3 meses)
- Test Portfolio FAANG (6 meses)  
- Comparar modelos LLM

### 2. Simulación Personalizada

```bash
python3 backtest_simulator.py
```

Te pedirá:
- **Tickers** a analizar (ej: AAPL,MSFT,GOOGL)
- **Fechas** de inicio y fin (ej: 2024-01-01 a 2024-12-31)
- **Intervalo** de decisiones (ej: 7 días)
- **Capital** inicial (ej: 10000)
- **Modelo LLM** a usar (Reasoning, Advanced, etc.)

### 3. Visualizar Resultados

```bash
python3 visualize_backtest.py backtest_results.json
```

Genera:
- Reporte detallado en consola
- Gráfico de equity curve
- Distribución de P&L

### 4. Comparar Múltiples Simulaciones

```bash
python3 visualize_backtest.py compare backtest_*.json
```

## 📊 Ejemplo de Uso Completo

```bash
# 1. Ejecutar simulación
python3 backtest_simulator.py
# Ingresar: AAPL,MSFT
# Período: 2024-01-01 a 2024-10-01
# Intervalo: 7 días
# Capital: 10000

# 2. Visualizar resultados
python3 visualize_backtest.py backtest_results.json

# 3. Comparar con otro modelo
python3 backtest_simulator.py
# (usar mismo período pero modelo diferente)

# 4. Comparar ambos
python3 visualize_backtest.py compare backtest_*.json
```

## 🧠 Cómo Funciona

### Flujo de Simulación

```
1. DESCARGA DE DATOS
   ↓
   Obtiene datos históricos completos de Yahoo Finance
   
2. ITERACIÓN TEMPORAL
   ↓
   Por cada fecha de decisión (ej: cada 7 días):
   
   a) FILTRAR DATOS
      Solo muestra datos hasta fecha actual (sin futuro)
   
   b) CONTEXTO DE MERCADO
      - Precio actual
      - Indicadores técnicos (SMA 5, 20)
      - Volumen, tendencia
      - Estado del portfolio
   
   c) CONSULTA AL LLM
      Pregunta: "¿Qué debo hacer con este stock?"
      LLM responde: BUY / SELL / HOLD + razón
   
   d) EJECUCIÓN
      - Si BUY: calcula shares, ejecuta compra
      - Si SELL: calcula % a vender, ejecuta venta
      - Si HOLD: no hace nada
   
   e) REGISTRO
      Guarda operación, actualiza portfolio
   
3. ANÁLISIS FINAL
   ↓
   Calcula métricas de desempeño
```

### Prevención de Sesgos

El sistema **garantiza** que el LLM no pueda "ver el futuro":

```python
# ❌ INCORRECTO (con sesgo)
data = get_all_historical_data()
llm.decide(data)  # LLM ve todo el período

# ✅ CORRECTO (sin sesgo)
data_until_today = get_data_until(current_date)
llm.decide(data_until_today)  # Solo ve hasta hoy
```

## 📈 Métricas Calculadas

### Métricas de Retorno
- **Total Return**: Ganancia/pérdida absoluta
- **Total Return %**: Retorno porcentual
- **Equity Curve**: Evolución del capital

### Métricas de Trading
- **Total Trades**: Número de operaciones
- **Win Rate**: % de operaciones ganadoras
- **Winning Trades**: Operaciones exitosas
- **Losing Trades**: Operaciones fallidas

### Métricas de Calidad
- **Average Win**: Ganancia promedio por trade ganador
- **Average Loss**: Pérdida promedio por trade perdedor
- **Profit Factor**: Ratio ganancia/pérdida (>1 es bueno)

## 🎯 Modelos LLM Disponibles

### 1. **DeepSeek Chimera** (Recomendado)
- 🎯 Razonamiento paso a paso
- ⚡ Velocidad: 15-25s
- 💰 Gratis con OpenRouter

### 2. **Qwen3 235B** (Estrategia Avanzada)
- 🧠 235B parámetros
- 📊 Análisis profundo
- ⚡ Velocidad: 20-40s
- 💰 Gratis con OpenRouter

### 3. **Tongyi DeepResearch**
- 🔬 Investigación detallada
- ⚡ Velocidad: 7-10s
- 💰 Gratis con OpenRouter

## 📝 Formato de Resultados JSON

```json
{
  "config": {
    "tickers": ["AAPL", "MSFT"],
    "start_date": "2024-01-01",
    "end_date": "2024-10-01",
    "initial_capital": 10000,
    "decision_interval": 7
  },
  "trades": [
    {
      "date": "2024-01-15",
      "action": "BUY",
      "ticker": "AAPL",
      "shares": 10,
      "price": 185.50,
      "cost": 1855.00,
      "fee": 1.86,
      "reason": "Tendencia alcista, SMA 5 > SMA 20"
    }
  ],
  "equity_curve": [
    {"date": "2024-01-15", "value": 10000, "cash": 8143.14}
  ],
  "final_metrics": {
    "total_return": 1250.50,
    "total_return_pct": 12.51,
    "win_rate": 65.5,
    "profit_factor": 1.85
  }
}
```

## 🔧 Configuración Avanzada

### Ajustar Parámetros de Trading

Edita `backtest_simulator.py`:

```python
class TradingSimulator:
    def __init__(
        self,
        initial_capital: float = 10000.0,
        transaction_cost: float = 0.001,  # 0.1% comisión
    ):
```

### Modificar Contexto del LLM

En `prepare_market_context()` puedes agregar más indicadores:

```python
# Ejemplo: agregar RSI
rsi = calculate_rsi(data['Close'])
context += f"RSI: {rsi:.2f}\n"
```

### Cambiar Lógica de Decisión

En `_parse_llm_response()` puedes modificar cómo se interpretan las decisiones.

## 🎓 Casos de Uso

### 1. Evaluar Diferentes Modelos LLM
```bash
# Probar modelo 1
python3 quick_backtest.py
# Opción 3: Comparar modelos

# Resultado: ¿Qué modelo tiene mejor win rate?
```

### 2. Optimizar Intervalo de Decisiones
```bash
# Test con decisiones diarias (interval=1)
# Test con decisiones semanales (interval=7)
# Test con decisiones mensuales (interval=30)

# Comparar: ¿Qué intervalo es más rentable?
```

### 3. Evaluar Portfolio vs Single Stock
```bash
# Test 1: Solo AAPL
# Test 2: AAPL + MSFT + GOOGL

# Comparar: ¿Diversificación mejora resultados?
```

### 4. Análisis de Períodos Volátiles
```bash
# Período alcista: 2023-01-01 a 2023-06-01
# Período bajista: 2022-01-01 a 2022-06-01

# Comparar: ¿Cómo se desempeña en diferentes mercados?
```

## 📊 Interpretación de Resultados

### Profit Factor
- **> 2.0**: Excelente
- **1.5 - 2.0**: Muy bueno
- **1.0 - 1.5**: Aceptable
- **< 1.0**: Perdedor

### Win Rate
- **> 60%**: Excelente
- **50% - 60%**: Bueno
- **40% - 50%**: Aceptable
- **< 40%**: Necesita mejoras

### Total Return %
- **> 20%**: Excepcional (anualizado)
- **10% - 20%**: Muy bueno
- **5% - 10%**: Bueno
- **< 5%**: Por debajo del mercado

## ⚠️ Limitaciones

1. **Datos de Yahoo Finance**
   - Puede tener gaps o errores
   - No incluye dividendos (puedes agregar)

2. **Comisiones Simplificadas**
   - Usa comisión fija del 0.1%
   - No considera slippage

3. **Ejecución Perfecta**
   - Asume que todas las órdenes se ejecutan
   - Precio de cierre del día

4. **Sin Short Selling**
   - Solo compra/venta de acciones
   - No soporta apalancamiento

## 🔮 Mejoras Futuras

- [ ] Agregar stop-loss automático
- [ ] Soportar dividendos
- [ ] Incluir análisis de drawdown
- [ ] Agregar Sharpe ratio
- [ ] Múltiples agentes en paralelo
- [ ] Optimización de hiperparámetros
- [ ] Dashboard web interactivo
- [ ] Alertas en tiempo real

## 💡 Tips y Mejores Prácticas

1. **Empieza con períodos cortos** (3-6 meses) para pruebas rápidas
2. **Usa intervalos de 7 días** como baseline
3. **Compara siempre con buy & hold** como benchmark
4. **Prueba múltiples modelos** para validar consistencia
5. **Guarda todos los resultados** para análisis posterior
6. **Analiza los trades perdedores** para mejorar prompts
7. **No sobre-optimices** con un solo período

## 🤝 Contribuciones

Ideas para contribuir:
- Agregar más indicadores técnicos
- Mejorar prompts del LLM
- Implementar más métricas
- Crear dashboard web
- Agregar backtesting walk-forward

## 📚 Recursos Adicionales

- [Documentación de yfinance](https://pypi.org/project/yfinance/)
- [Agno Framework Docs](https://docs.agno.com/)
- [OpenRouter Models](https://openrouter.ai/models)

## 🎉 Conclusión

Este sistema te permite:
- ✅ **Evaluar objetivamente** el desempeño de agentes LLM
- ✅ **Sin sesgos** de "ver el futuro"
- ✅ **Métricas profesionales** de trading
- ✅ **Comparar estrategias** fácilmente
- ✅ **Iterar y mejorar** tus prompts

---

**¡Empieza a hacer backtesting ahora!** 🚀

```bash
python3 quick_backtest.py
```

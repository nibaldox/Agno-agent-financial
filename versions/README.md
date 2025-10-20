# 🎯 Guía Rápida de Versiones

## 📂 Estructura de Archivos

```
Agno-agent-financial/
│
├── hourly_backtest.py              # ✅ V1 - Original
├── hourly_backtest_v2_optimized.py # 🚀 V2 - Optimizada
├── btc_deepseek_auto.py            # V1 runner
├── btc_deepseek_auto_v2.py         # V2 runner
│
├── versions/
│   ├── VERSION_HISTORY.md          # Historial completo
│   └── README.md                   # Este archivo
│
├── generate_dashboard.py           # Visualización HTML
├── visualize_backtest.py           # Visualización básica
│
└── results/                        # Resultados de ejecuciones
    ├── btc_30d_4h_deepseek.json   # V1
    └── btc_60d_1h_deepseek_v2_optimized.json  # V2
```

## 🚀 Ejecución Rápida

### Versión 1 (Original)
```bash
python3 btc_deepseek_auto.py
```
**Output:** `btc_30d_4h_deepseek.json`

### Versión 2 (Optimizada) ⭐ RECOMENDADA
```bash
python3 btc_deepseek_auto_v2.py
```
**Output:** `btc_60d_1h_deepseek_v2_optimized.json`

## 📊 Visualizar Resultados

### Dashboard HTML Interactivo
```bash
python3 generate_dashboard.py <archivo.json>
```
**Output:** `<archivo>_dashboard.html`

Abre el HTML en tu navegador para ver:
- 📈 Gráficos interactivos con Plotly
- 💰 KPIs animados
- 📋 Tabla de operaciones
- 🎯 Distribución de decisiones

### Visualización Básica
```bash
python3 visualize_backtest.py <archivo.json>
```

## 🔬 Comparación de Versiones

| Feature | V1 Original | V2 Optimizada |
|---------|-------------|---------------|
| **Stop Loss/Take Profit** | ❌ Manual | ✅ Automático (-3%/+5%) |
| **Indicadores** | SMA, RSI básico | ✅ EMA, MACD, Bollinger, ATR |
| **Reglas Trading** | ❌ Genéricas | ✅ Estrictas y verificables |
| **Position Sizing** | ❌ Fijo (25%) | ✅ Dinámico (15-25%) |
| **Filtro Volumen** | ❌ No | ✅ Sí (>0.3x) |
| **Prompt LLM** | Básico | ✅ Avanzado con reglas |
| **Gestión Riesgo** | ❌ Manual | ✅ Automática |

## 📈 Resultados Históricos

### V1 - Baseline (30 días, 4h)
- **Retorno:** -3.23%
- **Win Rate:** 45%
- **Total Trades:** 40
- **Comportamiento:** Muy conservador (54.9% HOLD)

### V2 - Optimizada (60 días, 1h) 🎯 OBJETIVO
- **Retorno Target:** +10-15%
- **Win Rate Target:** 55-60%
- **Total Trades Target:** 50-70
- **Comportamiento:** Activo pero controlado

## 🎓 Para Qué Usar Cada Versión

### Usa V1 si:
- ✅ Quieres el baseline para comparar
- ✅ Necesitas simplicidad
- ✅ Estás aprendiendo el sistema

### Usa V2 si: ⭐
- ✅ Buscas mejores resultados
- ✅ Quieres gestión de riesgo automática
- ✅ Necesitas indicadores avanzados
- ✅ Vas a hacer trading real

## 🔧 Crear Nueva Versión

```bash
# 1. Copiar versión base
cp hourly_backtest_v2_optimized.py hourly_backtest_v3.py
cp btc_deepseek_auto_v2.py btc_deepseek_auto_v3.py

# 2. Modificar archivos
# - Actualizar imports en runner
# - Cambiar número de versión en headers
# - Implementar mejoras

# 3. Documentar en versions/VERSION_HISTORY.md

# 4. Ejecutar y comparar
python3 btc_deepseek_auto_v3.py
python3 generate_dashboard.py btc_*_v3.json
```

## 📝 Checklist para Nueva Versión

- [ ] Copiar archivos base
- [ ] Actualizar número de versión
- [ ] Implementar mejoras
- [ ] Documentar en VERSION_HISTORY.md
- [ ] Actualizar este README
- [ ] Ejecutar backtesting
- [ ] Comparar con versiones anteriores
- [ ] Generar dashboard
- [ ] Commit con mensaje descriptivo

## 🐛 Debugging

### Error: "ModuleNotFoundError"
```bash
# Verifica que estés en el directorio correcto
cd /Users/xodla/Documents/Code/06-Agentes/Agno-agent-financial

# O usa el path completo en el import
```

### Error: "KeyError" en JSON
```bash
# El JSON podría estar corrupto
# Regenera ejecutando el backtesting nuevamente
```

### Simulación muy lenta
```bash
# V2 con 1,440 decisiones tarda 1-2 horas
# Para testing rápido, usa menos días:
# En btc_deepseek_auto_v2.py cambiar: days = 7
```

## 💡 Tips

1. **Ejecuta V1 primero** para tener baseline
2. **Guarda todos los JSONs** para comparar después
3. **Usa el dashboard HTML** para análisis visual
4. **Documenta cambios** siempre
5. **Compara métricas** objetivamente
6. **No modifiques V1** - manténla como referencia

## 🔗 Referencias

- [MEJORAS_ALGORITMO.md](../MEJORAS_ALGORITMO.md) - Optimizaciones detalladas
- [VERSION_HISTORY.md](VERSION_HISTORY.md) - Historial completo
- [README.md](../README.md) - Documentación principal

---

**¿Dudas?** Revisa `VERSION_HISTORY.md` para detalles técnicos completos.

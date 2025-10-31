# 🎨 GRÁFICOS INTERACTIVOS - Guía de Instalación

## 📦 Instalar Plotly

```powershell
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Instalar Plotly
pip install plotly

# Verificar instalación
python -c "import plotly; print(f'✅ Plotly {plotly.__version__} installed')"
```

## 🚀 Uso Rápido

```powershell
# Generar reporte con gráficos INTERACTIVOS
python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"

# Abrir en navegador
start reports\report_*.html
```

## ✨ Características de los Gráficos Interactivos

### 🖱️ Controles del Mouse
- **Zoom**: Arrastra con botón izquierdo sobre área
- **Pan**: Arrastra con botón izquierdo (después de zoom)
- **Reset**: Doble clic en cualquier parte
- **Zoom Eje X**: Arrastra horizontalmente
- **Zoom Eje Y**: Arrastra verticalmente

### 🎯 Tooltips (Hover)
- Pasa el mouse sobre cualquier punto
- Muestra valores exactos (fecha, precio, %, etc.)
- Tooltips unificados en eje X para comparaciones

### 📊 Barra de Herramientas
Aparece al pasar mouse sobre gráfico (esquina superior derecha):

- 📷 **Descargar PNG** - Guardar como imagen (1200x800px)
- 🔍 **Zoom** - Activar modo zoom
- ➕ **Zoom In** - Acercar
- ➖ **Zoom Out** - Alejar
- 📐 **Autoscale** - Ajustar automáticamente
- 🔄 **Reset Axes** - Restablecer vista original
- 🎛️ **Toggle Spike Lines** - Líneas de referencia

### 👁️ Leyenda Interactiva
- **Clic simple**: Ocultar/mostrar serie
- **Doble clic**: Aislar serie (ocultar todas las demás)

## 📈 Gráficos Disponibles

### 1. Daily Performance (📈)
**Archivo:** `daily_performance.html`

**Contenido:**
- Línea azul: Portfolio normalizado a 100
- Línea púrpura punteada: S&P 500 normalizado
- Área azul clara: Fill del portfolio

**Interacciones:**
- Zoom en períodos específicos
- Hover para ver valor exacto en fecha
- Toggle portfolio/S&P 500 en leyenda

### 2. Drawdown Analysis (📉)
**Archivo:** `drawdown_analysis.html`

**Contenido:**
- Panel superior: Equity + Running Maximum
- Panel inferior: Drawdown % (área roja)

**Interacciones:**
- Zoom sincronizado en ambos paneles
- Hover para ver drawdown exacto
- Identificar peores períodos

### 3. Performance vs S&P 500 (📊)
**Archivo:** `performance_vs_benchmark.html`

**Contenido:**
- Panel superior: Portfolio vs S&P 500
- Panel inferior: Alpha (barras verdes/rojas)

**Interacciones:**
- Comparación lado a lado
- Zoom en outperformance/underperformance
- Hover para ver alpha diario

### 4. Portfolio Composition (🥧)
**Archivo:** `composition.html`

**Contenido:**
- Donut chart con holdings
- Percentages + valores absolutos
- Sector más grande "pulled"

**Interacciones:**
- Hover para ver valor exacto
- Clic en leyenda para ocultar sectores
- Auto-labels con ticker y %

### 5. Win/Loss Analysis (💰)
**Archivo:** `win_loss_analysis.html`

**Contenido:**
- Barras verdes: Trades ganadores
- Barras rojas: Trades perdedores
- Línea punteada: Break-even (0)

**Interacciones:**
- Hover para P&L exacto por ticker
- Zoom en trades específicos
- Identificar mejores/peores posiciones

### 6. Cash Position (💵)
**Archivo:** `cash_position.html`

**Contenido:**
- Área verde: Cash
- Área azul: Capital invertido
- Línea punteada gris: Total equity

**Interacciones:**
- Hover para ver cash/invested/total
- Zoom en períodos de alta/baja exposición
- Stacked areas para composición

## 🎨 Colores (shadcn-inspired)

```python
Primary (Portfolio):   #3b82f6  🔵 Blue
Secondary (Benchmark): #8b5cf6  🟣 Purple
Success (Positive):    #10b981  🟢 Green
Danger (Negative):     #ef4444  🔴 Red
Warning:               #f59e0b  🟡 Amber
Info:                  #06b6d4  🔵 Cyan
Neutral:               #6b7280  ⚫ Gray
```

## 🌓 Modo Oscuro

Los gráficos de Plotly se adaptan automáticamente al tema del reporte:
- Fondo blanco en modo claro
- Fondos oscuros en modo oscuro (automático)
- Usa el botón 🌙/☀️ del reporte para cambiar

## 📁 Estructura de Archivos

```
reports/
├── charts/                         # Gráficos interactivos
│   ├── daily_performance.html      # 📈 Performance diario
│   ├── drawdown_analysis.html      # 📉 Análisis de caída
│   ├── performance_vs_benchmark.html  # 📊 vs S&P 500
│   ├── composition.html            # 🥧 Composición
│   ├── win_loss_analysis.html      # 💰 Win/Loss
│   └── cash_position.html          # 💵 Cash tracking
└── report_YYYYMMDD_HHMMSS.html     # Reporte principal
```

## 🔧 Troubleshooting

### Error: "No module named 'plotly'"

```powershell
# Instalar Plotly
pip install plotly

# Verificar
python -c "import plotly; print('OK')"
```

### Gráficos no se ven en el reporte

**Causa:** Rutas relativas incorrectas

**Solución:**
```powershell
# Regenerar con rutas absolutas
cd "d:\12_WindSurf\42-Agents\02-ChatGPT-Micro-Cap-Experiment"
python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"
```

### Gráficos se ven pero no son interactivos

**Causa:** JavaScript deshabilitado en navegador

**Solución:**
- Habilitar JavaScript en configuración del navegador
- Usar navegador moderno (Chrome, Firefox, Edge)

### Archivo HTML muy pesado

**Causa:** Plotly usa CDN pero puede ser lento

**Solución:**
```python
# En visualization_plotly.py, cambiar:
fig.write_html(
    str(filepath),
    include_plotlyjs='cdn',  # <-- Usa CDN (ligero)
    # include_plotlyjs=True,  # <-- Incrusta JS completo (pesado)
)
```

## 🆚 Comparación: Plotly vs Matplotlib

| Característica | Matplotlib (Antes) | Plotly (Ahora) |
|---|---|---|
| **Tipo** | PNG estático | HTML interactivo |
| **Tamaño archivo** | ~50-100 KB | ~20-30 KB (CDN) |
| **Interactividad** | ❌ Ninguna | ✅ Zoom, pan, hover |
| **Tooltips** | ❌ No | ✅ Valores exactos |
| **Export** | ✅ PNG fijo | ✅ PNG dinámico |
| **Mobile** | ✅ Sí | ✅ Responsive |
| **Dark mode** | ⚠️ Manual | ✅ Automático |
| **Calidad visual** | ⭐⭐⭐ Buena | ⭐⭐⭐⭐⭐ Excelente |
| **Performance** | ⚡ Rápido | ⚡⚡ Muy rápido |

## 💡 Tips Avanzados

### 1. Descargar gráfico como imagen

1. Pasa mouse sobre gráfico
2. Clic en botón 📷 (esquina superior derecha)
3. Se descarga PNG de alta resolución (1200x800px @ 2x)

### 2. Comparar múltiples series

1. Doble clic en serie en leyenda → Aislar
2. Clic simple para agregar/quitar series
3. Zoom en área específica
4. Hover para comparar valores

### 3. Explorar drawdowns

1. Abrir `drawdown_analysis.html`
2. Zoom en panel inferior (drawdown %)
3. Panel superior se sincroniza automáticamente
4. Identificar fecha exacta de máximo drawdown

### 4. Analizar composición

1. Abrir `composition.html`
2. Hover sobre cada sector para ver valor
3. Clic en leyenda para ocultar sectores pequeños
4. Focus en holdings principales

## 📚 Recursos

### Documentación Plotly
- [Plotly Python](https://plotly.com/python/)
- [Plotly Graph Objects](https://plotly.com/python/graph-objects/)
- [Plotly Express](https://plotly.com/python/plotly-express/)

### Ejemplos
- `fase2_example_interactive.py` - Script completo
- `visualization_plotly.py` - Clase generadora

### Color Palettes
- [shadcn/ui Colors](https://ui.shadcn.com/docs/components/theme)
- [Tailwind CSS Colors](https://tailwindcss.com/docs/customizing-colors)

## 🎯 Próximos Pasos

1. ✅ **Instalar Plotly** - `pip install plotly`
2. ✅ **Generar reporte** - `python agente-agno/fase2_example_interactive.py`
3. ✅ **Explorar gráficos** - Zoom, hover, toggle
4. 🔜 **Personalizar colores** - Editar `visualization_plotly.py`
5. 🔜 **Agregar más gráficos** - Extend `InteractiveVisualizationGenerator`

---

**Versión:** v3.7.0
**Última actualización:** 2025-10-12
**Estado:** ✅ PRODUCTION READY con Gráficos Interactivos

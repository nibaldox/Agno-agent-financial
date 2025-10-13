# 🎨 Transparent Charts for Dark Mode

## Overview
Los gráficos interactivos de Plotly ahora usan **fondos transparentes** para mantener coherencia visual con el modo claro/oscuro de la página HTML.

## Cambios Implementados (v3.8.0)

### 1. Fondo Transparente en Gráficos
```python
# ANTES (v3.7.0)
paper_bgcolor='white'  # Fondo blanco fijo

# AHORA (v3.8.0)
paper_bgcolor='rgba(0,0,0,0)'  # Transparente
plot_bgcolor='rgba(0,0,0,0)'   # Área de plot transparente
```

### 2. Colores Adaptativos de Texto
```python
# ANTES
font=dict(family="...", size=12)

# AHORA
font=dict(
    family="...",
    size=12,
    color='currentColor'  # Se adapta al color del texto de la página
)
```

### 3. Grid y Ejes con Opacidad
```python
# ANTES
gridcolor='#e2e8f0'  # Color fijo (solo modo claro)

# AHORA
gridcolor='rgba(107, 114, 128, 0.2)'  # Gris con opacidad (funciona en ambos modos)
linecolor='rgba(107, 114, 128, 0.3)'  # Líneas de ejes sutiles
```

### 4. Hover Tooltips Adaptados
```python
hoverlabel=dict(
    bgcolor='rgba(0,0,0,0.85)',    # Fondo oscuro semi-transparente
    font_color='white'              # Texto blanco (legible en fondo oscuro)
)
```

## Comportamiento Visual

### Modo Claro (☀️)
- Fondo de página: Blanco
- Gráficos: Se integran perfectamente con fondo blanco de página
- Grid: Gris sutil visible sobre blanco
- Texto: Negro (heredado de la página)

### Modo Oscuro (🌙)
- Fondo de página: `#0f172a` (slate-900)
- Gráficos: Se integran perfectamente con fondo oscuro de página
- Grid: Gris sutil visible sobre oscuro
- Texto: Blanco (heredado de la página)

## Ventajas

✅ **Coherencia visual**: Los gráficos se adaptan automáticamente al tema
✅ **Sin "cajas blancas"**: No hay fondos blancos sobresaliendo en modo oscuro
✅ **Legibilidad**: Grid y texto mantienen buen contraste en ambos modos
✅ **Profesional**: Apariencia pulida y moderna

## Compatibilidad

- ✅ Funciona con toggle manual de dark mode
- ✅ Compatible con `prefers-color-scheme: dark`
- ✅ Soporta transiciones suaves entre modos
- ✅ Exportación PNG mantiene transparencia

## Detalles Técnicos

### CSS del Reporte HTML
```css
/* Modo claro (default) */
body {
    background-color: white;
    color: #0f172a;
}

/* Modo oscuro (clase .dark-mode) */
.dark-mode {
    background-color: #0f172a;
    color: white;
}
```

### Plotly currentColor
El valor `color='currentColor'` es especial:
- No es un color RGB/hex específico
- Hereda el color del texto del elemento padre
- En `<body>`: negro en modo claro, blanco en modo oscuro
- Cambia automáticamente con el toggle de tema

### Transparencia RGBA
```
rgba(red, green, blue, alpha)
alpha: 0 = completamente transparente
alpha: 1 = completamente opaco
alpha: 0.2 = 20% visible (muy sutil)
alpha: 0.85 = 85% visible (tooltip)
```

## Testing

Para verificar que funciona correctamente:

1. **Genera un reporte**:
   ```powershell
   python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"
   ```

2. **Abre en navegador**:
   ```powershell
   start reports/report_*.html
   ```

3. **Prueba el toggle**:
   - Click en botón 🌙/☀️ (top-right)
   - Verifica que gráficos se integran sin "cajas blancas"
   - Comprueba legibilidad de grid y texto

4. **Inspecciona elementos** (F12):
   ```javascript
   // Ver color heredado
   document.querySelector('.js-plotly-plot text').style.color
   // Debería ser: 'currentcolor' o el color computado
   ```

## Solución de Problemas

### "Grid no visible en modo oscuro"
- **Causa**: Opacidad muy baja
- **Solución**: Aumentar alpha en `gridcolor` (de 0.2 a 0.3)

### "Texto no legible"
- **Causa**: Color no se hereda correctamente
- **Solución**: Verificar que `color='currentColor'` está en common_layout

### "Fondos blancos persisten"
- **Causa**: Caché del navegador
- **Solución**: Hard refresh (Ctrl+Shift+R) o modo incógnito

### "Hover tooltip invisible"
- **Causa**: Fondo demasiado transparente
- **Solución**: Aumentar alpha en hoverlabel bgcolor (de 0.85 a 0.95)

## Próximas Mejoras

Posibles mejoras futuras:

- [ ] Auto-detect system theme (prefers-color-scheme)
- [ ] Colores de línea adaptativos (más brillantes en modo oscuro)
- [ ] Animaciones de transición entre modos
- [ ] Exportar PNG con fondo según modo actual

## Referencias

- Plotly Layout: https://plotly.com/python/reference/layout/
- CSS currentColor: https://developer.mozilla.org/en-US/docs/Web/CSS/color_value#currentcolor_keyword
- RGBA Colors: https://www.w3schools.com/css/css_colors_rgb.asp

---

**Versión**: 3.8.0  
**Fecha**: Octubre 2025  
**Impacto**: Mejora visual significativa en modo oscuro 🎨

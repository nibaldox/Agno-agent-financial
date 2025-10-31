# Quick Start Guide - Agno Agent Financial Trading System

Este archivo te permite comenzar rápidamente con el sistema de trading backtest basado en agentes de Agno.

## Requisitos Previos

- Python 3.8+
- Git
- Cuenta de GitHub (para tokens de API si usas OpenRouter)

## Instalación Rápida

### 1. Clona el repositorio
```bash
git clone https://github.com/nibaldox/Agno-agent-financial.git
cd Agno-agent-financial
```

### 2. Configura el entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instala dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura variables de entorno (opcional)
Si usas OpenRouter o necesitas API keys, crea un archivo `.env`:
```bash
cp .env.example .env  # Si existe
# Edita .env con tus claves API
```

## Pruebas Rápidas

### Backtest Básico (5 minutos)
Ejecuta una prueba rápida del motor V3.0 híbrido:
```bash
python hourly_backtest_v3_hybrid_agno_compliant.py
```
Esto ejecutará un backtest de 1 día con datos de 5 minutos para AAPL.

### Prueba Interactiva
Para una experiencia interactiva:
```bash
python interactive_trading_agent.py
```

### Verificación de Resultados
Los resultados se guardan en archivos JSON en la raíz del proyecto. Usa el visualizador:
```bash
python visualize_backtest.py backtest_hybrid_v3_5m_1d_4int_20251020_134905.json
```

## Archivos Principales

- `hourly_backtest_v3_hybrid_agno_compliant.py` - Motor principal de backtest V3.0
- `agents/` - Configuraciones de agentes Agno
- `scripts/` - Scripts adicionales de trading
- `docs/` - Documentación detallada
- `tests/` - Pruebas del sistema

## Próximos Pasos

1. Revisa `docs/QUICKSTART_AGNO.md` para configuración avanzada
2. Explora `scripts/` para diferentes estrategias
3. Modifica `agents/` para personalizar comportamientos
4. Ejecuta backtests más largos cambiando parámetros en los scripts

## Soporte

Si encuentras problemas:
1. Verifica que todas las dependencias estén instaladas
2. Asegúrate de tener conexión a internet para datos de Yahoo Finance
3. Revisa los logs en la consola para errores específicos

¡Disfruta explorando el sistema de trading con IA!</content>
<filePath>/Users/xodla/Documents/Code/06-Agentes/Agno-agent-financial/QUICK_START.md

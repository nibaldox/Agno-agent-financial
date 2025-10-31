# Guía Rápida - Agno Trading System

## Archivos Creados

### 1. Sistema Principal
- `agno_trading_system.py` - Sistema multi-agente completo de trading
- `test_agno_simple.py` - Tests de integración (sin emojis para Windows)
- `test_agno_integration.py` - Tests completos (con emojis)

### 2. Configuración
- `llm_config.py` - Configuración de LLM providers (DeepSeek + OpenRouter)
- `.env.example` - Template para API keys
- `LLM_PROVIDERS.md` - Documentación de proveedores
- `MODEL_RECOMMENDATIONS.md` - Guía de selección de modelos
- `AGNO_README.md` - Documentación completa del sistema Agno

## Setup Rápido (5 minutos)

### Paso 1: Instalar Dependencias
```bash
pip install agno pandas yfinance python-dotenv
```

### Paso 2: Configurar API Keys

1. Crear archivo `.env`:
```bash
copy .env.example .env  # Windows
```

2. Editar `.env` y agregar keys:
```env
DEEPSEEK_API_KEY=tu_key_aqui
OPENROUTER_API_KEY=tu_key_aqui
```

3. Obtener keys:
- **DeepSeek**: https://platform.deepseek.com/ (pago, muy barato)
- **OpenRouter**: https://openrouter.ai/keys (GRATIS!)

### Paso 3: Probar Sistema

```bash
# Test básico con OpenRouter (gratis)
python test_agno_simple.py --provider openrouter

# Test con DeepSeek
python test_agno_simple.py --provider deepseek

# Test multi-agente
python test_agno_simple.py --provider openrouter --team
```

### Paso 4: Trading Analysis

```bash
# Dry run (solo análisis, sin trades)
python agno_trading_system.py --provider openrouter --dry-run

# Con DeepSeek (producción)
python agno_trading_system.py --provider deepseek --dry-run
```

## Arquitectura del Sistema

### 4 Agentes Especializados:

1. **Data Analyst**
   - Analiza portfolio actual
   - Calcula ROI y métricas
   - Custom tools: PortfolioAnalyzerTool

2. **Market Researcher**
   - Investiga stocks
   - Tools: YFinance (precio, noticias, analistas)

3. **Risk Manager**
   - Evalúa riesgo
   - Calcula position sizing
   - Custom tools: RiskAnalyzerTool

4. **Trading Strategist** (Líder)
   - Coordina decisiones
   - Output: JSON con recomendaciones

### Workflow:

```
Portfolio Data → Data Analyst → Metrics
                      ↓
Market Data → Researcher → Opportunities
                      ↓
Risk Analysis → Risk Manager → Sizing
                      ↓
All Inputs → Strategist → Trade Recommendations (JSON)
```

## Modelos Recomendados

### Para Testing/Desarrollo (GRATIS):
```bash
--provider openrouter --model google/gemini-2.0-flash-exp:free
```

### Para Razonamiento Profundo (GRATIS):
```bash
--provider openrouter --model google/gemini-2.0-flash-thinking-exp:free
```

### Para Producción (Económico):
```bash
--provider deepseek --model deepseek-chat
```

## Comandos Útiles

### Testing
```bash
# Test OpenRouter (gratis)
python test_agno_simple.py --provider openrouter

# Test DeepSeek
python test_agno_simple.py --provider deepseek

# Test team collaboration
python test_agno_simple.py --provider openrouter --team
```

### Trading Analysis
```bash
# Análisis completo dry-run
python agno_trading_system.py --dry-run

# Con provider específico
python agno_trading_system.py --provider openrouter --dry-run

# Con modelo específico
python agno_trading_system.py \
  --provider openrouter \
  --model google/gemini-2.0-flash-exp:free \
  --dry-run

# Con directorio de datos custom
python agno_trading_system.py \
  --data-dir "Start Your Own" \
  --provider deepseek \
  --dry-run
```

## Troubleshooting

### Problema: Import Errors
```bash
pip install --upgrade agno
```

### Problema: API Key Not Found
```bash
# Verificar .env existe
dir .env  # Windows
ls -la .env  # Linux/Mac

# Verificar contenido
type .env  # Windows
cat .env  # Linux/Mac
```

### Problema: Unicode Errors (Windows)
```bash
# Usar versión simple (sin emojis)
python test_agno_simple.py --provider openrouter
```

## Documentación Completa

Ver archivos:
- `AGNO_README.md` - Guía completa del sistema
- `LLM_PROVIDERS.md` - Configuración de providers
- `MODEL_RECOMMENDATIONS.md` - Selección de modelos

## Próximos Pasos

1. **Ejecutar tests** para verificar setup
2. **Revisar análisis** generados por el sistema
3. **Ajustar agentes** según necesidades
4. **Implementar ejecución** de trades (actualmente solo genera recomendaciones)

## Soporte

- **Agno Docs**: https://docs.agno.com/
- **GitHub Issues**: Reportar bugs en el repositorio
- **Discord**: https://discord.gg/4MtYHHrgA8 (Agno Community)

---

**¡Listo para empezar! Ejecuta el primer test:**
```bash
python test_agno_simple.py --provider openrouter
```

# 🤖 Agente Agno - Sistema Multi-Agente de Trading

Sistema avanzado de trading automatizado usando **Agno Framework** con 5 modelos especializados de IA.

## 📁 Estructura del Proyecto

```
agente-agno/
├── README.md                    # Este archivo
├── scripts/                     # Scripts ejecutables
│   ├── advanced_trading_team.py # Sistema multi-agente principal
│   ├── agno_trading_system.py   # Sistema original de trading
│   └── quick_test.py            # Validación rápida del sistema
├── tests/                       # Tests y validación
│   ├── test_models.py           # Test de modelos individuales
│   ├── test_selected_models.py  # Test de 5 modelos seleccionados
│   ├── test_agno_simple.py      # Test simple de Agno
│   └── test_agno_integration.py # Test de integración completa
├── config/                      # Configuración
│   └── llm_config.py            # Configuración de LLMs
└── docs/                        # Documentación completa
    ├── ADVANCED_TRADING_SYSTEM.md
    ├── AGNO_README.md
    ├── IMPLEMENTATION_STATUS.md
    ├── MODEL_RECOMMENDATIONS.md
    ├── QUICKSTART_AGNO.md
    ├── LLM_PROVIDERS.md
    ├── RESUMEN_EJECUTIVO.md
    ├── SISTEMA_FINAL.md
    └── ROADMAP.md
```

## 🚀 Quick Start

### 1. Validar Sistema (10 segundos)
```bash
cd agente-agno
python scripts/quick_test.py
```

### 2. Probar Modelos Individuales
```bash
# Ver modelos disponibles
python tests/test_selected_models.py --list

# Probar modelo específico
python tests/test_selected_models.py --model deep_research
python tests/test_selected_models.py --model reasoning

# Probar todos
python tests/test_selected_models.py --all
```

### 3. Analizar un Stock
```bash
# Con OpenRouter (5 modelos especializados GRATIS)
python scripts/advanced_trading_team.py --ticker AAPL --provider openrouter

# Con DeepSeek (fallback confiable ~$0.14/M tokens)
python scripts/advanced_trading_team.py --ticker TSLA --provider deepseek
```

### 4. Análisis Diario Completo
```bash
python scripts/advanced_trading_team.py --daily --provider openrouter
```

## 🎯 Modelos Configurados

### OpenRouter (100% GRATIS)
1. **Tongyi DeepResearch 30B** - Market research profundo
2. **DeepSeek R1T2 Chimera** - Razonamiento complejo
3. **Nemotron Nano 9B** - Cálculos rápidos
4. **GLM 4.5 Air** - Análisis general
5. **Qwen3 235B** - Estrategia avanzada (235B parámetros!)

### DeepSeek (Fallback)
- **deepseek-chat** - ~$0.14/M tokens, muy confiable

## 🤖 Arquitectura del Sistema

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────┐
│  TRADING TEAM (4 Agents)            │
├─────────────────────────────────────┤
│  1. Market Researcher               │
│     └─ Tongyi DeepResearch 30B      │
│        └─ YFinanceTools             │
│                                     │
│  2. Risk Analyst                    │
│     └─ Nemotron Nano 9B             │
│        └─ Fast Calculations         │
│                                     │
│  3. Trading Strategist              │
│     └─ DeepSeek R1T2 Chimera        │
│        └─ Step-by-step Reasoning    │
│                                     │
│  4. Portfolio Manager               │
│     └─ Qwen3 235B                   │
│        └─ Final Decision            │
└─────────────────────────────────────┘
    │
    ▼
STRUCTURED JSON OUTPUT
```

## 📚 Documentación

- **[QUICKSTART_AGNO.md](docs/QUICKSTART_AGNO.md)** - Inicio rápido en 5 minutos
- **[ADVANCED_TRADING_SYSTEM.md](docs/ADVANCED_TRADING_SYSTEM.md)** - Arquitectura completa
- **[RESUMEN_EJECUTIVO.md](docs/RESUMEN_EJECUTIVO.md)** - Estado del sistema
- **[ROADMAP.md](docs/ROADMAP.md)** - Próximos pasos y planificación
- **[MODEL_RECOMMENDATIONS.md](docs/MODEL_RECOMMENDATIONS.md)** - Guía de modelos

## ⚙️ Configuración Requerida

### API Keys
Crear archivo `.env` en la raíz del proyecto:
```bash
# Recomendado: OpenRouter (GRATIS con límites)
OPENROUTER_API_KEY=sk-or-v1-...

# Fallback: DeepSeek (~$0.14/M tokens)
DEEPSEEK_API_KEY=sk-...
```

### Obtener API Keys
- **OpenRouter**: https://openrouter.ai/keys
- **DeepSeek**: https://platform.deepseek.com/

## 🧪 Testing

### Validación Completa
```bash
# Verificar dependencias, API keys y funcionalidad básica
python scripts/quick_test.py
```

### Tests Individuales
```bash
# Test simple con DeepSeek
python tests/test_models.py --provider deepseek

# Test de modelos seleccionados
python tests/test_selected_models.py --model deep_research

# Test de integración completa
python tests/test_agno_simple.py --provider openrouter
```

## 📊 Performance

| Modelo | Tiempo | Calidad | Costo |
|--------|--------|---------|-------|
| DeepSeek Chat | 2.6s | ⭐⭐⭐⭐ | $0.14/M |
| Tongyi DeepResearch | 7.8s | ⭐⭐⭐⭐⭐ | GRATIS |
| DeepSeek R1T2 Chimera | 20.7s | ⭐⭐⭐⭐⭐ | GRATIS |

## 🎯 Casos de Uso

### 1. Análisis de Stock Individual
Obtén análisis completo con:
- Precio actual y fundamentales
- Análisis de riesgo y volatilidad
- Recomendación BUY/SELL/HOLD con razonamiento
- Plan de acción específico

### 2. Revisión Diaria del Portfolio
Análisis comprehensivo que incluye:
- Estado actual de holdings
- Nuevas oportunidades
- Métricas de riesgo
- Plan estratégico de 30 días

### 3. Research Profundo
Investigación detallada de mercado usando:
- Deep research con Tongyi 30B
- Análisis de noticias y tendencias
- Evaluación de sector completa

## 🚧 Próximos Pasos

1. **Inmediato** (Hoy)
   - Probar todos los modelos restantes
   - Ejecutar análisis diario completo
   - Documentar outputs típicos

2. **Corto Plazo** (Esta semana)
   - Integrar con trading_script.py
   - Automatización con scheduler
   - Sistema de logging mejorado

3. **Medio Plazo** (2 semanas)
   - Dashboard web
   - Alertas automáticas
   - Backtesting histórico

Ver [ROADMAP.md](docs/ROADMAP.md) para detalles completos.

## 🆘 Soporte

### Problemas Comunes

**Rate Limits de OpenRouter**
```bash
# Solución: Usar DeepSeek
python scripts/advanced_trading_team.py --daily --provider deepseek
```

**Error de API Key**
```bash
# Verificar .env en raíz del proyecto
cat ../.env
```

**Modelo no disponible**
```bash
# Probar modelos uno por uno
python tests/test_selected_models.py --model deep_research
```

## 📞 Recursos

- **Agno Docs**: https://docs.agno.com/
- **OpenRouter**: https://openrouter.ai/models
- **DeepSeek**: https://platform.deepseek.com/
- **YFinance**: https://pypi.org/project/yfinance/

## ✅ Estado del Sistema

- ✅ Instalación completa
- ✅ API Keys configuradas
- ✅ 3/5 modelos probados
- ✅ Sistema multi-agente operacional
- ✅ YFinanceTools integrado
- ⏳ Integración con trading automático

---

**Última actualización**: 2025-10-12  
**Versión**: 1.0  
**Estado**: ✅ OPERACIONAL

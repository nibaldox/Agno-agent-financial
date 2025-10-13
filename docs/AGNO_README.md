# 🤖 Agno Multi-Agent Trading System

## Descripción

Sistema avanzado de trading automatizado utilizando **Agno Framework** con arquitectura multi-agente. Integra DeepSeek y OpenRouter para análisis y toma de decisiones de trading.

## 🏗️ Arquitectura

### Multi-Agente Especializado

El sistema consta de 4 agentes especializados que trabajan en equipo:

```
┌─────────────────────────────────────────────────────────────┐
│                   Trading Team Workflow                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 📊 Data Analyst                                         │
│     - Analiza portfolio actual                              │
│     - Calcula métricas de performance                       │
│     - Identifica tendencias en historial                    │
│                                                              │
│  2. 🔍 Market Researcher                                    │
│     - Investiga oportunidades de mercado                    │
│     - Analiza fundamentales de stocks                       │
│     - Verifica recomendaciones de analistas                 │
│     - Tools: YFinance (precio, noticias, info)              │
│                                                              │
│  3. ⚠️ Risk Manager                                          │
│     - Evalúa riesgo de posiciones                           │
│     - Calcula tamaño óptimo de posiciones                   │
│     - Verifica diversificación                              │
│     - Establece stop-loss levels                            │
│                                                              │
│  4. 🎯 Trading Strategist (Leader)                          │
│     - Sintetiza insights de todos los agentes               │
│     - Toma decisiones finales BUY/SELL/HOLD                 │
│     - Genera recomendaciones con confianza                  │
│     - Output: JSON estructurado con trades                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Custom Tools Integradas

```python
# Portfolio Analysis Tools
- PortfolioAnalyzerTool
  └─ get_current_portfolio()
  └─ get_trade_history()
  └─ calculate_performance_metrics()

# Risk Analysis Tools
- RiskAnalyzerTool
  └─ analyze_position_risk(ticker)
  └─ calculate_portfolio_risk()

# Market Data Tools (Agno Built-in)
- YFinanceTools
  └─ stock_price
  └─ analyst_recommendations
  └─ company_info
  └─ company_news
```

## 🚀 Instalación

### Requisitos Previos

```bash
Python 3.10+
pip
```

### Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O instalar manualmente
pip install agno pandas yfinance python-dotenv
```

### Configurar API Keys

1. **Crear archivo `.env`**:
```bash
cp .env.example .env
```

2. **Agregar tus API keys**:
```env
# DeepSeek (Primary Provider)
DEEPSEEK_API_KEY=tu_key_aqui

# OpenRouter (Free Secondary Provider)
OPENROUTER_API_KEY=tu_key_aqui
```

3. **Obtener API Keys**:

- **DeepSeek**: https://platform.deepseek.com/
  - Crea cuenta
  - Genera API key
  - ~$0.14/M tokens (muy económico)

- **OpenRouter**: https://openrouter.ai/keys
  - Login con Google/GitHub
  - Genera API key
  - **100% GRATIS** para modelos seleccionados

## 📖 Uso

### Test de Integración Básico

```bash
# Test con DeepSeek
python test_agno_integration.py --provider deepseek

# Test con OpenRouter (gratis)
python test_agno_integration.py --provider openrouter

# Test con modelo específico
python test_agno_integration.py --provider openrouter --model google/gemini-2.0-flash-exp:free

# Test multi-agente
python test_agno_integration.py --provider deepseek --multi-agent
```

### Sistema Completo de Trading

```bash
# Análisis con DeepSeek (producción)
python agno_trading_system.py --provider deepseek

# Análisis con OpenRouter (gratis)
python agno_trading_system.py --provider openrouter

# Dry run (solo análisis, sin trades)
python agno_trading_system.py --provider deepseek --dry-run

# Con modelo específico
python agno_trading_system.py \
  --provider openrouter \
  --model google/gemini-2.0-flash-thinking-exp:free \
  --dry-run

# Con directorio de datos custom
python agno_trading_system.py \
  --provider deepseek \
  --data-dir "Start Your Own" \
  --dry-run
```

## 🔧 Configuración Avanzada

### Selección de Modelos

#### DeepSeek (Recomendado para Producción)

```bash
# deepseek-chat: Rápido, económico, excelente para trading
python agno_trading_system.py --provider deepseek --model deepseek-chat

# deepseek-coder: Especializado en código
python agno_trading_system.py --provider deepseek --model deepseek-coder
```

**Características**:
- ⚡ Muy rápido (~1-2s respuesta)
- 💰 Económico (~$0.14/M tokens)
- ✅ Tool calling completo
- 📊 Excelente para decisiones de trading

#### OpenRouter (Gratis)

```bash
# Gemini 2.0 Flash: Mejor modelo gratis general
python agno_trading_system.py --provider openrouter --model google/gemini-2.0-flash-exp:free

# Gemini 2.0 Thinking: Razonamiento profundo
python agno_trading_system.py --provider openrouter --model google/gemini-2.0-flash-thinking-exp:free

# Qwen 3 (235B params): Modelo masivo
python agno_trading_system.py --provider openrouter --model qwen/qwen-3-235b-instruct:free

# Llama 3.1 405B: Largest Llama
python agno_trading_system.py --provider openrouter --model meta-llama/llama-3.1-405b-instruct:free

# Phi-4: Pequeño pero potente
python agno_trading_system.py --provider openrouter --model microsoft/phi-4:free
```

**Modelos Gratuitos Disponibles**:
- `google/gemini-2.0-flash-exp:free` - Mejor general ⭐
- `google/gemini-2.0-flash-thinking-exp:free` - Reasoning ⭐
- `qwen/qwen-3-235b-instruct:free` - 235B params
- `meta-llama/llama-3.1-405b-instruct:free` - 405B params
- `microsoft/phi-4:free` - Rápido, eficiente
- `meta-llama/llama-3.3-70b-instruct:free` - Balance
- `mistralai/ministral-8b:free` - Compacto

Ver lista completa: `LLM_PROVIDERS.md`

### Personalizar Agentes

Editar `agno_trading_system.py`:

```python
def create_data_analyst_agent(provider, model):
    agent = Agent(
        name="Data Analyst",
        model=agent_model,
        role="Portfolio data analyst",
        description="...",
        instructions=[
            "Tus instrucciones personalizadas aquí",
            "Ajusta estrategia de análisis",
            "Define métricas prioritarias"
        ],
        markdown=True,
    )
    return agent
```

## 📊 Output del Sistema

### Formato de Respuesta

El Trading Strategist genera un JSON estructurado:

```json
{
    "date": "2025-01-10",
    "analysis_summary": "El portfolio muestra crecimiento del 5% esta semana...",
    "recommendations": [
        {
            "action": "BUY",
            "ticker": "ABEO",
            "shares": 50,
            "price_target": 8.50,
            "confidence": 85,
            "reason": "Fundamentales sólidos, volumen incrementando...",
            "risk_level": "MEDIUM"
        },
        {
            "action": "SELL",
            "ticker": "XYZ",
            "shares": 100,
            "price_target": null,
            "confidence": 75,
            "reason": "Stop-loss alcanzado, proteger capital",
            "risk_level": "HIGH"
        }
    ],
    "risk_assessment": "Portfolio bien diversificado con 6 posiciones...",
    "next_steps": "Monitorear ABEO para entrada, considerar nuevas oportunidades micro-cap"
}
```

### Ejemplo de Ejecución

```bash
$ python agno_trading_system.py --provider deepseek --dry-run

============================================================
🤖 Agno Multi-Agent Trading System
============================================================
Provider: deepseek
Model: default
Data Dir: Scripts and CSV Files
Mode: DRY RUN (no trades)
============================================================

🚀 Starting team analysis...

📊 Data Analyst Response:
Current portfolio shows 5 positions with total equity $1,250...
ROI: 25% since inception...

🔍 Market Researcher Response:
Found 3 potential micro-cap opportunities:
- TICKER1: Strong fundamentals, P/E 12, analyst buy rating
- TICKER2: Recent news catalyst, volume spike
...

⚠️ Risk Manager Response:
Portfolio risk level: MODERATE
Concentration: No position exceeds 18%
Recommend: Maintain diversification with next trade
...

🎯 Trading Strategist Decision:
{
  "recommendations": [
    {
      "action": "BUY",
      "ticker": "TICKER1",
      "confidence": 88,
      ...
    }
  ]
}

============================================================
✅ Analysis Complete
============================================================
```

## 🛡️ Best Practices

### 1. Siempre Usa Dry Run Primero

```bash
# NUNCA ejecutes trades reales sin revisar primero
python agno_trading_system.py --dry-run
```

### 2. Verifica API Keys

```bash
# Test básico antes de trading completo
python test_agno_integration.py --provider deepseek
```

### 3. Monitorea Costos (DeepSeek)

```bash
# Aunque es barato (~$0.14/M tokens), monitorea uso
# Ver dashboard: https://platform.deepseek.com/
```

### 4. Usa Modelos Apropiados

- **Trading diario**: `deepseek-chat` o `gemini-2.0-flash`
- **Análisis profundo**: `gemini-2.0-flash-thinking` o `qwen-3-235b`
- **Desarrollo/testing**: Cualquier modelo OpenRouter FREE

## 🔍 Troubleshooting

### Error: "Import agno.agent could not be resolved"

```bash
# Reinstalar agno
pip install --upgrade agno
```

### Error: "DEEPSEEK_API_KEY not found"

```bash
# Verificar .env
cat .env  # Linux/Mac
type .env  # Windows

# Asegurar que tiene:
DEEPSEEK_API_KEY=sk-...
```

### Error: "No parameter named 'show_tool_calls'"

```bash
# Versión de agno incorrecta
pip install --upgrade agno
```

### Agentes No Colaboran Correctamente

```bash
# Verificar que Team está configurado correctamente
# Revisar instructions de cada agente
# Asegurar que strategist espera input de otros
```

## 📚 Recursos Adicionales

- **Agno Docs**: https://docs.agno.com/
- **Agno Cookbook**: https://github.com/agno-agi/agno/tree/main/cookbook
- **DeepSeek API**: https://platform.deepseek.com/docs
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Model Recommendations**: Ver `MODEL_RECOMMENDATIONS.md`
- **Provider Config**: Ver `LLM_PROVIDERS.md`

## 🤝 Contribuir

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Ver archivo `LICENSE` para detalles.

## ⚠️ Disclaimer

Este sistema es experimental y para fines educativos. No es asesoría financiera. Trading conlleva riesgos. Solo invierte lo que puedes permitirte perder.

---

**¡Disfruta del trading automatizado con Agno! 🚀**

# Advanced Multi-Agent Trading System

## 🎯 Overview

Sistema de trading multi-agente con **5 modelos especializados de OpenRouter** (todos GRATIS) más DeepSeek como respaldo confiable.

## 🤖 Arquitectura de Agentes

### 1. **Market Researcher** 🔍
- **Modelo**: `alibaba/tongyi-deepresearch-30b-a3b:free`
- **Especialidad**: Investigación profunda de mercado
- **Herramientas**: YFinanceTools (precios, noticias, info empresarial)
- **Función**: Analiza tendencias de mercado, noticias y oportunidades micro-cap

### 2. **Risk Analyst** 📊
- **Modelo**: `nvidia/nemotron-nano-9b-v2:free`
- **Especialidad**: Cálculos rápidos de riesgo
- **Función**: Métricas de portfolio, volatilidad, stop-loss, position sizing

### 3. **Trading Strategist** 🧠
- **Modelo**: `tngtech/deepseek-r1t2-chimera:free`
- **Especialidad**: Razonamiento complejo para decisiones
- **Función**: Recomendaciones BUY/SELL/HOLD con lógica paso a paso

### 4. **Portfolio Manager** 📈
- **Modelo**: `qwen/qwen3-235b-a22b:free`
- **Especialidad**: Estrategia avanzada (235B parámetros!)
- **Función**: Visión general, planificación 3-6 meses, decisiones finales

### 5. **General Analyst** (Respaldo)
- **Modelo**: `z-ai/glm-4.5-air:free`
- **Especialidad**: Análisis general de propósito
- **Función**: Soporte para análisis diversos

### Fallback: **DeepSeek** 🛡️
- **Modelo**: `deepseek-chat`
- **Costo**: ~$0.14/M tokens
- **Función**: Respaldo confiable cuando OpenRouter tiene límites de tasa

## 🔄 Workflow del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      DAILY TRADING CYCLE                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. MARKET RESEARCHER (Tongyi DeepResearch 30B)                 │
│  ├─ Fetch current prices & news (YFinance)                      │
│  ├─ Analyze micro-cap opportunities                             │
│  └─ Identify 2-3 high-potential stocks                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. RISK ANALYST (Nemotron Nano 9B)                             │
│  ├─ Calculate portfolio volatility                              │
│  ├─ Assess concentration risk                                   │
│  ├─ Recommend position sizes & stop-losses                      │
│  └─ Fast numerical analysis                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. TRADING STRATEGIST (DeepSeek R1T2 Chimera)                  │
│  ├─ Synthesize research + risk data                             │
│  ├─ Apply logical reasoning                                     │
│  ├─ Generate BUY/SELL/HOLD recommendations                      │
│  └─ Explain decision-making process                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. PORTFOLIO MANAGER (Qwen3 235B)                              │
│  ├─ Review overall portfolio health                             │
│  ├─ Make final execution decisions                              │
│  ├─ Plan 30-90 day strategy                                     │
│  └─ Output JSON action plan                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STRUCTURED OUTPUT (JSON)                           │
│  {                                                               │
│    "actions": [                                                  │
│      {"type": "BUY", "ticker": "XYZ", "shares": 10, ...},       │
│      {"type": "SELL", "ticker": "ABC", "shares": 5, ...}        │
│    ],                                                            │
│    "reasoning": "...",                                           │
│    "risk_metrics": {...},                                        │
│    "30_day_plan": "..."                                          │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Usage Examples

### Analizar un Stock Específico
```bash
# Con OpenRouter (5 modelos especializados)
python advanced_trading_team.py --ticker AAPL --provider openrouter

# Con DeepSeek (respaldo confiable)
python advanced_trading_team.py --ticker TSLA --provider deepseek
```

### Análisis Diario del Portfolio
```bash
# Recomendado: OpenRouter para máxima variedad
python advanced_trading_team.py --daily --provider openrouter

# Alternativa: DeepSeek para estabilidad
python advanced_trading_team.py --daily --provider deepseek
```

## 📋 Modelos Seleccionados - Justificación

### ¿Por qué estos modelos?

1. **Tongyi DeepResearch 30B** (Market Research)
   - ✅ Especializado en investigación profunda
   - ✅ 30B parámetros = capacidad de análisis complejo
   - ✅ GRATIS en OpenRouter

2. **Nemotron Nano 9B** (Risk Analysis)
   - ✅ NVIDIA optimizado para inferencia rápida
   - ✅ Perfecto para cálculos numéricos
   - ✅ Respuestas sub-segundo

3. **DeepSeek R1T2 Chimera** (Reasoning)
   - ✅ Modelo de razonamiento avanzado
   - ✅ Explica paso a paso su lógica
   - ✅ Ideal para decisiones complejas

4. **Qwen3 235B** (Strategy)
   - ✅ 235B parámetros = el más potente
   - ✅ Comprensión contextual superior
   - ✅ Planificación estratégica a largo plazo

5. **GLM 4.5 Air** (General)
   - ✅ Balance velocidad/calidad
   - ✅ Soporte general

## ⚙️ Configuration

### API Keys Required

Create `.env` file:
```bash
# Primary (recommended for variety)
OPENROUTER_API_KEY=sk-or-v1-...

# Fallback (stable, $0.14/M tokens)
DEEPSEEK_API_KEY=sk-...
```

### Get API Keys
- **OpenRouter**: https://openrouter.ai/keys (GRATIS con límites)
- **DeepSeek**: https://platform.deepseek.com/ (~$0.14/M tokens)

## 🧪 Testing

### Test Individual Models
```bash
# Ver lista de modelos
python test_selected_models.py --list

# Probar deep research
python test_selected_models.py --model deep_research

# Probar razonamiento
python test_selected_models.py --model reasoning

# Probar todos (requiere confirmación)
python test_selected_models.py --all
```

### Test Complete System
```bash
# Análisis simple de un ticker
python advanced_trading_team.py --ticker NVDA --provider openrouter

# Análisis diario completo
python advanced_trading_team.py --daily --provider openrouter
```

## 📊 Expected Output

El sistema genera análisis estructurado con:

1. **Market Research**: Precios actuales, noticias, tendencias del sector
2. **Risk Metrics**: Volatilidad, concentración, stop-loss levels
3. **Trading Decisions**: BUY/SELL/HOLD con razonamiento detallado
4. **Portfolio Impact**: Cómo afecta al portfolio de $100
5. **Action Plan**: Pasos concretos para los próximos 30 días

## 🔒 Safety Features

- ✅ **Dry-run mode** por defecto (no trades reales)
- ✅ **Maximum position size**: 30% del portfolio
- ✅ **Minimum cash reserve**: 20% del portfolio
- ✅ **Stop-loss recommendations**: En cada posición
- ✅ **Multi-agent validation**: Decisiones revisadas por 4 agentes

## 🎯 Next Steps

1. **Test the system**:
   ```bash
   python test_selected_models.py --all
   ```

2. **Run first analysis**:
   ```bash
   python advanced_trading_team.py --daily --provider openrouter
   ```

3. **Analyze specific stocks**:
   ```bash
   python advanced_trading_team.py --ticker YOUR_STOCK --provider openrouter
   ```

4. **Integrate with trading_script.py**:
   - Parse JSON output from team analysis
   - Execute trades via existing trading_script.py
   - Log to CSV files

## 🆘 Troubleshooting

### OpenRouter Rate Limits
```bash
# Use DeepSeek fallback
python advanced_trading_team.py --daily --provider deepseek
```

### Model Availability Issues
```bash
# Test each model individually
python test_selected_models.py --model deep_research
python test_selected_models.py --model reasoning
```

### API Key Errors
```bash
# Check .env file exists
cat .env

# Verify keys are set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'OpenRouter: {os.getenv(\"OPENROUTER_API_KEY\")[:20] if os.getenv(\"OPENROUTER_API_KEY\") else \"NOT SET\"}')"
```

## 📚 Resources

- **Agno Docs**: https://docs.agno.com/
- **OpenRouter Models**: https://openrouter.ai/models
- **DeepSeek API**: https://platform.deepseek.com/
- **YFinance Docs**: https://pypi.org/project/yfinance/

---

**Sistema creado para maximizar variedad de perspectivas usando modelos especializados GRATIS de OpenRouter, con DeepSeek como respaldo confiable.**

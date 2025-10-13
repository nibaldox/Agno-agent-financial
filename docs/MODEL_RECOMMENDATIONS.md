# 🤖 **Recomendaciones de Modelos LLM**

## 📊 **Guía Rápida de Selección**

### **Por Caso de Uso**

#### **🎯 Trading en Producción (Decisiones Críticas)**
```bash
# Opción 1: DeepSeek Chat (Recomendado)
--provider deepseek --model deepseek-chat
# ✅ Rápido, económico, excelente para trading
# ✅ Soporte completo de tools/functions
# 💰 ~$0.14/M tokens

# Opción 2: Gemini 2.0 Flash (Gratis, Excelente)
--provider openrouter --model gemini-2.0-flash
# ✅ GRATIS, última generación de Google
# ✅ 1M context, multimodal, reasoning
# ✅ Soporte tools ✅
```

#### **🧠 Análisis Complejo con Razonamiento**
```bash
# Opción 1: DeepSeek Reasoner (Mejor Razonamiento)
--provider deepseek --model deepseek-reasoner
# ✅ Diseñado específicamente para reasoning
# ⚠️ NO soporta tools - solo reasoning puro
# 💰 ~$0.55/M tokens input, $2.19/M output

# Opción 2: Gemini 2.0 Flash Thinking (Gratis)
--provider openrouter --model gemini-2.0-flash-thinking
# ✅ GRATIS, modo thinking/reasoning
# ✅ Soporta tools ✅
# ✅ Excelente para decisiones complejas
```

#### **⚡ Velocidad Máxima (Respuestas Rápidas)**
```bash
# Opción 1: Phi-4 (Pequeño pero Potente)
--provider openrouter --model phi-4
# ✅ GRATIS, 14B params
# ✅ Rápido, eficiente
# ✅ Soporte tools ✅

# Opción 2: Gemini Flash 1.5 8B
--provider openrouter --model gemini-flash-1.5-8b
# ✅ GRATIS, optimizado para velocidad
# ✅ Multimodal
```

#### **🎨 Máxima Capacidad (Modelos Grandes)**
```bash
# Opción 1: Qwen 3 (235B params - MASIVO!)
--provider openrouter --model qwen-3-235b
# ✅ GRATIS, 235 mil millones de parámetros
# ✅ Uno de los modelos open-source más grandes
# ✅ Excelente para análisis profundos

# Opción 2: Llama 3.1 405B (Más Grande Llama)
--provider openrouter --model llama-3.1-405b
# ✅ GRATIS, 405B params
# ✅ Best-in-class open source
```

#### **💻 Generación de Código**
```bash
# Opción 1: DeepSeek Coder
--provider deepseek --model deepseek-coder
# ✅ Especializado en código
# ✅ Soporte tools ✅
# 💰 Económico

# Opción 2: Qwen 2.5 72B
--provider openrouter --model qwen-2.5-72b
# ✅ GRATIS, excelente para código
# ✅ Multilenguaje (Python, JS, etc.)
```

---

## 🏆 **Ranking por Categoría**

### **Mejor Rendimiento General (FREE)**
1. 🥇 **Gemini 2.0 Flash** - Último de Google, excelente en todo
2. 🥈 **Qwen 3 235B** - Modelo masivo, análisis profundos
3. 🥉 **Llama 3.1 405B** - Mejor Llama, open source

### **Mejor Razonamiento**
1. 🥇 **DeepSeek Reasoner** (sin tools, pago)
2. 🥈 **Gemini 2.0 Flash Thinking** (con tools, gratis)
3. 🥉 **Qwen 3 235B** (gratis)

### **Mejor para Trading Automático**
1. 🥇 **DeepSeek Chat** - Optimizado para decisiones rápidas
2. 🥈 **Gemini 2.0 Flash** - Gratis, excelente, tools ✅
3. 🥉 **Llama 3.3 70B** - Balance perfecto

### **Mejor Relación Costo/Beneficio**
1. 🥇 **Todos los modelos OpenRouter FREE** - $0.00
2. 🥈 **DeepSeek Chat** - $0.14/M tokens
3. 🥉 **DeepSeek Coder** - $0.14/M tokens

---

## 📋 **Tabla Comparativa Completa**

| Modelo | Provider | Versión | Params | Tools | Reasoning | Context | Costo | Velocidad |
|--------|----------|---------|--------|-------|-----------|---------|-------|-----------|
| **Gemini 2.0 Flash** | OpenRouter | 2.0 | - | ✅ | ✅ | 1M | FREE | ⚡⚡⚡ |
| **Gemini 2.0 Thinking** | OpenRouter | 2.0 | - | ✅ | ✅✅ | 1M | FREE | ⚡⚡ |
| **Qwen 3** | OpenRouter | 3.0 | 235B | ✅ | ✅ | 128K | FREE | ⚡ |
| **Llama 3.1 405B** | OpenRouter | 3.1 | 405B | ✅ | ✅ | 128K | FREE | ⚡ |
| **Phi-4** | OpenRouter | 4.0 | 14B | ✅ | ✅ | 128K | FREE | ⚡⚡⚡ |
| **DeepSeek Chat** | DeepSeek | Latest | - | ✅ | ❌ | 128K | $0.14 | ⚡⚡⚡⚡ |
| **DeepSeek Reasoner** | DeepSeek | Latest | - | ❌ | ✅✅✅ | 64K | $0.55 | ⚡⚡ |
| **Llama 3.3 70B** | OpenRouter | 3.3 | 70B | ✅ | ✅ | 128K | FREE | ⚡⚡ |
| **Qwen 2.5 72B** | OpenRouter | 2.5 | 72B | ✅ | ✅ | 128K | FREE | ⚡⚡ |

---

## 🎯 **Estrategias de Uso Recomendadas**

### **💼 Estrategia de Producción (Recomendada)**
```python
# Primary: DeepSeek Chat (rápido, económico, tools)
# Fallback: Gemini 2.0 Flash (gratis, excelente)
# Reasoning: DeepSeek Reasoner cuando sea necesario
```

### **💰 Estrategia 100% Gratis**
```python
# Primary: Gemini 2.0 Flash (mejor gratis general)
# Reasoning: Gemini 2.0 Flash Thinking
# Alternativo: Qwen 3 235B (análisis profundos)
```

### **⚡ Estrategia Máxima Velocidad**
```python
# Primary: DeepSeek Chat (más rápido pago)
# Free: Phi-4 (rápido y capaz)
# Backup: Gemini Flash 1.5 8B
```

### **🧠 Estrategia Máxima Inteligencia**
```python
# Reasoning: DeepSeek Reasoner
# General: Qwen 3 235B o Llama 3.1 405B
# Multimodal: Gemini 2.0 Flash
```

---

## ⚙️ **Configuración por Escenario**

### **Trading Diario Automático**
```bash
# Configuración óptima
python simple_automation.py \
  --provider deepseek \
  --model deepseek-chat \
  --data-dir "Scripts and CSV Files"

# Configuración gratis
python simple_automation.py \
  --provider openrouter \
  --model gemini-2.0-flash \
  --data-dir "Scripts and CSV Files"
```

### **Análisis Profundo Semanal**
```bash
# Con razonamiento profundo
python simple_automation.py \
  --provider deepseek \
  --model deepseek-reasoner \
  --dry-run

# Gratis con thinking
python simple_automation.py \
  --provider openrouter \
  --model gemini-2.0-flash-thinking \
  --dry-run
```

### **Testing y Desarrollo**
```bash
# Rápido y gratis
python simple_automation.py \
  --provider openrouter \
  --model phi-4 \
  --dry-run

# Máxima capacidad gratis
python simple_automation.py \
  --provider openrouter \
  --model qwen-3-235b \
  --dry-run
```

---

## 🔄 **Sistema de Fallback Automático**

El sistema automáticamente cambia de proveedor si uno falla:

```python
# Si DeepSeek falla → OpenRouter (Gemini 2.0)
# Si un modelo no soporta tools → auto-switch a modelo con tools
# Si necesitas reasoning → auto-switch a modelo de reasoning
```

---

## 💡 **Tips Avanzados**

### **Selección Automática de Modelo**
```python
from llm_config import llm_config

# Para trading (necesitas tools)
model = llm_config.get_tool_model("openrouter")  # gemini-2.0-flash

# Para reasoning (no tools)
model = llm_config.get_reasoning_model("openrouter")  # gemini-2.0-flash-thinking
```

### **Verificar Soporte de Tools**
```python
from llm_config import llm_config

# Verificar si modelo soporta tools
supports = llm_config.supports_tools("gemini-2.0-flash")  # True
supports = llm_config.supports_tools("deepseek-reasoner")  # False
```

### **Optimizar Costos**
```python
# Desarrollo: Usa OpenRouter FREE
# Testing: Usa Phi-4 o Gemini 2.0
# Producción: Usa DeepSeek Chat ($0.14/M)
# Reasoning: Usa Gemini 2.0 Thinking (FREE) vs DeepSeek Reasoner ($0.55/M)
```

---

## 🚀 **Conclusión**

### **Recomendación Final**
Para la mayoría de casos de trading:

1. **Producción**: `DeepSeek Chat` (rápido, económico, confiable)
2. **Desarrollo**: `Gemini 2.0 Flash` (gratis, excelente)
3. **Reasoning**: `DeepSeek Reasoner` o `Gemini 2.0 Thinking`
4. **Backup**: `Qwen 3` o `Llama 3.1 405B`

Todos los modelos listados soportan **tool calling** excepto `deepseek-reasoner` (solo reasoning puro).

---

**Última actualización**: Octubre 2025
**Modelos verificados**: Todos funcionando y disponibles gratis en OpenRouter

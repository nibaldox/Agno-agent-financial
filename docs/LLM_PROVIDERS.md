# 🤖 **Configuración de Proveedores LLM**

Este proyecto ahora soporta **múltiples proveedores de LLM** con fallback automático:

## 🎯 **Proveedores Configurados**

### **1. DeepSeek (Proveedor Principal)**
- **Prioridad**: 🥇 Principal
- **Modelos**: `deepseek-chat`, `deepseek-coder`
- **Ventajas**: Rápido, económico, excelente para trading
- **API Key**: https://platform.deepseek.com/

### **2. OpenRouter (Proveedor Secundario)**
- **Prioridad**: 🥈 Fallback
- **Modelos**: ✅ **MODELOS GRATUITOS**
- **Ventajas**: Sin costo, múltiples modelos open-source
- **API Key**: https://openrouter.ai/keys

---

## 🚀 **Setup Rápido**

### **1. Obtener API Keys**

#### **DeepSeek** (Recomendado)
```bash
1. Ir a: https://platform.deepseek.com/
2. Crear cuenta
3. Generar API Key
4. Copiar la key
```

#### **OpenRouter** (Gratis)
```bash
1. Ir a: https://openrouter.ai/keys
2. Crear cuenta con Google/GitHub
3. Generar API Key (gratis)
4. Copiar la key
```

### **2. Configurar Variables de Entorno**

#### **Windows (PowerShell)**
```powershell
# Crear archivo .env
Copy-Item .env.example .env

# Editar .env y agregar tus keys:
# DEEPSEEK_API_KEY=tu-key-aqui
# OPENROUTER_API_KEY=tu-key-aqui
```

#### **Linux/Mac**
```bash
# Copiar template
cp .env.example .env

# Editar .env
nano .env

# O usar export
export DEEPSEEK_API_KEY="tu-key-aqui"
export OPENROUTER_API_KEY="tu-key-aqui"
```

### **3. Verificar Configuración**
```bash
python llm_config.py
```

Deberías ver:
```
✅ DeepSeek: Connected
  • deepseek-chat
  • deepseek-coder

✅ OpenRouter: Connected
  • llama-3.1-8b (FREE)
  • mistral-7b (FREE)
  • gemma-2-9b (FREE)
```

---

## 🎨 **Modelos Disponibles**

### **DeepSeek Models**
| Modelo | Uso | Tokens | Costo |
|--------|-----|--------|-------|
| `deepseek-chat` | Trading decisions, análisis general | Hasta 4K | ~$0.14/M tokens |
| `deepseek-coder` | Generación de código, scripts | Hasta 16K | ~$0.14/M tokens |

### **OpenRouter Free Models**
| Modelo | Proveedor | Versión | Tamaño | Tools | Gratis |
|--------|-----------|---------|--------|-------|--------|
| `gemini-2.0-flash` | Google | 2.0 | - | ✅ | ✅ Sí |
| `gemini-2.0-flash-thinking` | Google | 2.0 | - | ✅ | ✅ Sí |
| `qwen-3-235b` | Alibaba | 3.0 | 235B params | ✅ | ✅ Sí |
| `phi-4` | Microsoft | 4.0 | 14B params | ✅ | ✅ Sí |
| `llama-3.3-70b` | Meta | 3.3 | 70B params | ✅ | ✅ Sí |
| `llama-3.1-405b` | Meta | 3.1 | 405B params | ✅ | ✅ Sí |
| `qwen-2.5-72b` | Alibaba | 2.5 | 72B params | ✅ | ✅ Sí |
| `phi-3.5-mini` | Microsoft | 3.5 | 3.8B params | ✅ | ✅ Sí |

**Notas:**
- ✅ **Gemini 2.0**: Último modelo de Google, excelente para multimodal + reasoning
- ✅ **Qwen 3**: 235B parámetros, uno de los modelos open-source más grandes
- ✅ **Phi-4**: Nuevo modelo pequeño pero potente de Microsoft
- ✅ **Llama 3.1 405B**: El modelo Llama más grande disponible gratis

---

## 💻 **Uso en Código**

### **Básico**
```python
from llm_config import get_llm_response

# Usar DeepSeek (principal)
response = get_llm_response(
    "Analiza este portfolio...",
    provider="deepseek",
    model="deepseek-chat"
)

# Usar OpenRouter (gratis)
response = get_llm_response(
    "Analiza este portfolio...",
    provider="openrouter",
    model="llama-3.1-8b"
)
```

### **Con Fallback Automático**
```python
from llm_config import llm_config

# Intenta DeepSeek, si falla usa OpenRouter automáticamente
response = llm_config.call_llm(
    prompt="Your trading prompt...",
    provider="deepseek"  # Fallback a openrouter si falla
)
```

### **Verificar Disponibilidad**
```python
from llm_config import llm_config

available = llm_config.get_available_models()
print(available)
# {
#   "deepseek": {"available": True, "models": [...]},
#   "openrouter": {"available": True, "models": [...]}
# }
```

---

## 🔧 **Configuración Avanzada**

### **Personalizar Temperatura**
```python
# Más conservador (trading)
response = get_llm_response(
    prompt="Trading decision...",
    temperature=0.3,  # Menos creativo, más consistente
    provider="deepseek"
)

# Más creativo (research)
response = get_llm_response(
    prompt="Find new opportunities...",
    temperature=0.7,  # Más exploración
    provider="openrouter"
)
```

### **Ajustar Max Tokens**
```python
# Respuestas largas
response = get_llm_response(
    prompt="Deep analysis...",
    max_tokens=3000,  # Más detalle
    provider="deepseek"
)

# Respuestas cortas
response = get_llm_response(
    prompt="Quick answer...",
    max_tokens=500,  # Conciso
    provider="openrouter"
)
```

---

## 🎯 **Estrategia de Uso Recomendada**

### **DeepSeek Para:**
- ✅ Decisiones de trading críticas (deepseek-chat)
- ✅ Análisis complejo con razonamiento (deepseek-reasoner)
- ✅ Generación de código (deepseek-coder)
- ✅ Producción diaria (rápido y económico)

### **OpenRouter (Gratis) Para:**
- ✅ **Gemini 2.0 Flash**: Mejor modelo gratis general, multimodal, reasoning
- ✅ **Gemini 2.0 Thinking**: Razonamiento profundo cuando no necesitas tools
- ✅ **Qwen 3 (235B)**: Modelo masivo para análisis complejos
- ✅ **Phi-4**: Modelo pequeño pero potente, rápido
- ✅ **Llama 3.1 (405B)**: Alternativa open-source de alta calidad
- ✅ Testing y desarrollo
- ✅ Backup cuando DeepSeek falla
- ✅ Experimentación sin costo

---

## ⚠️ **Troubleshooting**

### **Error: "No API keys configured"**
```bash
# Verificar que .env existe
ls .env

# Verificar contenido
cat .env  # Linux/Mac
type .env  # Windows

# Asegurar que las keys están configuradas
```

### **Error: "DeepSeek API error"**
```bash
# El sistema automáticamente cambia a OpenRouter
# Pero verifica tu key:
python llm_config.py
```

### **Modelos gratuitos lentos**
```bash
# Normal para modelos gratuitos
# Usa DeepSeek para velocidad (muy económico)
# OpenRouter es backup/testing
```

---

## 💡 **Tips de Optimización**

### **Costos**
```python
# DeepSeek es ~100x más barato que GPT-4
# OpenRouter free models = $0

# Para minimizar costos:
# 1. Usa OpenRouter para desarrollo
# 2. Usa DeepSeek para producción
# 3. Reserva GPT-4 solo para casos críticos
```

### **Performance**
```python
# DeepSeek: ~1-2s respuesta
# OpenRouter Free: ~3-10s respuesta (depende de carga)

# Para tiempo real: DeepSeek
# Para batch processing: OpenRouter OK
```

---

## 🔗 **Enlaces Útiles**

- **DeepSeek Docs**: https://platform.deepseek.com/docs
- **OpenRouter Docs**: https://openrouter.ai/docs
- **OpenRouter Free Models**: https://openrouter.ai/models?order=newest&supported_parameters=tools&max_price=0
- **Agno Framework**: https://github.com/agno-agi/agno

---

## 🎉 **Ejemplo Completo**

```python
# test_llm_providers.py
from llm_config import llm_config, get_llm_response

# Test 1: DeepSeek (principal)
print("🤖 Testing DeepSeek...")
response1 = get_llm_response(
    "Should I buy ABEO stock at $7.50?",
    provider="deepseek",
    model="deepseek-chat"
)
print(f"DeepSeek: {response1}\n")

# Test 2: OpenRouter Free (backup)
print("🌐 Testing OpenRouter (free)...")
response2 = get_llm_response(
    "Should I buy ABEO stock at $7.50?",
    provider="openrouter",
    model="llama-3.1-8b"
)
print(f"OpenRouter: {response2}\n")

# Test 3: Fallback automático
print("🔄 Testing automatic fallback...")
response3 = llm_config.call_llm(
    "Quick market analysis",
    provider="deepseek"  # Cambia a openrouter si falla
)
print(f"Response: {response3}")
```

---

¡Ahora tienes **2 proveedores potentes** con fallback automático y **modelos gratuitos** para desarrollo! 🚀

# 🔄 Guía de Separación e Independencia del Proyecto

## Resumen

`agente-agno` se ha convertido en un proyecto maduro e independiente que merece su propio repositorio. Esta guía explica cómo separarlo del proyecto original.

## 📊 Estado Actual

### Proyecto Original (ChatGPT-Micro-Cap-Experiment)
```
02-ChatGPT-Micro-Cap-Experiment/
├── trading_script.py           # Script de trading original
├── simple_automation.py        # Automatización básica
├── run_report.py              # Reportes básicos
└── agente-agno/               # ← Sistema completo dentro
```

### Proyecto Independiente (Agno Trading System)
```
agno-trading-system/           # ← Nuevo repo independiente
├── setup.py                   # Instalación con pip
├── pyproject.toml            # Config moderna
├── requirements.txt          # Dependencias específicas
├── agno_trading/             # Paquete principal
│   ├── __init__.py
│   ├── agents/              # Sistema de agentes
│   ├── core/                # Analytics FASE 2
│   └── utils/
├── examples/                 # Scripts de ejemplo
├── tests/                    # Tests unitarios
└── docs/                     # Documentación completa
```

## 🎯 Pasos para Separar el Proyecto

### Opción 1: Crear Nuevo Repositorio (Recomendado)

#### Paso 1: Copiar agente-agno a nueva ubicación

```powershell
# Crear directorio para nuevo proyecto
cd D:\12_WindSurf\42-Agents
mkdir agno-trading-system
cd agno-trading-system

# Copiar contenido de agente-agno
Copy-Item -Path "..\02-ChatGPT-Micro-Cap-Experiment\agente-agno\*" -Destination "." -Recurse
```

#### Paso 2: Renombrar carpetas internas

```powershell
# Renombrar carpeta principal
Rename-Item -Path "agente-agno" -NewName "agno_trading"

# O crear estructura limpia
mkdir agno_trading
Copy-Item -Path "core" -Destination "agno_trading\" -Recurse
Copy-Item -Path "agents" -Destination "agno_trading\" -Recurse
```

#### Paso 3: Inicializar Git

```powershell
git init
git add .
git commit -m "Initial commit: Agno Trading System v2.1.0"
```

#### Paso 4: Crear repositorio en GitHub

```powershell
# En GitHub: Create new repository "agno-trading-system"

git remote add origin https://github.com/tu-usuario/agno-trading-system.git
git branch -M main
git push -u origin main
```

### Opción 2: Usar Git Subtree (Mantener Historia)

```powershell
cd D:\12_WindSurf\42-Agents\02-ChatGPT-Micro-Cap-Experiment

# Extraer agente-agno con su historia
git subtree split -P agente-agno -b agno-trading-branch

# Crear nuevo repo
cd ..
mkdir agno-trading-system
cd agno-trading-system
git init
git pull ..\02-ChatGPT-Micro-Cap-Experiment agno-trading-branch
```

### Opción 3: Mantener como Submodule

```powershell
cd D:\12_WindSurf\42-Agents\02-ChatGPT-Micro-Cap-Experiment

# Remover carpeta agente-agno
git rm -r --cached agente-agno
git commit -m "Prepare for submodule"

# Agregar como submodule
git submodule add https://github.com/tu-usuario/agno-trading-system.git agente-agno
```

## 📁 Reestructuración de Archivos

### Archivos a Renombrar

| Original | Nuevo | Motivo |
|----------|-------|--------|
| `agente-agno/` | `agno_trading/` | Python package naming |
| `fase2_example_interactive.py` | `examples/generate_report.py` | Mejor organización |
| `scripts/advanced_reporting_workflow.py` | `examples/complete_workflow.py` | Consistencia |

### Archivos Nuevos Creados

✅ `setup.py` - Instalación con pip
✅ `pyproject.toml` - Config moderna Python
✅ `LICENSE` - MIT License
✅ `MANIFEST.in` - Inclusión de archivos
✅ `.gitignore` - Ignorar archivos temporales
✅ `.env.example` - Template de variables
✅ `requirements.txt` - Dependencias específicas
✅ `__init__.py` - Paquete Python válido

### Archivos a Mover

```
agente-agno/
├── agents/                    → agno_trading/agents/
├── core/                      → agno_trading/core/
├── config/                    → agno_trading/config/
├── tests/                     → tests/
├── docs/                      → docs/
├── fase2_example_interactive.py → examples/generate_report.py
└── scripts/advanced_reporting_workflow.py → examples/complete_workflow.py
```

## 🔧 Ajustes de Código

### 1. Actualizar Imports

**Antes:**
```python
from core import MetricsCalculator
from agents import load_complete_team
```

**Después:**
```python
from agno_trading.core import MetricsCalculator
from agno_trading.agents import load_complete_team
```

### 2. Actualizar Paths

**Antes:**
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Después:**
```python
# No necesario si se instala con pip
from agno_trading import ...
```

### 3. Ajustar Referencias a Datos

**Antes:**
```python
data_dir = Path("Scripts and CSV Files")
```

**Después:**
```python
data_dir = Path(os.getenv('DATA_DIR', 'data/portfolio'))
```

## 🚀 Instalación del Proyecto Independiente

### Como Paquete Editable (Desarrollo)

```bash
cd agno-trading-system
pip install -e .
```

### Como Paquete Normal

```bash
pip install git+https://github.com/tu-usuario/agno-trading-system.git
```

### Desde PyPI (Futuro)

```bash
pip install agno-trading-system
```

## 📦 Publicación en PyPI

```bash
# Build
python -m build

# Upload to PyPI
twine upload dist/*
```

## 🔄 Mantener Ambos Proyectos

### Proyecto Original (ChatGPT-Micro-Cap-Experiment)

**Propósito**: Experimento original con ChatGPT
**Mantener**:
- trading_script.py
- simple_automation.py
- Scripts and CSV Files/
- Documentación del experimento

### Proyecto Nuevo (Agno Trading System)

**Propósito**: Sistema profesional de trading con IA
**Mantener**:
- Sistema de agentes Agno
- FASE 2 Analytics
- Visualizaciones interactivas
- AI Insights

### Enlace entre Proyectos

**README del proyecto original:**
```markdown
## Sistema Avanzado de Agentes

El sistema avanzado de agentes multimodales se ha movido a su propio proyecto:

👉 [Agno Trading System](https://github.com/tu-usuario/agno-trading-system)

Features:
- 9 Agentes especializados
- Métricas institucionales
- Gráficos interactivos
- AI Insights con DeepSeek
```

## 📚 Documentación a Actualizar

### En Agno Trading System

1. **README.md** - Overview completo
2. **docs/INSTALLATION.md** - Guía de instalación
3. **docs/QUICKSTART.md** - Quick start guide
4. **docs/API.md** - Referencia API
5. **docs/AGENTS.md** - Documentación de agentes
6. **docs/ANALYTICS.md** - FASE 2 analytics
7. **docs/DEPLOYMENT.md** - Deployment guide

### En Proyecto Original

1. Actualizar README con link al nuevo proyecto
2. Marcar `agente-agno/` como deprecated
3. Agregar instrucciones de migración

## ✅ Checklist de Separación

### Pre-Separación
- [ ] Backup completo del proyecto original
- [ ] Verificar que todo funciona actualmente
- [ ] Listar todas las dependencias
- [ ] Identificar archivos compartidos

### Durante Separación
- [ ] Crear estructura de nuevo proyecto
- [ ] Copiar archivos relevantes
- [ ] Renombrar carpetas según convenciones Python
- [ ] Crear setup.py y pyproject.toml
- [ ] Actualizar imports en todo el código
- [ ] Crear .env.example
- [ ] Agregar LICENSE
- [ ] Crear .gitignore apropiado

### Post-Separación
- [ ] Instalar paquete localmente
- [ ] Ejecutar todos los tests
- [ ] Generar reporte de ejemplo
- [ ] Verificar que agentes funcionan
- [ ] Actualizar documentación
- [ ] Crear repositorio GitHub
- [ ] Push inicial
- [ ] Actualizar README del proyecto original

### Publicación (Opcional)
- [ ] Preparar para PyPI
- [ ] Crear releases en GitHub
- [ ] Agregar badges al README
- [ ] Crear documentación online (ReadTheDocs)

## 🎯 Resultado Final

### Proyecto Original
```
ChatGPT-Micro-Cap-Experiment/
├── README.md (actualizado con link)
├── trading_script.py
├── simple_automation.py
└── Scripts and CSV Files/
```

### Proyecto Nuevo
```
agno-trading-system/
├── README.md (completo)
├── setup.py
├── agno_trading/
│   ├── agents/
│   └── core/
├── examples/
├── tests/
└── docs/
```

## 💡 Recomendaciones

1. **Mantén ambos proyectos**: El original como experimento histórico, el nuevo como producto
2. **Usa semantic versioning**: Empieza en v2.1.0 (ya tienes funcionalidad madura)
3. **Crea releases**: Tag cada versión importante en GitHub
4. **Documenta bien**: README profesional atrae contribuciones
5. **Tests automáticos**: Agrega GitHub Actions para CI/CD
6. **Pre-commit hooks**: Mantén calidad de código automáticamente

## 🚧 Próximos Pasos

1. **Semana 1**: Separar proyecto y crear repo
2. **Semana 2**: Completar documentación
3. **Semana 3**: Agregar tests faltantes
4. **Semana 4**: Preparar para PyPI
5. **Mes 2**: Publicar v2.1.0 oficial

## 📞 Soporte

Si tienes problemas durante la separación:
1. Verifica que tienes backup
2. Revisa esta guía paso a paso
3. Crea un issue en GitHub
4. Revierte cambios si es necesario

---

**Versión de esta guía**: 1.0
**Fecha**: Octubre 2025
**Autor**: Asistente AI

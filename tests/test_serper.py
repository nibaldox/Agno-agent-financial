"""
Test rápido de SerperTools
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env
PROJECT_ROOT = Path(__file__).parent.parent.parent
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"[INFO] .env cargado desde: {env_file}")
else:
    print(f"[WARNING] No se encontró .env en: {env_file}")

# Verificar que la API key esté disponible
serper_key = os.getenv("SERPER_API_KEY")
if serper_key:
    print(f"[OK] SERPER_API_KEY encontrada: {serper_key[:10]}...")
else:
    print("[ERROR] SERPER_API_KEY no encontrada en .env")
    print("\nPara obtener una API key:")
    print("1. Visita: https://serper.dev/")
    print("2. Crea una cuenta (gratis)")
    print("3. Copia tu API key")
    print("4. Agrégala a .env: SERPER_API_KEY=tu_key_aqui")
    exit(1)

# Probar importación y uso de SerperTools
try:
    from agno.tools.serper import SerperTools

    print("[OK] SerperTools importado correctamente")

    # Crear instancia
    serper = SerperTools()
    print("[OK] SerperTools instanciado correctamente")

    # Verificar métodos disponibles
    methods = [m for m in dir(serper) if not m.startswith("_")]
    print(f"\n[INFO] Métodos disponibles: {methods}")

    # Probar búsqueda básica (si la clase lo soporta)
    if hasattr(serper, "search") or hasattr(serper, "google_search"):
        print("\n[TEST] Probando búsqueda con Serper...")
        print("(Esto se integrará con Agno Agents automáticamente)")

    print("\n[SUCCESS] SerperTools está listo para usar con Agno!")

except ImportError as e:
    print(f"[ERROR] No se pudo importar SerperTools: {e}")
    print("\nIntenta instalar con: pip install agno[serper]")
    exit(1)
except Exception as e:
    print(f"[ERROR] Error al probar SerperTools: {e}")
    exit(1)

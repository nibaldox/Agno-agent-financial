#!/usr/bin/env python3
"""
Runner automático para Backtesting V2.1 - AGNO-COMPLIANT
Ejecuta hourly_backtest_v2_1_agno_compliant.py con parámetros CLI

Uso:
    python btc_deepseek_auto_v2_1_agno.py <days> <interval_hours>

Ejemplos:
    python btc_deepseek_auto_v2_1_agno.py 7 1    # 7 días, decisión cada 1h
    python btc_deepseek_auto_v2_1_agno.py 30 2   # 30 días, decisión cada 2h
    python btc_deepseek_auto_v2_1_agno.py 60 4   # 60 días, decisión cada 4h
"""

import subprocess
import sys
from datetime import datetime


def main():
    # Parámetros por defecto
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    interval_hours = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    print("=" * 80)
    print("🚀 BACKTESTING AUTOMÁTICO V2.1 - AGNO-COMPLIANT")
    print("=" * 80)
    print(f"📅 Período: {days} días")
    print(f"⏰ Intervalo de decisiones: Cada {interval_hours} hora(s)")
    print(f"🤖 Framework: Agno V2 (instructions + output_schema)")
    print(f"⏱️  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # Ejecutar backtest
    cmd = ["python3", "hourly_backtest_v2_1_agno_compliant.py", str(days), str(interval_hours)]

    print(f"🎯 Ejecutando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)

        print()
        print("=" * 80)
        print("✅ BACKTESTING COMPLETADO EXITOSAMENTE")
        print(f"⏱️  Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return result.returncode

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 80)
        print(f"❌ ERROR EN BACKTESTING: {e}")
        print("=" * 80)
        return e.returncode
    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print("⚠️ BACKTESTING INTERRUMPIDO POR USUARIO")
        print("=" * 80)
        return 130


if __name__ == "__main__":
    sys.exit(main())

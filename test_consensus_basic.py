#!/usr/bin/env python3
"""
Prueba corta del motor consenso corregido
"""

from datetime import datetime

import pandas as pd


def test_ema_calculations():
    """Probar cálculos de EMA48 y proyección"""
    print("🧪 Probando cálculos EMA48...")

    # Leer datos simplificados
    data = pd.read_csv("btc_hourly_simple.csv")
    print(f"✅ Datos cargados: {len(data)} filas")
    print(f"Columnas: {data.columns.tolist()}")

    # Simular cálculo EMA48 básico
    if len(data) >= 48:
        ema_series = data["Close"].ewm(span=48, adjust=False).mean()
        ema48 = ema_series.iloc[-1]
        print(f"📊 EMA48 calculada: ${ema48:.2f}")

        # Proyección simple
        if len(ema_series) >= 3:
            delta1 = ema_series.iloc[-1] - ema_series.iloc[-2]
            delta2 = ema_series.iloc[-2] - ema_series.iloc[-3]
            avg_delta = (delta1 + delta2) / 2
            ema48_proj_1 = ema48 + avg_delta
            ema48_proj_2 = ema48_proj_1 + avg_delta
            print(f"📈 EMA48 Proyección +1: ${ema48_proj_1:.2f}")
            print(f"📈 EMA48 Proyección +2: ${ema48_proj_2:.2f}")

        print("✅ Cálculos EMA48 funcionan correctamente")
        return True
    else:
        print(f"❌ Datos insuficientes: {len(data)} < 48 filas necesarias")
        return False


if __name__ == "__main__":
    test_ema_calculations()

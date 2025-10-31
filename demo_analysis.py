#!/usr/bin/env python3
"""
Demo: Análisis de Stock usando Modelos OpenRouter
Simple análisis sin el framework Team para demostrar funcionalidad
"""

import os
import sys
from datetime import datetime

import yfinance as yf
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from agno.models.deepseek import DeepSeek

# Importar modelos Agno
from agno.models.openrouter import OpenRouter

# Configuración de modelos
MODELS = {
    "deep_research": "alibaba/tongyi-deepresearch-30b-a3b:free",  # Market research
    "reasoning": "tngtech/deepseek-r1t2-chimera:free",  # Complex decisions
    "fast_calc": "nvidia/nemotron-nano-9b-v2:free",  # Quick calculations
    "general": "z-ai/glm-4.5-air:free",  # General analysis
    "advanced": "qwen/qwen3-235b-a22b:free",  # Strategy planning
    "deepseek": "deepseek-chat",  # Fallback
}


def get_stock_data(ticker):
    """Obtener datos básicos del stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")

        current_price = hist["Close"].iloc[-1] if not hist.empty else "N/A"
        volume = hist["Volume"].iloc[-1] if not hist.empty else "N/A"

        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "current_price": f"${current_price:.2f}" if current_price != "N/A" else "N/A",
            "market_cap": info.get("marketCap", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "volume": volume,
            "pe_ratio": info.get("trailingPE", "N/A"),
            "description": (
                info.get("longBusinessSummary", "N/A")[:200] + "..."
                if info.get("longBusinessSummary")
                else "N/A"
            ),
        }
    except Exception as e:
        return {"error": f"Error obteniendo datos: {str(e)}"}


def analyze_with_model(model, prompt, ticker_data):
    """Analizar usando un modelo específico"""
    try:
        from agno.agent import Agent

        # Crear agente con el modelo
        agent = Agent(
            name="Stock Analyzer",
            model=model,
            markdown=True,
        )

        # Crear contexto con datos del stock
        context = f"""
DATOS DEL STOCK:
- Ticker: {ticker_data['ticker']}
- Empresa: {ticker_data['name']}
- Precio Actual: {ticker_data['current_price']}
- Sector: {ticker_data['sector']}
- Industria: {ticker_data['industry']}
- Market Cap: {ticker_data['market_cap']}
- P/E Ratio: {ticker_data['pe_ratio']}
- Descripción: {ticker_data['description']}

ANÁLISIS SOLICITADO:
{prompt}
"""

        # Usar print_response que sabemos que funciona
        agent.print_response(context)
        return "✅ Análisis completado arriba"

    except Exception as e:
        return f"Error en análisis: {str(e)}"


def main():
    print("=" * 70)
    print("DEMO: ANÁLISIS DE STOCK CON MODELOS OPENROUTER")
    print("=" * 70)

    # Ticker a analizar
    ticker = input("Ingresa el ticker a analizar (ej: AAPL): ").upper()
    if not ticker:
        ticker = "AAPL"

    print(f"\n🔍 Obteniendo datos de {ticker}...")

    # Obtener datos del stock
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    print(f"✅ Datos obtenidos para {stock_data['name']}")
    print(f"   Precio: {stock_data['current_price']}")
    print(f"   Sector: {stock_data['sector']}")

    # Análisis 1: Investigación de Mercado (Tongyi DeepResearch)
    print(f"\n🔬 ANÁLISIS 1: INVESTIGACIÓN DE MERCADO")
    print("-" * 50)

    research_model = OpenRouter(id=MODELS["deep_research"])
    research_prompt = f"""
Actúa como un analista de mercado experto. Analiza este stock desde la perspectiva de investigación de mercado.

Proporciona:
1. Análisis del sector y posición competitiva
2. Tendencias de la industria
3. Oportunidades y amenazas
4. Perspectiva de crecimiento

Responde en español, máximo 300 palabras.
"""

    research_result = analyze_with_model(research_model, research_prompt, stock_data)
    print(research_result)

    # Análisis 2: Decisión de Trading (DeepSeek Chimera)
    print(f"\n🧠 ANÁLISIS 2: DECISIÓN DE TRADING")
    print("-" * 50)

    reasoning_model = OpenRouter(id=MODELS["reasoning"])
    reasoning_prompt = f"""
Actúa como un trader experto. Basándote en los datos proporcionados, toma una decisión de trading.

Proporciona:
1. Recomendación: BUY / HOLD / SELL
2. Razonamiento paso a paso
3. Precio objetivo
4. Stop-loss sugerido
5. Horizonte temporal

Responde en español, máximo 250 palabras.
"""

    reasoning_result = analyze_with_model(reasoning_model, reasoning_prompt, stock_data)
    print(reasoning_result)

    # Análisis 3: Gestión de Riesgo (Cálculo Rápido)
    print(f"\n⚡ ANÁLISIS 3: GESTIÓN DE RIESGO")
    print("-" * 50)

    risk_model = OpenRouter(id=MODELS["fast_calc"])
    risk_prompt = f"""
Actúa como un analista de riesgo. Calcula métricas de riesgo para este stock.

Basándote en el precio actual, calcula:
1. Tamaño de posición recomendado para portfolio de $10,000
2. Stop-loss en % y precio
3. Risk/Reward ratio objetivo
4. Máxima pérdida aceptable

Responde en español, formato conciso.
"""

    risk_result = analyze_with_model(risk_model, risk_prompt, stock_data)
    print(risk_result)

    print(f"\n✅ ANÁLISIS COMPLETADO PARA {ticker}")
    print("=" * 70)


if __name__ == "__main__":
    main()

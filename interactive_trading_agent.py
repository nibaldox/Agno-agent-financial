#!/usr/bin/env python3
"""
Sistema Interactivo de Análisis de Trading con IA
Usa múltiples modelos especializados de OpenRouter para análisis completo
"""

import os
import sys
from datetime import datetime

import yfinance as yf
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from agno.agent import Agent
from agno.models.deepseek import DeepSeek

# Importar modelos Agno
from agno.models.openrouter import OpenRouter

# Configuración de modelos
MODELS = {
    "deep_research": "alibaba/tongyi-deepresearch-30b-a3b:free",
    "reasoning": "tngtech/deepseek-r1t2-chimera:free",
    "fast_calc": "nvidia/nemotron-nano-9b-v2:free",
    "general": "z-ai/glm-4.5-air:free",
    "advanced": "qwen/qwen3-235b-a22b:free",
    "deepseek": "deepseek-chat",
}


def clear_screen():
    """Limpiar pantalla"""
    os.system("clear" if os.name != "nt" else "cls")


def print_header():
    """Imprimir encabezado"""
    print("\n" + "=" * 70)
    print("  🤖 SISTEMA INTERACTIVO DE ANÁLISIS DE TRADING CON IA")
    print("=" * 70)


def print_menu():
    """Mostrar menú principal"""
    print("\n📋 MENÚ PRINCIPAL:")
    print("─" * 70)
    print("  1. 🔍 Análisis Completo de Stock (3 modelos)")
    print("  2. 🔬 Investigación de Mercado (Deep Research)")
    print("  3. 🧠 Decisión de Trading (Reasoning)")
    print("  4. ⚡ Gestión de Riesgo (Fast Calc)")
    print("  5. 📊 Análisis Técnico (General)")
    print("  6. 🎯 Estrategia Avanzada (Qwen 235B)")
    print("  7. 💬 Pregunta Personalizada")
    print("  8. 📈 Comparar Múltiples Stocks")
    print("  9. ℹ️  Ver Información de Modelos")
    print("  0. 🚪 Salir")
    print("─" * 70)


def get_stock_data(ticker):
    """Obtener datos del stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")

        if hist.empty:
            return {"error": f"No se encontraron datos para {ticker}"}

        current_price = hist["Close"].iloc[-1]
        volume = hist["Volume"].iloc[-1]
        prev_close = hist["Close"].iloc[0]
        change_pct = ((current_price - prev_close) / prev_close) * 100

        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "current_price": f"${current_price:.2f}",
            "price_raw": current_price,
            "change_pct": f"{change_pct:+.2f}%",
            "market_cap": info.get("marketCap", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "volume": f"{volume:,.0f}",
            "pe_ratio": info.get("trailingPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
            "description": (
                info.get("longBusinessSummary", "N/A")[:300] + "..."
                if info.get("longBusinessSummary")
                else "N/A"
            ),
        }
    except Exception as e:
        return {"error": f"Error obteniendo datos: {str(e)}"}


def format_stock_data(data):
    """Formatear datos del stock para mostrar"""
    return f"""
DATOS DEL STOCK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ticker: {data['ticker']}
• Empresa: {data['name']}
• Precio Actual: {data['current_price']} ({data['change_pct']})
• Sector: {data['sector']}
• Industria: {data['industry']}
• Market Cap: {data['market_cap']}
• P/E Ratio: {data['pe_ratio']}
• Volumen: {data['volume']}
• Rango 52 semanas: ${data['52w_low']} - ${data['52w_high']}
• Dividend Yield: {data['dividend_yield']}

Descripción: {data['description']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def analyze_with_agent(model_id, model_name, prompt, stock_data):
    """Realizar análisis con un agente específico"""
    try:
        print(f"\n⏳ Analizando con {model_name}...")

        model = OpenRouter(id=model_id)
        agent = Agent(
            name=f"{model_name} Analyst",
            model=model,
            markdown=True,
        )

        full_prompt = format_stock_data(stock_data) + f"\n{prompt}"
        agent.print_response(full_prompt)

    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")


def option_1_complete_analysis():
    """Análisis completo con 3 modelos"""
    ticker = input("\n📊 Ingresa el ticker (ej: AAPL): ").upper().strip()
    if not ticker:
        print("❌ Ticker inválido")
        return

    print(f"\n🔍 Obteniendo datos de {ticker}...")
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    print(f"✅ Datos obtenidos para {stock_data['name']}")

    # Análisis 1: Investigación
    print("\n" + "=" * 70)
    print("🔬 PARTE 1: INVESTIGACIÓN DE MERCADO")
    print("=" * 70)
    prompt1 = """
Actúa como analista de mercado. Analiza:
1. Posición competitiva en el sector
2. Tendencias de la industria
3. Fortalezas y debilidades
4. Oportunidades y amenazas (FODA)

Responde en español, máximo 300 palabras.
"""
    analyze_with_agent(MODELS["deep_research"], "Tongyi DeepResearch", prompt1, stock_data)

    input("\n⏸️  Presiona ENTER para continuar...")

    # Análisis 2: Decisión de Trading
    print("\n" + "=" * 70)
    print("🧠 PARTE 2: DECISIÓN DE TRADING")
    print("=" * 70)
    prompt2 = """
Actúa como trader profesional. Proporciona:
1. Recomendación: BUY / HOLD / SELL
2. Razonamiento detallado paso a paso
3. Precio objetivo (target)
4. Stop-loss sugerido
5. Horizonte temporal

Responde en español, máximo 250 palabras.
"""
    analyze_with_agent(MODELS["reasoning"], "DeepSeek Chimera", prompt2, stock_data)

    input("\n⏸️  Presiona ENTER para continuar...")

    # Análisis 3: Gestión de Riesgo
    print("\n" + "=" * 70)
    print("⚡ PARTE 3: GESTIÓN DE RIESGO")
    print("=" * 70)

    portfolio = input("💰 Tamaño de tu portfolio (default: $10,000): ").strip()
    portfolio = portfolio if portfolio else "10,000"

    prompt3 = f"""
Actúa como analista de riesgo. Para un portfolio de ${portfolio}, calcula:
1. Tamaño de posición recomendado (% y monto)
2. Stop-loss en % y precio exacto
3. Take-profit en % y precio exacto
4. Risk/Reward ratio
5. Máxima pérdida aceptable

Responde en formato conciso y claro, en español.
"""
    analyze_with_agent(MODELS["fast_calc"], "Nemotron Nano", prompt3, stock_data)

    print("\n✅ ANÁLISIS COMPLETO FINALIZADO")


def option_2_market_research():
    """Investigación de mercado profunda"""
    ticker = input("\n📊 Ingresa el ticker: ").upper().strip()
    if not ticker:
        return

    print(f"\n🔍 Obteniendo datos de {ticker}...")
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    prompt = """
Actúa como analista de investigación de mercado senior. Realiza un análisis exhaustivo:

1. ANÁLISIS DEL SECTOR:
   - Dinámica del sector
   - Principales competidores
   - Barreras de entrada
   - Ciclo de vida de la industria

2. POSICIÓN COMPETITIVA:
   - Ventajas competitivas (moat)
   - Cuota de mercado
   - Poder de fijación de precios
   - Diferenciación vs competencia

3. TENDENCIAS Y CATALIZADORES:
   - Tendencias macroeconómicas
   - Innovaciones tecnológicas
   - Cambios regulatorios
   - Eventos próximos importantes

4. ANÁLISIS FODA DETALLADO

Responde en español, formato estructurado.
"""
    analyze_with_agent(MODELS["deep_research"], "Tongyi DeepResearch", prompt, stock_data)


def option_3_trading_decision():
    """Decisión de trading con razonamiento"""
    ticker = input("\n📊 Ingresa el ticker: ").upper().strip()
    if not ticker:
        return

    print(f"\n🔍 Obteniendo datos de {ticker}...")
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    timeframe = input("⏰ Horizonte temporal (corto/medio/largo, default: medio): ").lower().strip()
    timeframe = timeframe if timeframe in ["corto", "medio", "largo"] else "medio"

    prompt = f"""
Actúa como trader profesional con 20 años de experiencia. Analiza este stock para horizonte {timeframe} plazo.

Proporciona un análisis completo con:

1. RECOMENDACIÓN CLARA: BUY / HOLD / SELL
   - Nivel de confianza (1-10)
   - Tamaño de posición sugerido (conservador/moderado/agresivo)

2. RAZONAMIENTO DETALLADO:
   - Factores técnicos
   - Factores fundamentales
   - Sentimiento del mercado
   - Consideraciones de timing

3. NIVELES CLAVE:
   - Precio objetivo (target)
   - Stop-loss
   - Take-profit parcial
   - Niveles de soporte/resistencia

4. ESCENARIOS:
   - Caso bull (mejor escenario)
   - Caso base (más probable)
   - Caso bear (peor escenario)

5. PLAN DE ACCIÓN:
   - Punto de entrada ideal
   - Gestión de la posición
   - Criterios de salida

Responde en español, formato profesional.
"""
    analyze_with_agent(MODELS["reasoning"], "DeepSeek Chimera", prompt, stock_data)


def option_4_risk_management():
    """Análisis de gestión de riesgo"""
    ticker = input("\n📊 Ingresa el ticker: ").upper().strip()
    if not ticker:
        return

    print(f"\n🔍 Obteniendo datos de {ticker}...")
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    portfolio = input("💰 Tamaño de tu portfolio ($): ").strip()
    risk_tolerance = (
        input("🎯 Tolerancia al riesgo (bajo/medio/alto, default: medio): ").lower().strip()
    )
    risk_tolerance = risk_tolerance if risk_tolerance in ["bajo", "medio", "alto"] else "medio"

    prompt = f"""
Actúa como analista de riesgo certificado. Para un portfolio de ${portfolio} con tolerancia al riesgo {risk_tolerance}:

1. TAMAÑO DE POSICIÓN:
   - Porcentaje recomendado del portfolio
   - Monto en dólares
   - Número de acciones
   - Justificación

2. NIVELES DE PROTECCIÓN:
   - Stop-loss inicial (% y precio)
   - Stop-loss trailing (método)
   - Take-profit parcial (niveles)
   - Take-profit total (precio objetivo)

3. MÉTRICAS DE RIESGO:
   - Risk/Reward ratio
   - Máxima pérdida en $
   - Máxima pérdida en %
   - Tamaño máximo de posición

4. ESTRATEGIA DE ENTRADA:
   - Entrada completa vs escalonada
   - Niveles de compra
   - Dollar-cost averaging

5. PLAN DE CONTINGENCIA:
   - Qué hacer si cae X%
   - Qué hacer si sube X%
   - Eventos que gatillan salida inmediata

Responde en español con números precisos y concretos.
"""
    analyze_with_agent(MODELS["fast_calc"], "Nemotron Nano", prompt, stock_data)


def option_5_technical_analysis():
    """Análisis técnico"""
    ticker = input("\n📊 Ingresa el ticker: ").upper().strip()
    if not ticker:
        return

    print(f"\n🔍 Obteniendo datos de {ticker}...")
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    prompt = """
Actúa como analista técnico experto. Analiza este stock desde perspectiva técnica:

1. ANÁLISIS DE TENDENCIA:
   - Tendencia principal (alcista/bajista/lateral)
   - Fuerza de la tendencia
   - Posibles cambios de tendencia

2. NIVELES CLAVE:
   - Soportes principales
   - Resistencias principales
   - Niveles de Fibonacci relevantes

3. INDICADORES TÉCNICOS:
   - RSI y niveles de sobrecompra/sobreventa
   - MACD y señales
   - Medias móviles (cruces importantes)
   - Volumen y patrones

4. PATRONES:
   - Patrones de velas
   - Patrones de continuación/reversión
   - Gaps significativos

5. TIMING:
   - Mejor momento para entrada
   - Señales de confirmación a esperar

Responde en español, formato técnico pero comprensible.
"""
    analyze_with_agent(MODELS["general"], "GLM 4.5 Air", prompt, stock_data)


def option_6_advanced_strategy():
    """Estrategia avanzada con Qwen 235B"""
    ticker = input("\n📊 Ingresa el ticker: ").upper().strip()
    if not ticker:
        return

    print(f"\n🔍 Obteniendo datos de {ticker}...")
    stock_data = get_stock_data(ticker)

    if "error" in stock_data:
        print(f"❌ {stock_data['error']}")
        return

    prompt = """
Actúa como estratega de inversión senior. Desarrolla una estrategia completa:

1. ANÁLISIS INTEGRAL:
   - Resumen ejecutivo (3-5 puntos clave)
   - Tesis de inversión
   - Ventaja competitiva sostenible

2. ESTRATEGIA RECOMENDADA:
   - Tipo de estrategia (value/growth/momentum/blend)
   - Horizonte temporal óptimo
   - Asignación de capital sugerida

3. PLAN DE IMPLEMENTACIÓN:
   - Fase 1: Investigación y preparación
   - Fase 2: Construcción de posición
   - Fase 3: Monitoreo y ajustes
   - Fase 4: Salida estratégica

4. FACTORES DE ÉXITO:
   - KPIs a monitorear
   - Catalizadores potenciales
   - Red flags que requieren acción

5. INTEGRACIÓN DE PORTFOLIO:
   - Correlación con otras posiciones
   - Impacto en diversificación
   - Contribución esperada al retorno

6. ESCENARIOS Y CONTINGENCIAS:
   - Plan A, B y C
   - Triggers de cada escenario

Responde en español, formato ejecutivo profesional.
"""
    analyze_with_agent(MODELS["advanced"], "Qwen3 235B", prompt, stock_data)


def option_7_custom_question():
    """Pregunta personalizada"""
    ticker = (
        input("\n📊 Ingresa el ticker (o presiona ENTER para pregunta general): ").upper().strip()
    )

    stock_data = None
    if ticker:
        print(f"\n🔍 Obteniendo datos de {ticker}...")
        stock_data = get_stock_data(ticker)
        if "error" in stock_data:
            print(f"❌ {stock_data['error']}")
            return

    print("\n💬 Ingresa tu pregunta personalizada:")
    question = input("❓ ").strip()

    if not question:
        print("❌ Pregunta vacía")
        return

    print("\n🤖 Selecciona el modelo:")
    print("  1. Tongyi DeepResearch (investigación profunda)")
    print("  2. DeepSeek Chimera (razonamiento complejo)")
    print("  3. Nemotron Nano (cálculos rápidos)")
    print("  4. GLM 4.5 Air (análisis general)")
    print("  5. Qwen3 235B (estrategia avanzada)")

    choice = input("👉 ").strip()

    model_map = {
        "1": ("deep_research", "Tongyi DeepResearch"),
        "2": ("reasoning", "DeepSeek Chimera"),
        "3": ("fast_calc", "Nemotron Nano"),
        "4": ("general", "GLM 4.5 Air"),
        "5": ("advanced", "Qwen3 235B"),
    }

    if choice not in model_map:
        print("❌ Opción inválida")
        return

    model_key, model_name = model_map[choice]

    if stock_data:
        analyze_with_agent(MODELS[model_key], model_name, question, stock_data)
    else:
        # Pregunta sin contexto de stock
        try:
            print(f"\n⏳ Analizando con {model_name}...")
            model = OpenRouter(id=MODELS[model_key])
            agent = Agent(name=f"{model_name} Analyst", model=model, markdown=True)
            agent.print_response(question)
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def option_8_compare_stocks():
    """Comparar múltiples stocks"""
    tickers_input = (
        input("\n📊 Ingresa los tickers separados por comas (ej: AAPL,MSFT,GOOGL): ")
        .upper()
        .strip()
    )
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]

    if len(tickers) < 2:
        print("❌ Necesitas al menos 2 tickers para comparar")
        return

    print(f"\n🔍 Obteniendo datos de {len(tickers)} stocks...")
    stocks_data = []

    for ticker in tickers:
        data = get_stock_data(ticker)
        if "error" not in data:
            stocks_data.append(data)
            print(f"  ✅ {ticker}: {data['name']}")
        else:
            print(f"  ❌ {ticker}: Error")

    if len(stocks_data) < 2:
        print("❌ No se pudieron obtener suficientes datos")
        return

    # Crear resumen comparativo
    comparison = "\n\nCOMPARACIÓN DE STOCKS:\n" + "=" * 70 + "\n"
    for data in stocks_data:
        comparison += f"\n{data['ticker']} - {data['name']}\n"
        comparison += f"  Precio: {data['current_price']} ({data['change_pct']})\n"
        comparison += f"  Sector: {data['sector']}\n"
        comparison += f"  Market Cap: {data['market_cap']}\n"
        comparison += f"  P/E: {data['pe_ratio']}\n"
        comparison += "─" * 70 + "\n"

    prompt = f"""
Actúa como analista comparativo de inversiones. Analiza y compara estos stocks:

{comparison}

Proporciona:

1. RANKING GENERAL (1º, 2º, 3º...):
   - Mejor opción overall
   - Justificación breve para cada posición

2. ANÁLISIS POR CATEGORÍAS:
   - Mejor valuación
   - Mejor crecimiento potencial
   - Menor riesgo
   - Mejor momento de entrada

3. COMPARACIÓN DETALLADA:
   - Ventajas y desventajas de cada uno
   - En qué escenarios cada uno es mejor
   - Correlaciones entre ellos

4. RECOMENDACIÓN DE PORTFOLIO:
   - Si tuvieras $10,000, cómo los distribuirías
   - Justificación de la asignación
   - Estrategia de rebalanceo

5. CONCLUSIÓN:
   - ¿Cuál elegirías para inversión a largo plazo?
   - ¿Cuál para trading activo?
   - ¿Cuál evitarías y por qué?

Responde en español, formato comparativo claro.
"""

    print("\n" + "=" * 70)
    print("🔬 ANÁLISIS COMPARATIVO")
    print("=" * 70)

    # Usar modelo avanzado para comparación
    try:
        model = OpenRouter(id=MODELS["advanced"])
        agent = Agent(name="Comparative Analyst", model=model, markdown=True)
        agent.print_response(prompt)
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")


def option_9_model_info():
    """Mostrar información de modelos"""
    print("\n" + "=" * 70)
    print("📚 INFORMACIÓN DE MODELOS DISPONIBLES")
    print("=" * 70)

    models_info = [
        {
            "name": "Tongyi DeepResearch 30B",
            "id": MODELS["deep_research"],
            "icon": "🔬",
            "specialty": "Investigación profunda de mercado",
            "best_for": "Análisis sectorial, competencia, tendencias",
            "speed": "⚡⚡⚡ Rápido (7-10s)",
            "cost": "💰 GRATIS",
        },
        {
            "name": "DeepSeek R1T2 Chimera",
            "id": MODELS["reasoning"],
            "icon": "🧠",
            "specialty": "Razonamiento complejo y decisiones",
            "best_for": "Decisiones BUY/SELL/HOLD, análisis paso a paso",
            "speed": "⚡⚡ Moderado (15-25s)",
            "cost": "💰 GRATIS",
        },
        {
            "name": "Nemotron Nano 9B",
            "id": MODELS["fast_calc"],
            "icon": "⚡",
            "specialty": "Cálculos rápidos y métricas",
            "best_for": "Gestión de riesgo, position sizing, stop-loss",
            "speed": "⚡⚡⚡ Muy rápido (5-15s)",
            "cost": "💰 GRATIS",
        },
        {
            "name": "GLM 4.5 Air",
            "id": MODELS["general"],
            "icon": "📊",
            "specialty": "Análisis general balanceado",
            "best_for": "Análisis técnico, perspectiva general",
            "speed": "⚡⚡⚡ Rápido (8-12s)",
            "cost": "💰 GRATIS",
        },
        {
            "name": "Qwen3 235B",
            "id": MODELS["advanced"],
            "icon": "🎯",
            "specialty": "Estrategia avanzada (235B parámetros!)",
            "best_for": "Estrategia de portfolio, análisis integral",
            "speed": "⚡ Más lento (20-40s)",
            "cost": "💰 GRATIS",
        },
    ]

    for i, model in enumerate(models_info, 1):
        print(f"\n{model['icon']} {i}. {model['name']}")
        print(f"   ID: {model['id']}")
        print(f"   Especialidad: {model['specialty']}")
        print(f"   Mejor para: {model['best_for']}")
        print(f"   Velocidad: {model['speed']}")
        print(f"   Costo: {model['cost']}")
        print("   " + "─" * 66)

    print("\n💡 TIPS:")
    print("  • Todos los modelos son GRATUITOS con OpenRouter")
    print("  • Tienen rate limits razonables")
    print("  • Usa el modelo adecuado para cada tarea")
    print("  • Combina múltiples modelos para mejor análisis")
    print("\n" + "=" * 70)


def main():
    """Función principal"""

    # Verificar API keys
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ ERROR: OPENROUTER_API_KEY no encontrada en .env")
        print("👉 Configura tu API key en el archivo .env")
        return

    while True:
        print_header()
        print_menu()

        choice = input("\n👉 Selecciona una opción: ").strip()

        if choice == "0":
            print("\n👋 ¡Hasta luego!")
            break
        elif choice == "1":
            option_1_complete_analysis()
        elif choice == "2":
            option_2_market_research()
        elif choice == "3":
            option_3_trading_decision()
        elif choice == "4":
            option_4_risk_management()
        elif choice == "5":
            option_5_technical_analysis()
        elif choice == "6":
            option_6_advanced_strategy()
        elif choice == "7":
            option_7_custom_question()
        elif choice == "8":
            option_8_compare_stocks()
        elif choice == "9":
            option_9_model_info()
        else:
            print("❌ Opción inválida")

        input("\n⏸️  Presiona ENTER para volver al menú...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo del programa...")
        sys.exit(0)

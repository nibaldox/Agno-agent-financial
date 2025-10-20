#!/usr/bin/env python3
"""
Análisis Interactivo de Criptomonedas en Tiempo Real
Sistema especializado para análisis de crypto con IA
"""

import os
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from agno.models.openrouter import OpenRouter
from agno.agent import Agent

# Modelos
MODELS = {
    "deep_research": "alibaba/tongyi-deepresearch-30b-a3b:free",
    "reasoning": "tngtech/deepseek-r1t2-chimera:free",
    "fast_calc": "nvidia/nemotron-nano-9b-v2:free",
}

# Criptos populares
CRYPTO_MAP = {
    "BTC": "BTC-USD", "ETH": "ETH-USD", "BNB": "BNB-USD",
    "XRP": "XRP-USD", "ADA": "ADA-USD", "DOGE": "DOGE-USD",
    "SOL": "SOL-USD", "MATIC": "MATIC-USD", "DOT": "DOT-USD",
    "AVAX": "AVAX-USD", "LINK": "LINK-USD", "UNI": "UNI-USD",
}

def get_crypto_data(symbol: str) -> dict:
    """Obtener datos de criptomoneda"""
    ticker = CRYPTO_MAP.get(symbol.upper(), f"{symbol.upper()}-USD")
    
    try:
        crypto = yf.Ticker(ticker)
        hist = crypto.history(period="1mo")
        
        if hist.empty:
            return {"error": f"No se encontraron datos para {symbol}"}
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[0]
        change_1d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        change_1mo = ((current_price - prev_close) / prev_close) * 100
        
        # Volatilidad
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * 100
        
        # Máximo y mínimo 30 días
        high_30d = hist['High'].max()
        low_30d = hist['Low'].min()
        
        return {
            "symbol": symbol.upper(),
            "ticker": ticker,
            "name": ticker.replace("-USD", ""),
            "current_price": f"${current_price:,.2f}",
            "price_raw": current_price,
            "change_1d": f"{change_1d:+.2f}%",
            "change_1mo": f"{change_1mo:+.2f}%",
            "high_30d": f"${high_30d:,.2f}",
            "low_30d": f"${low_30d:,.2f}",
            "volatility": f"{volatility:.2f}%",
            "volume": f"{hist['Volume'].iloc[-1]:,.0f}",
            "avg_volume": f"{hist['Volume'].mean():,.0f}"
        }
    except Exception as e:
        return {"error": f"Error obteniendo datos: {str(e)}"}

def format_crypto_context(data: dict) -> str:
    """Formatear contexto de cripto"""
    return f"""
DATOS DE CRIPTOMONEDA: {data['name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PRECIO Y RENDIMIENTO:
   • Precio Actual: {data['current_price']}
   • Cambio 24h: {data['change_1d']}
   • Cambio 30 días: {data['change_1mo']}

📈 RANGO Y VOLATILIDAD:
   • Máximo 30d: {data['high_30d']}
   • Mínimo 30d: {data['low_30d']}
   • Volatilidad: {data['volatility']} (desviación estándar diaria)

💹 VOLUMEN:
   • Volumen actual: {data['volume']}
   • Volumen promedio: {data['avg_volume']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def analyze_crypto(symbol: str, analysis_type: str):
    """Analizar criptomoneda"""
    print(f"\n🔍 Obteniendo datos de {symbol}...")
    data = get_crypto_data(symbol)
    
    if "error" in data:
        print(f"❌ {data['error']}")
        return
    
    print(f"✅ Datos obtenidos para {data['name']}")
    print(format_crypto_context(data))
    
    # Seleccionar prompt según tipo de análisis
    prompts = {
        "trading": f"""
Actúa como trader profesional de criptomonedas con experiencia en trading de alta volatilidad.

Analiza {data['name']} y proporciona:

1. RECOMENDACIÓN: BUY / HOLD / SELL
   - Nivel de confianza (1-10)
   - Timeframe recomendado (corto/medio/largo plazo)

2. ANÁLISIS TÉCNICO:
   - Tendencia actual (alcista/bajista/lateral)
   - Niveles de soporte y resistencia
   - Momentum del precio
   - Contexto del volumen

3. GESTIÓN DE RIESGO:
   - Precio de entrada ideal
   - Stop-loss sugerido (% y precio)
   - Take-profit objetivo (% y precio)
   - Tamaño de posición recomendado (% del portfolio)

4. CONSIDERACIONES ESPECIALES:
   - Factores de volatilidad a considerar
   - Eventos próximos relevantes
   - Correlaciones con BTC/mercado cripto general

5. ESCENARIOS:
   - Caso bull: ¿Hasta dónde puede llegar?
   - Caso bear: ¿Cuál es el downside?
   - Probabilidad de cada escenario

Responde en español, formato estructurado. Sé específico con precios y porcentajes.
""",
        "fundamentals": f"""
Actúa como analista de criptomonedas especializado en análisis fundamental.

Analiza {data['name']} considerando:

1. FUNDAMENTOS DEL PROYECTO:
   - Utilidad y caso de uso
   - Tecnología y diferenciación
   - Equipo y desarrollo
   - Adopción y comunidad

2. TOKENOMICS:
   - Supply (circulante, total, máximo)
   - Distribución de tokens
   - Inflación/deflación
   - Mecanismos de quema

3. COMPETENCIA:
   - Principales competidores
   - Ventajas competitivas
   - Posición en el mercado

4. CATALIZADORES:
   - Próximos eventos importantes
   - Actualizaciones de protocolo
   - Partnerships estratégicos
   - Tendencias del sector

5. VALORACIÓN:
   - ¿Está sobrevalorado o infravalorado?
   - Comparación con competidores
   - Perspectiva a largo plazo

Responde en español, análisis profundo.
""",
        "risk": f"""
Actúa como gestor de riesgo especializado en criptomonedas.

Para {data['name']} con una cartera de $10,000:

1. TAMAÑO DE POSICIÓN:
   - % recomendado del portfolio (considerando alta volatilidad)
   - Monto en dólares
   - Número de unidades/tokens
   - Justificación conservadora

2. ESTRATEGIA DE ENTRADA:
   - Entrada completa vs escalonada
   - Niveles de compra sugeridos
   - DCA (Dollar Cost Averaging) vs lump sum

3. PROTECCIÓN DE CAPITAL:
   - Stop-loss inicial (% y precio exacto)
   - Stop-loss trailing
   - Take-profit parcial (25%, 50%, 75%)
   - Take-profit total

4. MÉTRICAS DE RIESGO:
   - Riesgo máximo por operación ($)
   - Risk/Reward ratio objetivo
   - Máxima exposición al sector crypto
   - Diversificación recomendada

5. PLAN DE CONTINGENCIA:
   - ¿Qué hacer si cae 20%?
   - ¿Qué hacer si sube 50%?
   - Señales de salida de emergencia
   - Rebalanceo del portfolio

Responde en español con números concretos y realistas. Prioriza la preservación de capital.
"""
    }
    
    prompt = prompts.get(analysis_type, prompts["trading"])
    
    # Ejecutar análisis
    print(f"\n⏳ Analizando con IA...")
    
    try:
        model = OpenRouter(id=MODELS["reasoning"])
        agent = Agent(name="Crypto Analyst", model=model, markdown=True)
        agent.print_response(prompt)
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")

def compare_cryptos():
    """Comparar múltiples criptomonedas"""
    print("\n📊 COMPARACIÓN DE CRIPTOMONEDAS")
    print("="*70)
    
    cryptos_input = input("Ingresa símbolos separados por coma (ej: BTC,ETH,SOL): ").upper().strip()
    cryptos = [c.strip() for c in cryptos_input.split(",") if c.strip()]
    
    if len(cryptos) < 2:
        print("❌ Necesitas al menos 2 criptos para comparar")
        return
    
    print(f"\n🔍 Obteniendo datos...")
    cryptos_data = []
    
    for symbol in cryptos:
        data = get_crypto_data(symbol)
        if "error" not in data:
            cryptos_data.append(data)
            print(f"  ✅ {symbol}: {data['current_price']}")
        else:
            print(f"  ❌ {symbol}: Error")
    
    if len(cryptos_data) < 2:
        print("❌ No se pudieron obtener suficientes datos")
        return
    
    # Crear contexto comparativo
    comparison = "\n\nCOMPARACIÓN DE CRIPTOMONEDAS:\n" + "="*70 + "\n"
    for data in cryptos_data:
        comparison += f"\n{data['name']}:\n"
        comparison += f"  Precio: {data['current_price']}\n"
        comparison += f"  Cambio 24h: {data['change_1d']}\n"
        comparison += f"  Cambio 30d: {data['change_1mo']}\n"
        comparison += f"  Volatilidad: {data['volatility']}\n"
        comparison += f"  Rango 30d: {data['low_30d']} - {data['high_30d']}\n"
        comparison += "─" * 70 + "\n"
    
    prompt = f"""
Actúa como analista comparativo de criptomonedas. Analiza y compara:

{comparison}

Proporciona:

1. RANKING GENERAL (1º, 2º, 3º...):
   - Mejor opción para inversión ahora
   - Justificación clara para cada posición

2. ANÁLISIS POR CATEGORÍAS:
   - Mejor para corto plazo (trading)
   - Mejor para largo plazo (holding)
   - Menor riesgo / más estable
   - Mayor potencial de crecimiento

3. COMPARACIÓN TÉCNICA:
   - Momentum relativo
   - Volatilidad comparada
   - Tendencias actuales
   - Volumen y liquidez

4. RECOMENDACIÓN DE PORTFOLIO:
   - Si tuvieras $10,000, ¿cómo los distribuirías?
   - % asignado a cada crypto
   - Justificación de la estrategia
   - Timeframe recomendado

5. RIESGOS Y CONSIDERACIONES:
   - Correlaciones entre estas criptos
   - Riesgos específicos de cada una
   - Eventos a vigilar

Responde en español, formato comparativo claro y estructurado.
"""
    
    print("\n" + "="*70)
    print("🔬 ANÁLISIS COMPARATIVO")
    print("="*70)
    
    try:
        model = OpenRouter(id=MODELS["reasoning"])
        agent = Agent(name="Comparative Analyst", model=model, markdown=True)
        agent.print_response(prompt)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Menú principal"""
    print("\n" + "="*70)
    print("💰 ANÁLISIS INTERACTIVO DE CRIPTOMONEDAS CON IA")
    print("="*70)
    
    while True:
        print("\n📋 MENÚ:")
        print("─"*70)
        print("  1. 📊 Análisis de Trading (BUY/SELL/HOLD)")
        print("  2. 🔬 Análisis Fundamental (proyecto, tokenomics)")
        print("  3. ⚡ Gestión de Riesgo (position sizing, stop-loss)")
        print("  4. 📈 Comparar Múltiples Criptos")
        print("  5. 💡 Ver Criptos Disponibles")
        print("  0. 🚪 Salir")
        print("─"*70)
        
        choice = input("\n👉 Selecciona opción: ").strip()
        
        if choice == "0":
            print("\n👋 ¡Hasta luego!")
            break
        
        elif choice in ["1", "2", "3"]:
            print("\n💰 Criptos populares: BTC, ETH, BNB, XRP, ADA, SOL, DOGE, MATIC")
            symbol = input("Ingresa símbolo (ej: BTC): ").strip()
            
            if not symbol:
                print("❌ Símbolo vacío")
                continue
            
            analysis_map = {
                "1": "trading",
                "2": "fundamentals",
                "3": "risk"
            }
            analyze_crypto(symbol, analysis_map[choice])
        
        elif choice == "4":
            compare_cryptos()
        
        elif choice == "5":
            print("\n" + "="*70)
            print("💰 CRIPTOMONEDAS DISPONIBLES")
            print("="*70)
            print("\n🔝 Top 10:")
            for symbol in ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "MATIC", "DOT", "AVAX"]:
                print(f"  {symbol}")
            print("\n💡 También puedes usar cualquier símbolo (se agregará -USD automáticamente)")
        
        else:
            print("❌ Opción inválida")
        
        input("\n⏸️  Presiona ENTER para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

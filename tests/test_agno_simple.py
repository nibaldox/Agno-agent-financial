"""
Test Agno Integration - Simple Version
=======================================

Script simple para probar Agno con DeepSeek y OpenRouter.
Versión sin emojis para compatibilidad con Windows PowerShell.

Uso:
    python test_agno_simple.py --provider deepseek
    python test_agno_simple.py --provider openrouter
"""

import argparse
import os

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agno imports
try:
    from agno.agent import Agent
    from agno.models.deepseek import DeepSeek
    from agno.models.openai import OpenAIChat
    from agno.team.team import Team
    from agno.tools.yfinance import YFinanceTools
except ImportError as e:
    print(f"[ERROR] Failed to import Agno: {e}")
    print("[FIX] Run: pip install agno")
    exit(1)


def test_basic_agent(provider: str = "deepseek", model: str = ""):
    """Test básico de un agente con Agno"""

    print(f"\n{'='*60}")
    print(f"[TEST] Testing Agno Agent")
    print(f"{'='*60}")
    print(f"Provider: {provider}")
    print(f"Model: {model or 'default'}")
    print(f"{'='*60}\n")

    # Crear agente según proveedor
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("[ERROR] DEEPSEEK_API_KEY not found in environment")
            print("[INFO] Get your key at: https://platform.deepseek.com/")
            print("[INFO] Then add to .env file: DEEPSEEK_API_KEY=your-key-here")
            return False

        agent_model = DeepSeek(id=model or "deepseek-chat", api_key=api_key)
        print(f"[OK] Using DeepSeek model: {model or 'deepseek-chat'}")

    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("[ERROR] OPENROUTER_API_KEY not found in environment")
            print("[INFO] Get your FREE key at: https://openrouter.ai/keys")
            print("[INFO] Then add to .env file: OPENROUTER_API_KEY=your-key-here")
            return False

        agent_model = OpenAIChat(
            id=model or "google/gemini-2.0-flash-exp:free",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        print(f"[OK] Using OpenRouter model: {model or 'google/gemini-2.0-flash-exp:free'}")

    else:
        print(f"[ERROR] Unknown provider: {provider}")
        return False

    # Crear agente
    print("\n[INFO] Creating Agno Agent...")
    try:
        agent = Agent(
            name="Test Agent",
            model=agent_model,
            role="Financial analyst assistant",
            description="You are a helpful financial analyst.",
            instructions=[
                "Be concise and clear",
                "Use bullet points for lists",
                "Focus on key insights",
            ],
            markdown=True,
        )
        print("[OK] Agent created successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to create agent: {e}")
        return False

    # Test 1: Simple query
    print(f"\n{'='*60}")
    print("Test 1: Simple Conversation")
    print(f"{'='*60}\n")

    try:
        response = agent.run(
            "What are the top 3 factors to consider when investing in micro-cap stocks?"
        )
        print("[RESPONSE]")
        print(response.content)
    except Exception as e:
        print(f"[ERROR] Test 1 failed: {e}")
        return False

    # Test 2: Con tools (YFinance)
    print(f"\n{'='*60}")
    print("Test 2: Agent with YFinance Tools")
    print(f"{'='*60}\n")

    try:
        finance_agent = Agent(
            name="Finance Agent",
            model=agent_model,
            role="Stock market analyst",
            tools=[YFinanceTools(include_tools=["get_current_stock_price", "get_company_info"])],
            description="You are a stock market analyst with access to real-time market data.",
            instructions=[
                "Always use tools to get current data",
                "Present data in tables when possible",
                "Include ticker symbols in your responses",
            ],
            markdown=True,
        )
        print("[OK] Finance agent with tools created!")
    except Exception as e:
        print(f"[ERROR] Failed to create finance agent: {e}")
        return False

    print("\n[INFO] Querying stock price for AAPL...")
    try:
        response = finance_agent.run("What is the current stock price of Apple (AAPL)?")
        print("[RESPONSE]")
        print(response.content)
    except Exception as e:
        print(f"[ERROR] Test 2 failed: {e}")
        return False

    print(f"\n{'='*60}")
    print("[SUCCESS] All tests passed!")
    print(f"{'='*60}\n")

    return True


def test_team(provider: str = "deepseek"):
    """Test colaboración de equipo"""

    print(f"\n{'='*60}")
    print(f"[TEST] Testing Multi-Agent Team")
    print(f"{'='*60}\n")

    # Setup model
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("[ERROR] DEEPSEEK_API_KEY not found")
            return False
        model = DeepSeek(id="deepseek-chat", api_key=api_key)
    else:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("[ERROR] OPENROUTER_API_KEY not found")
            return False
        model = OpenAIChat(
            id="google/gemini-2.0-flash-exp:free",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    # Crear agentes
    print("[INFO] Creating specialized agents...")

    try:
        researcher = Agent(
            name="Researcher",
            model=model,
            role="Market researcher",
            tools=[
                YFinanceTools(
                    include_tools=["get_current_stock_price", "get_analyst_recommendations"]
                )
            ],
            description="You research stocks and provide market insights.",
            instructions=["Focus on fundamental analysis", "Use real market data"],
            markdown=True,
        )

        analyst = Agent(
            name="Analyst",
            model=model,
            role="Financial analyst",
            description="You analyze financial data and make recommendations.",
            instructions=["Synthesize research into actionable insights", "Be conservative"],
            markdown=True,
        )
        print("[OK] Agents created!")
    except Exception as e:
        print(f"[ERROR] Failed to create agents: {e}")
        return False

    # Crear team
    print("\n[INFO] Creating team...")
    try:
        team = Team(
            name="Investment Team",
            members=[researcher, analyst],
            description="A team that researches and analyzes stocks.",
            instructions=[
                "First, research the stock thoroughly",
                "Then, provide an analysis and recommendation",
                "Be conservative and risk-aware",
            ],
            markdown=True,
        )
        print("[OK] Team created!")
    except Exception as e:
        print(f"[ERROR] Failed to create team: {e}")
        return False

    # Ejecutar análisis
    print(f"\n{'='*60}")
    print("[INFO] Running team analysis on MSFT...")
    print(f"{'='*60}\n")

    query = "Analyze Microsoft (MSFT) stock. Should I buy it?"

    try:
        response = team.run(query)
        print("[TEAM RESPONSE]")
        print(response.content)
    except Exception as e:
        print(f"[ERROR] Team analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    print(f"\n{'='*60}")
    print("[SUCCESS] Team test passed!")
    print(f"{'='*60}\n")

    return True


def main():
    parser = argparse.ArgumentParser(description="Test Agno Integration")
    parser.add_argument(
        "--provider",
        type=str,
        default="deepseek",
        choices=["deepseek", "openrouter"],
        help="LLM provider to test",
    )
    parser.add_argument("--model", type=str, default="", help="Specific model to test (optional)")
    parser.add_argument("--team", action="store_true", help="Test multi-agent team collaboration")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Agno Integration Test Suite")
    print("=" * 60)

    try:
        # Test básico
        success = test_basic_agent(args.provider, args.model)

        if not success:
            print("\n[FAILED] Basic agent test failed")
            return

        # Test team (opcional)
        if args.team:
            success = test_team(args.provider)
            if not success:
                print("\n[FAILED] Team test failed")
                return

        print("\n[DONE] All tests completed successfully!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Tests cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

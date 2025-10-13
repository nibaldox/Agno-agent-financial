"""
🧪 Test Agno Integration
========================

Script simple para probar la integración de Agno con DeepSeek y OpenRouter.

Uso:
    python test_agno_integration.py --provider deepseek
    python test_agno_integration.py --provider openrouter
"""

import os
import argparse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agno imports
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools


def test_basic_agent(provider: str = "deepseek", model: str = ""):
    """Test básico de un agente con Agno"""
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing Agno Agent")
    print(f"{'='*60}")
    print(f"Provider: {provider}")
    print(f"Model: {model or 'default'}")
    print(f"{'='*60}\n")
    
    # Crear agente según proveedor
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ Error: DEEPSEEK_API_KEY not found")
            print("Get your key at: https://platform.deepseek.com/")
            return False
        
        agent_model = DeepSeek(
            id=model or "deepseek-chat",
            api_key=api_key
        )
        print(f"✅ Using DeepSeek model: {model or 'deepseek-chat'}")
        
    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ Error: OPENROUTER_API_KEY not found")
            print("Get your FREE key at: https://openrouter.ai/keys")
            return False
        
        agent_model = OpenAIChat(
            id=model or "google/gemini-2.0-flash-exp:free",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        print(f"✅ Using OpenRouter model: {model or 'google/gemini-2.0-flash-exp:free'}")
    
    else:
        print(f"❌ Unknown provider: {provider}")
        return False
    
    # Crear agente
    print("\n📦 Creating Agno Agent...")
    agent = Agent(
        name="Test Agent",
        model=agent_model,
        role="Financial analyst assistant",
        description="You are a helpful financial analyst.",
        instructions=[
            "Be concise and clear",
            "Use bullet points for lists",
            "Focus on key insights"
        ],
        markdown=True,
    )
    
    print("✅ Agent created successfully!")
    
    # Test 1: Simple query
    print(f"\n{'='*60}")
    print("Test 1: Simple Conversation")
    print(f"{'='*60}\n")
    
    response = agent.run("What are the top 3 factors to consider when investing in micro-cap stocks?")
    print(response.content)
    
    # Test 2: Con tools (YFinance)
    print(f"\n{'='*60}")
    print("Test 2: Agent with YFinance Tools")
    print(f"{'='*60}\n")
    
    finance_agent = Agent(
        name="Finance Agent",
        model=agent_model,
        role="Stock market analyst",
        tools=[YFinanceTools(stock_price=True, company_info=True)],
        description="You are a stock market analyst with access to real-time market data.",
        instructions=[
            "Always use tools to get current data",
            "Present data in tables when possible",
            "Include ticker symbols in your responses"
        ],
        markdown=True,
    )
    
    print("✅ Finance agent with tools created!")
    
    print("\n🔍 Querying stock price for AAPL...")
    response = finance_agent.run("What is the current stock price of Apple (AAPL)?")
    print(response.content)
    
    print(f"\n{'='*60}")
    print("✅ All tests passed successfully!")
    print(f"{'='*60}\n")
    
    return True


def test_multi_agent_collaboration(provider: str = "deepseek"):
    """Test colaboración entre múltiples agentes"""
    
    from agno.team.team import Team
    
    print(f"\n{'='*60}")
    print(f"🤝 Testing Multi-Agent Collaboration")
    print(f"{'='*60}\n")
    
    # Setup model
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ DEEPSEEK_API_KEY not found")
            return False
        model = DeepSeek(id="deepseek-chat", api_key=api_key)
    else:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ OPENROUTER_API_KEY not found")
            return False
        model = OpenAIChat(
            id="google/gemini-2.0-flash-exp:free",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    # Crear agentes especializados
    print("📦 Creating specialized agents...")
    
    researcher = Agent(
        name="Researcher",
        model=model,
        role="Market researcher",
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True)],
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
    
    print("✅ Agents created!")
    
    # Crear team
    print("\n🏗️ Creating team...")
    team = Team(
        name="Investment Team",
        members=[researcher, analyst],
        description="A team that researches and analyzes stocks.",
        instructions=[
            "First, research the stock thoroughly",
            "Then, provide an analysis and recommendation",
            "Be conservative and risk-aware"
        ],
        markdown=True,
    )
    
    print("✅ Team created!")
    
    # Ejecutar análisis
    print(f"\n{'='*60}")
    print("🚀 Running team analysis...")
    print(f"{'='*60}\n")
    
    query = "Analyze Microsoft (MSFT) stock. Should I buy it?"
    
    response = team.run(query)
    print(response.content)
    
    print(f"\n{'='*60}")
    print("✅ Multi-agent collaboration test passed!")
    print(f"{'='*60}\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Test Agno Integration")
    parser.add_argument(
        "--provider",
        type=str,
        default="deepseek",
        choices=["deepseek", "openrouter"],
        help="LLM provider to test"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Specific model to test (optional)"
    )
    parser.add_argument(
        "--multi-agent",
        action="store_true",
        help="Test multi-agent collaboration"
    )
    
    args = parser.parse_args()
    
    try:
        # Test básico
        success = test_basic_agent(args.provider, args.model)
        
        if not success:
            return
        
        # Test multi-agent (opcional)
        if args.multi_agent:
            test_multi_agent_collaboration(args.provider)
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Test Selected OpenRouter Models for Trading System
Tests 5 specific models chosen for different purposes
"""

import os

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Selected models for trading system
SELECTED_MODELS = {
    "deep_research": {
        "id": "alibaba/tongyi-deepresearch-30b-a3b:free",
        "name": "Tongyi DeepResearch 30B",
        "purpose": "Deep market research and analysis",
        "test_query": "Analyze the key factors that affect micro-cap stock performance.",
    },
    "nano_fast": {
        "id": "nvidia/nemotron-nano-9b-v2:free",
        "name": "Nemotron Nano 9B",
        "purpose": "Fast portfolio calculations and quick analysis",
        "test_query": "Calculate the risk-reward ratio for a portfolio with 60% stocks and 40% cash.",
    },
    "glm_general": {
        "id": "z-ai/glm-4.5-air:free",
        "name": "GLM 4.5 Air",
        "purpose": "General purpose analysis and recommendations",
        "test_query": "What are the top 3 risk management strategies for micro-cap trading?",
    },
    "reasoning": {
        "id": "tngtech/deepseek-r1t2-chimera:free",
        "name": "DeepSeek R1T2 Chimera",
        "purpose": "Complex reasoning for trade decisions",
        "test_query": "Should I buy a stock with high volatility but strong fundamentals? Explain your reasoning.",
    },
    "qwen_advanced": {
        "id": "qwen/qwen3-235b-a22b:free",
        "name": "Qwen3 235B",
        "purpose": "Advanced strategy and comprehensive analysis",
        "test_query": "Design a 3-month trading strategy for a $100 micro-cap portfolio.",
    },
}


def test_single_model(model_key: str, verbose: bool = True):
    """Test a single model"""

    model_info = SELECTED_MODELS[model_key]

    print("\n" + "=" * 70)
    print(f"[TEST] {model_info['name']}")
    print("=" * 70)
    print(f"Model ID: {model_info['id']}")
    print(f"Purpose:  {model_info['purpose']}")
    print("-" * 70)

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not found in .env file")
        return False

    try:
        # Create agent
        agent = Agent(
            model=OpenRouter(id=model_info["id"]),
            markdown=True,
        )

        if verbose:
            print(f"\n[QUERY] {model_info['test_query']}")
            print("-" * 70)

        # Get response
        agent.print_response(model_info["test_query"], stream=True)

        print("\n" + "=" * 70)
        print(f"[SUCCESS] {model_info['name']} completed!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        print("=" * 70)
        return False


def test_all_models():
    """Test all selected models sequentially"""

    print("\n" + "=" * 70)
    print("TESTING ALL SELECTED MODELS FOR TRADING SYSTEM")
    print("=" * 70)
    print("\nThis will test 5 models:")
    for key, info in SELECTED_MODELS.items():
        print(f"  - {info['name']}: {info['purpose']}")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    input()

    results = {}

    for model_key in SELECTED_MODELS.keys():
        success = test_single_model(model_key)
        results[model_key] = success

        # Small pause between tests
        if model_key != list(SELECTED_MODELS.keys())[-1]:
            print("\n[INFO] Waiting 2 seconds before next test...")
            import time

            time.sleep(2)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for model_key, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        model_name = SELECTED_MODELS[model_key]["name"]
        print(f"{status} {model_name}")

    success_count = sum(results.values())
    total_count = len(results)
    print(f"\nTotal: {success_count}/{total_count} models working")
    print("=" * 70)


def list_models():
    """List all selected models with details"""

    print("\n" + "=" * 70)
    print("SELECTED MODELS FOR TRADING SYSTEM")
    print("=" * 70)

    for idx, (key, info) in enumerate(SELECTED_MODELS.items(), 1):
        print(f"\n{idx}. {info['name']}")
        print(f"   Model ID: {info['id']}")
        print(f"   Purpose:  {info['purpose']}")
        print(f"   Test:     {info['test_query'][:60]}...")

    print("\n" + "=" * 70)
    print("USAGE:")
    print("  Test single model:")
    print("    python test_selected_models.py --model deep_research")
    print("    python test_selected_models.py --model nano_fast")
    print("    python test_selected_models.py --model glm_general")
    print("    python test_selected_models.py --model reasoning")
    print("    python test_selected_models.py --model qwen_advanced")
    print("\n  Test all models:")
    print("    python test_selected_models.py --all")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test selected OpenRouter models for trading system"
    )

    parser.add_argument(
        "--model", type=str, choices=list(SELECTED_MODELS.keys()), help="Test a specific model"
    )

    parser.add_argument("--all", action="store_true", help="Test all models sequentially")

    parser.add_argument("--list", action="store_true", help="List all selected models")

    args = parser.parse_args()

    # Check if .env exists
    if not os.path.exists(".env") and not args.list:
        print("\n[WARNING] .env file not found!")
        print("Please create .env file with your OPENROUTER_API_KEY")
        print("\nSee .env.example for reference")
        exit(1)

    if args.list:
        list_models()
    elif args.all:
        test_all_models()
    elif args.model:
        test_single_model(args.model)
    else:
        # No arguments - show help
        list_models()
        print("\n[INFO] Use --help to see all options")

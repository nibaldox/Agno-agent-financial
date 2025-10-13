"""
Simple Model Testing Script for Agno Framework
Tests DeepSeek and OpenRouter models with basic queries
"""

import argparse
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.openrouter import OpenRouter

# Load environment variables
load_dotenv()

def test_deepseek():
    """Test DeepSeek model with simple query"""
    print("\n" + "="*60)
    print("[DEEPSEEK TEST]")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("[ERROR] DEEPSEEK_API_KEY not found in .env file")
        print("Get your API key from: https://platform.deepseek.com/")
        return False
    
    print(f"[OK] API Key found: {api_key[:20]}...")
    
    try:
        # Create simple agent
        agent = Agent(
            model=DeepSeek(id="deepseek-chat"),
            markdown=True,
        )
        
        print("\n[TEST] Asking: 'What is 2+2? Respond in one sentence.'")
        print("-" * 60)
        
        # Print response
        agent.print_response("What is 2+2? Respond in one sentence.", stream=True)
        
        print("\n" + "="*60)
        print("[SUCCESS] DeepSeek test completed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] DeepSeek test failed: {str(e)}")
        print("="*60)
        return False


def test_openrouter(model_id: str):
    """Test OpenRouter model with simple query"""
    print("\n" + "="*60)
    print(f"[OPENROUTER TEST] - Model: {model_id}")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not found in .env file")
        print("Get your API key from: https://openrouter.ai/keys")
        return False
    
    print(f"[OK] API Key found: {api_key[:20]}...")
    
    try:
        # Create simple agent
        agent = Agent(
            model=OpenRouter(id=model_id),
            markdown=True,
        )
        
        print("\n[TEST] Asking: 'What is 2+2? Respond in one sentence.'")
        print("-" * 60)
        
        # Print response
        agent.print_response("What is 2+2? Respond in one sentence.", stream=True)
        
        print("\n" + "="*60)
        print(f"[SUCCESS] OpenRouter test completed for {model_id}!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] OpenRouter test failed: {str(e)}")
        print("="*60)
        return False


def list_recommended_models():
    """List recommended OpenRouter models"""
    print("\n" + "="*60)
    print("RECOMMENDED OPENROUTER MODELS")
    print("="*60)
    print("\nFREE MODELS:")
    print("  1. google/gemini-2.0-flash-exp:free")
    print("     - Best general purpose, fast responses")
    print("     - Note: May have rate limits")
    print()
    print("  2. google/gemini-2.0-flash-thinking-exp:free")
    print("     - Advanced reasoning capabilities")
    print("     - Good for complex analysis")
    print()
    print("  3. qwen/qwen-3-235b-instruct:free")
    print("     - 235B parameters, very capable")
    print("     - Good for detailed responses")
    print()
    print("  4. meta-llama/llama-3.1-405b-instruct:free")
    print("     - Largest Llama model (405B)")
    print("     - Excellent for complex tasks")
    print()
    print("  5. microsoft/phi-4:free")
    print("     - Fast and efficient")
    print("     - Good for quick queries")
    print("\nPAID MODELS (Recommended for production):")
    print("  - anthropic/claude-3.5-sonnet")
    print("  - openai/gpt-4-turbo")
    print("  - openai/o1-preview")
    print()
    print("Visit https://openrouter.ai/models for full list")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Test Agno models (DeepSeek and OpenRouter)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test DeepSeek (recommended)
  python test_models.py --provider deepseek
  
  # List available OpenRouter models
  python test_models.py --list-models
  
  # Test OpenRouter with specific model
  python test_models.py --provider openrouter --model google/gemini-2.0-flash-exp:free
  
  # Test OpenRouter with Qwen
  python test_models.py --provider openrouter --model qwen/qwen-3-235b-instruct:free
        """
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=["deepseek", "openrouter"],
        help="LLM provider to test"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="OpenRouter model ID (only used with --provider openrouter)"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List recommended OpenRouter models"
    )
    
    args = parser.parse_args()
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("\n[WARNING] .env file not found!")
        print("Please create .env file with your API keys:")
        print("\n  DEEPSEEK_API_KEY=sk-...")
        print("  OPENROUTER_API_KEY=sk-...")
        print("\nSee .env.example for reference")
        return
    
    # List models if requested
    if args.list_models:
        list_recommended_models()
        return
    
    # Test provider
    if args.provider == "deepseek":
        success = test_deepseek()
        if success:
            print("\n[NEXT STEP] Try OpenRouter models:")
            print("  python test_models.py --list-models")
    
    elif args.provider == "openrouter":
        # Default to Gemini if no model specified
        model_id = args.model or "google/gemini-2.0-flash-exp:free"
        success = test_openrouter(model_id)
        if success:
            print("\n[NEXT STEP] Try other models from:")
            print("  python test_models.py --list-models")
    
    else:
        # No provider specified
        print("\n[INFO] No provider specified. Choose one:")
        print("\n  RECOMMENDED (Stable, $0.14/M tokens):")
        print("    python test_models.py --provider deepseek")
        print("\n  FREE ALTERNATIVE (May have rate limits):")
        print("    python test_models.py --provider openrouter")
        print("\n  See all options:")
        print("    python test_models.py --list-models")
        print("    python test_models.py --help")


if __name__ == "__main__":
    main()

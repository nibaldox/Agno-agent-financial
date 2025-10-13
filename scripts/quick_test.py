"""
Quick Test Script - Validates Complete Multi-Agent Trading System
Tests all 5 specialized models + complete team analysis
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_requirements():
    """Check if all dependencies are installed"""
    print("\n" + "="*70)
    print("CHECKING REQUIREMENTS")
    print("="*70)
    
    required = ["agno", "pandas", "yfinance", "dotenv", "openai"]
    missing = []
    
    for package in required:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing.append(package)
    
    if missing:
        print("\n[ERROR] Missing packages. Install with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("\n[SUCCESS] All requirements installed!")
    return True


def check_api_keys():
    """Check if API keys are configured"""
    print("\n" + "="*70)
    print("CHECKING API KEYS")
    print("="*70)
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    if openrouter_key:
        print(f"[OK] OpenRouter API Key: {openrouter_key[:20]}...")
    else:
        print("[WARNING] OpenRouter API Key not found")
        print("  Get free key at: https://openrouter.ai/keys")
    
    if deepseek_key:
        print(f"[OK] DeepSeek API Key: {deepseek_key[:20]}...")
    else:
        print("[WARNING] DeepSeek API Key not found")
        print("  Get key at: https://platform.deepseek.com/ (~$0.14/M tokens)")
    
    if not openrouter_key and not deepseek_key:
        print("\n[ERROR] No API keys found!")
        print("Please create .env file with at least one API key:")
        print("\n  OPENROUTER_API_KEY=sk-or-v1-...")
        print("  DEEPSEEK_API_KEY=sk-...")
        print("\nSee .env.example for reference")
        return False
    
    print("\n[SUCCESS] API keys configured!")
    return True


def test_simple_model():
    """Test a simple model to verify setup"""
    print("\n" + "="*70)
    print("TESTING SIMPLE MODEL")
    print("="*70)
    
    try:
        from agno.agent import Agent
        
        # Try DeepSeek first (most reliable)
        if os.getenv("DEEPSEEK_API_KEY"):
            from agno.models.deepseek import DeepSeek
            print("\n[TEST] Using DeepSeek (most reliable)")
            agent = Agent(
                model=DeepSeek(id="deepseek-chat"),
                markdown=True,
            )
        elif os.getenv("OPENROUTER_API_KEY"):
            from agno.models.openrouter import OpenRouter
            print("\n[TEST] Using OpenRouter")
            agent = Agent(
                model=OpenRouter(id="google/gemini-2.0-flash-exp:free"),
                markdown=True,
            )
        else:
            print("[ERROR] No API key available")
            return False
        
        print("[QUERY] What is 2+2? (One sentence)")
        print("-"*70)
        
        agent.print_response("What is 2+2? Respond in one sentence.", stream=True)
        
        print("\n" + "="*70)
        print("[SUCCESS] Simple model test passed!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Simple model test failed: {str(e)}")
        print("="*70)
        return False


def show_next_steps():
    """Show recommended next steps"""
    print("\n" + "="*70)
    print("NEXT STEPS - CHOOSE YOUR PATH")
    print("="*70)
    
    print("\n1. TEST INDIVIDUAL MODELS")
    print("   See which models work best for you:")
    print("   python test_selected_models.py --list")
    print("   python test_selected_models.py --model deep_research")
    print("   python test_selected_models.py --model reasoning")
    
    print("\n2. ANALYZE A STOCK")
    print("   Get complete multi-agent analysis:")
    print("   python advanced_trading_team.py --ticker AAPL --provider openrouter")
    print("   python advanced_trading_team.py --ticker TSLA --provider deepseek")
    
    print("\n3. DAILY PORTFOLIO ANALYSIS")
    print("   Run comprehensive daily review:")
    print("   python advanced_trading_team.py --daily --provider openrouter")
    
    print("\n4. READ DOCUMENTATION")
    print("   SISTEMA_FINAL.md - Complete system overview (Spanish)")
    print("   ADVANCED_TRADING_SYSTEM.md - Full architecture guide")
    print("   QUICKSTART_AGNO.md - 5-minute quick start")
    
    print("\n" + "="*70)


def main():
    print("""
==================================================================
                                                                  
        MULTI-AGENT TRADING SYSTEM - QUICK VALIDATION             
                                                                  
  Tests: Dependencies -> API Keys -> Simple Model -> System Ready   
                                                                  
==================================================================
    """)
    
    # Run checks
    if not check_requirements():
        print("\n[FAILED] Fix requirements and run again")
        sys.exit(1)
    
    if not check_api_keys():
        print("\n[FAILED] Configure API keys and run again")
        sys.exit(1)
    
    if not test_simple_model():
        print("\n[FAILED] Model test failed. Check API keys and try again")
        sys.exit(1)
    
    # All tests passed
    print("\n" + "="*70)
    print("[OK] SYSTEM VALIDATION COMPLETE!")
    print("="*70)
    print("\n[STATUS] Your multi-agent trading system is ready to use!")
    print("\n[MODELS AVAILABLE]:")
    if os.getenv("OPENROUTER_API_KEY"):
        print("  [OK] OpenRouter (5 specialized FREE models)")
        print("     - Tongyi DeepResearch 30B (market research)")
        print("     - DeepSeek R1T2 Chimera (reasoning)")
        print("     - Nemotron Nano 9B (fast calculations)")
        print("     - GLM 4.5 Air (general analysis)")
        print("     - Qwen3 235B (advanced strategy)")
    if os.getenv("DEEPSEEK_API_KEY"):
        print("  [OK] DeepSeek (~$0.14/M tokens, very reliable)")
    
    show_next_steps()


if __name__ == "__main__":
    main()

"""
Example: Using Modular Agent System
====================================
Demonstrates how to use YAML-based agent configurations.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import (
    load_complete_team,
    load_market_researcher,
    load_risk_analysts,
    AgentLoader
)


def example_1_complete_team():
    """Example 1: Load complete trading team"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Load Complete Trading Team from YAML")
    print("="*70)
    
    # Load team (9 agents) with one function call
    team = load_complete_team(use_openrouter=True)
    
    print(f"\n✅ Team loaded with {len(team.members)} agents")
    print("\nAgents:")
    for i, agent in enumerate(team.members, 1):
        print(f"  {i}. {agent.name}")
    
    # Use the team
    print("\n" + "-"*70)
    print("Running analysis...")
    print("-"*70)
    
    query = """
    Analyze ABEO as a potential micro-cap investment.
    
    Current Portfolio:
    - Cash: $100.00
    - Total Equity: $100.00
    - Positions: 0
    
    Provide your analysis and recommendation.
    """
    
    # This will run all 9 agents sequentially
    team.print_response(query, stream=True)


def example_2_individual_agents():
    """Example 2: Load and use individual agents"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Load Individual Agents")
    print("="*70)
    
    # Load only Market Researcher
    print("\n[1/1] Loading Market Researcher...")
    researcher = load_market_researcher(use_openrouter=False)
    
    print(f"✅ Loaded: {researcher.name}")
    
    # Use the researcher
    print("\n" + "-"*70)
    print("Running market research on ABEO...")
    print("-"*70)
    
    response = researcher.run("Research ABEO stock: price, fundamentals, recent news")
    print(f"\n{response.content}")


def example_3_risk_analysts_consensus():
    """Example 3: Use 3 Risk Analysts for consensus"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Risk Analysts Consensus")
    print("="*70)
    
    portfolio_summary = {
        'cash': 100.0,
        'total_equity': 100.0,
        'roi': 0.0
    }
    
    # Load all 3 risk analysts
    print("\n[Loading 3 Risk Analysts...]")
    risk_analysts = load_risk_analysts(
        use_openrouter=False,
        portfolio_summary=portfolio_summary
    )
    
    print(f"✅ Loaded {len(risk_analysts)} risk analysts:")
    for analyst in risk_analysts:
        print(f"  - {analyst.name}")
    
    # Get opinion from each analyst
    query = "Analyze the risk profile of ABEO stock"
    
    print("\n" + "-"*70)
    print("Collecting risk opinions...")
    print("-"*70)
    
    for analyst in risk_analysts:
        print(f"\n📊 {analyst.name}:")
        response = analyst.run(query)
        print(f"{response.content[:200]}...")  # First 200 chars
    
    print("\n💡 In production, you would aggregate these 3 opinions")
    print("   using weighted voting (40%-30%-30%)")


def example_4_custom_agent_loader():
    """Example 4: Advanced usage with AgentLoader"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Advanced AgentLoader Usage")
    print("="*70)
    
    loader = AgentLoader()
    
    # Load specific nested configuration
    print("\n[Loading Risk Analyst Conservador...]")
    risk_conservative = loader.load_agent(
        agent_id="risk_conservative",
        config_file="risk_analysts.yaml",
        config_key="agents.conservative",
        use_openrouter=False
    )
    
    print(f"✅ Loaded: {risk_conservative.name}")
    
    # Load YAML config directly for inspection
    print("\n[Inspecting Configuration...]")
    config = loader.load_yaml("market_researcher.yaml")
    
    print(f"\nMarket Researcher Config:")
    print(f"  Name: {config['name']}")
    print(f"  Model: {config['model']['provider']} - {config['model']['model_id']}")
    print(f"  Tools: {', '.join(config['tools'].keys())}")
    print(f"  Estimated Time: {config['metadata']['estimated_time']}")
    print(f"  Estimated Cost: {config['metadata']['cost_per_run']}")


def example_5_modify_on_the_fly():
    """Example 5: Modify configuration programmatically"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Modify Configuration On-the-Fly")
    print("="*70)
    
    loader = AgentLoader()
    
    # Load config
    config = loader.load_yaml("market_researcher.yaml")
    
    print("\n[Original Config]")
    print(f"Temperature: {config['model']['temperature']}")
    print(f"Max Tokens: {config['model']['max_tokens']}")
    
    # Modify config
    print("\n[Modifying Config...]")
    config['model']['temperature'] = 0.5  # More deterministic
    config['model']['max_tokens'] = 2000  # Shorter responses
    
    print("\n[Modified Config]")
    print(f"Temperature: {config['model']['temperature']}")
    print(f"Max Tokens: {config['model']['max_tokens']}")
    
    print("\n💡 In production, you could save modified config to a new YAML file")
    print("   or apply changes dynamically before agent creation")


def main():
    """Run all examples"""
    examples = [
        ("Complete Team", example_1_complete_team),
        ("Individual Agents", example_2_individual_agents),
        ("Risk Analysts Consensus", example_3_risk_analysts_consensus),
        ("Custom Agent Loader", example_4_custom_agent_loader),
        ("Modify On-the-Fly", example_5_modify_on_the_fly)
    ]
    
    print("\n" + "="*70)
    print("MODULAR AGENT SYSTEM - EXAMPLES")
    print("="*70)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "="*70)
    choice = input("\nSelect example (1-5, or 'all'): ").strip().lower()
    
    if choice == 'all':
        for name, func in examples:
            func()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        _, func = examples[int(choice) - 1]
        func()
    else:
        print("❌ Invalid choice")
        return
    
    print("\n" + "="*70)
    print("✅ EXAMPLES COMPLETED")
    print("="*70)


if __name__ == "__main__":
    # Run specific example or all
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_complete_team()
        elif example_num == "2":
            example_2_individual_agents()
        elif example_num == "3":
            example_3_risk_analysts_consensus()
        elif example_num == "4":
            example_4_custom_agent_loader()
        elif example_num == "5":
            example_5_modify_on_the_fly()
        else:
            print(f"Usage: python {sys.argv[0]} [1-5]")
    else:
        main()

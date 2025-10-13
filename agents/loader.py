"""
Agent Configuration Loader
===========================
Loads agent configurations from YAML files and creates Agent instances dynamically.
Supports modular agent architecture with separate config files.

Usage:
    from agents.loader import AgentLoader
    
    loader = AgentLoader()
    researcher = loader.load_agent("market_researcher")
    team = loader.load_team()
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from agno.agent import Agent
from agno.team import Team
from agno.models.openrouter import OpenRouter
from agno.models.deepseek import DeepSeek
from agno.tools.yfinance import YFinanceTools
from agno.tools.serper import SerperTools


class AgentLoader:
    """Load agent configurations from YAML files"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the agent loader
        
        Args:
            config_dir: Path to directory containing YAML configs
                       If None, uses default 'agents/' directory
        """
        if config_dir is None:
            # Default to agents/ directory relative to this file
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
        
        if not self.config_dir.exists():
            raise ValueError(f"Config directory not found: {self.config_dir}")
        
        print(f"[AgentLoader] Initialized with config dir: {self.config_dir}")
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get_nested_config(self, config: Dict, key_path: str) -> Dict[str, Any]:
        """
        Get nested configuration using dot notation
        
        Example:
            get_nested_config(config, "agents.conservative")
        """
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if key not in current:
                raise KeyError(f"Key not found in config: {key_path}")
            current = current[key]
        
        return current
    
    def create_model(self, model_config: Dict[str, Any], use_openrouter: bool = True) -> Any:
        """
        Create model instance from configuration
        
        Args:
            model_config: Model configuration dict
            use_openrouter: Whether to use OpenRouter (if available)
        
        Returns:
            Model instance (OpenRouter or DeepSeek)
        """
        provider = model_config.get('provider', 'deepseek')
        model_id = model_config.get('model_id', 'deepseek-chat')
        
        # Check if we should use OpenRouter
        if provider == 'openrouter' and use_openrouter:
            try:
                model = OpenRouter(id=model_id)
                print(f"    ✓ Using OpenRouter model: {model_id}")
                return model
            except Exception as e:
                print(f"    ⚠️ OpenRouter failed, falling back to DeepSeek: {e}")
        
        # Fallback or default to DeepSeek
        fallback_id = model_config.get('fallback', {}).get('model_id', 'deepseek-chat')
        model = DeepSeek(id=fallback_id)
        print(f"    ✓ Using DeepSeek model: {fallback_id}")
        return model
    
    def create_tools(self, tools_config: Dict[str, Any]) -> List[Any]:
        """
        Create tool instances from configuration
        
        Args:
            tools_config: Tools configuration dict
        
        Returns:
            List of tool instances
        """
        tools = []
        
        if not tools_config.get('enabled', True):
            return tools
        
        # YFinance tools
        if 'yfinance' in tools_config:
            yf_config = tools_config['yfinance']
            if yf_config.get('enabled', True):
                if yf_config.get('include_all', False):
                    tools.append(YFinanceTools())
                    print("    ✓ Added YFinanceTools (all)")
                elif 'include_tools' in yf_config:
                    tools.append(YFinanceTools(
                        include_tools=yf_config['include_tools']
                    ))
                    print(f"    ✓ Added YFinanceTools ({len(yf_config['include_tools'])} tools)")
        
        # Serper tools (web search)
        if 'serper' in tools_config:
            serper_config = tools_config['serper']
            if serper_config.get('enabled', False):
                try:
                    tools.append(SerperTools())
                    print("    ✓ Added SerperTools (web search)")
                except Exception as e:
                    if serper_config.get('required', False):
                        raise
                    print(f"    ⚠️ SerperTools not available: {e}")
        
        return tools
    
    def build_instructions(self, instructions_config: Dict[str, Any]) -> List[str]:
        """
        Build instruction list from configuration
        
        Args:
            instructions_config: Instructions configuration dict
        
        Returns:
            List of instruction strings
        """
        instructions = []
        
        # Add critical rules first
        if 'critical_rules' in instructions_config:
            for rule in instructions_config['critical_rules']:
                instructions.append(rule)
        
        # Add expertise/profile
        if 'expertise' in instructions_config:
            for item in instructions_config['expertise']:
                instructions.append(item)
        
        if 'profile' in instructions_config:
            profile = instructions_config['profile']
            if isinstance(profile, dict):
                # Format profile as instructions
                if 'name' in profile:
                    instructions.append(f"Eres un analista de riesgo {profile['name']}")
                if 'philosophy' in profile:
                    instructions.append(f"FILOSOFÍA: {profile['philosophy']}")
                # Add other profile fields...
            else:
                for item in profile:
                    instructions.append(item)
        
        # Add tool usage instructions
        if 'tool_usage' in instructions_config:
            instructions.append("USA las herramientas disponibles:")
            for tool_name, tool_instructions in instructions_config['tool_usage'].items():
                for instr in tool_instructions:
                    instructions.append(f"  - {tool_name}: {instr}")
        
        # Add focus areas
        if 'focus_areas' in instructions_config:
            for area in instructions_config['focus_areas']:
                instructions.append(area)
        
        # Add remaining instruction fields
        for key, value in instructions_config.items():
            if key not in ['critical_rules', 'expertise', 'profile', 'tool_usage', 
                          'focus_areas', 'language', 'search_strategy']:
                if isinstance(value, list):
                    instructions.extend(value)
                elif isinstance(value, str):
                    instructions.append(value)
        
        return instructions
    
    def load_agent(self, 
                   agent_id: str, 
                   config_file: Optional[str] = None,
                   config_key: Optional[str] = None,
                   use_openrouter: bool = True,
                   portfolio_summary: Optional[Dict] = None) -> Agent:
        """
        Load a single agent from configuration
        
        Args:
            agent_id: Agent identifier
            config_file: YAML config filename (optional if using default)
            config_key: Dot-notation path for nested configs (e.g., "agents.conservative")
            use_openrouter: Whether to use OpenRouter models
            portfolio_summary: Current portfolio summary for context
        
        Returns:
            Configured Agent instance
        """
        # Load config file
        if config_file is None:
            config_file = f"{agent_id}.yaml"
        
        config = self.load_yaml(config_file)
        
        # Get nested config if specified
        if config_key:
            config = self.get_nested_config(config, config_key)
        
        print(f"\n[Creating Agent: {config['name']}]")
        
        # Create model
        model = self.create_model(config['model'], use_openrouter)
        
        # Create tools
        tools = []
        if 'tools' in config:
            tools = self.create_tools(config['tools'])
        
        # Build instructions
        instructions = self.build_instructions(config['instructions'])
        
        # Add portfolio context if provided
        if portfolio_summary and config.get('output', {}).get('include_portfolio_context', False):
            instructions.append("")
            instructions.append(f"ESTADO ACTUAL DEL PORTAFOLIO:")
            instructions.append(f"- Efectivo: ${portfolio_summary.get('cash', 0):.2f}")
            instructions.append(f"- Equity Total: ${portfolio_summary.get('total_equity', 0):.2f}")
            instructions.append(f"- ROI: {portfolio_summary.get('roi', 0):.2f}%")
        
        # Create agent
        agent = Agent(
            name=config['name'],
            role=config['role'],
            model=model,
            tools=tools if tools else None,
            instructions=instructions,
            markdown=config.get('output', {}).get('markdown', True)
        )
        
        print(f"  ✅ Agent created successfully")
        return agent
    
    def load_team(self, 
                  use_openrouter: bool = True,
                  portfolio_summary: Optional[Dict] = None) -> Team:
        """
        Load complete team from team_config.yaml
        
        Args:
            use_openrouter: Whether to use OpenRouter models
            portfolio_summary: Current portfolio summary for context
        
        Returns:
            Configured Team instance with all agents
        """
        print("\n" + "="*70)
        print("LOADING TRADING TEAM FROM YAML CONFIGURATIONS")
        print("="*70)
        
        # Load team config
        team_config = self.load_yaml('team_config.yaml')
        
        # Load all agents
        agents = []
        for member in team_config['team']['members']:
            agent_id = member['id']
            config_file = member['config_file']
            config_key = member.get('config_key')
            
            try:
                agent = self.load_agent(
                    agent_id=agent_id,
                    config_file=config_file,
                    config_key=config_key,
                    use_openrouter=use_openrouter,
                    portfolio_summary=portfolio_summary
                )
                agents.append(agent)
            except Exception as e:
                if member.get('required', True):
                    raise RuntimeError(f"Failed to load required agent {agent_id}: {e}")
                else:
                    print(f"⚠️ Optional agent {agent_id} failed to load: {e}")
        
        # Build team instructions
        team_instructions = []
        for instr in team_config['team']['instructions']['critical_rules']:
            team_instructions.append(instr)
        
        team_instructions.append("")
        team_instructions.append("FLUJO DE TRABAJO SECUENCIAL - 9 AGENTES:")
        team_instructions.append("")
        
        for stage_name, stage_desc in team_config['team']['instructions']['workflow_description'].items():
            team_instructions.append(f"{stage_name.replace('stage_', '')}. {stage_desc}")
        
        team_instructions.append("")
        for phil in team_config['team']['instructions']['philosophy']:
            team_instructions.append(phil)
        
        # Create team
        team = Team(
            name=team_config['team']['name'],
            members=agents,
            instructions=team_instructions,
            markdown=team_config.get('output', {}).get('markdown', True)
        )
        
        print("\n" + "="*70)
        print(f"✅ TEAM LOADED SUCCESSFULLY - {len(agents)} AGENTS")
        print("="*70 + "\n")
        
        return team


# Convenience functions for quick loading
def load_market_researcher(use_openrouter: bool = False) -> Agent:
    """Quick loader for Market Researcher agent"""
    loader = AgentLoader()
    return loader.load_agent("market_researcher", use_openrouter=use_openrouter)


def load_risk_analysts(use_openrouter: bool = False, 
                       portfolio_summary: Optional[Dict] = None) -> List[Agent]:
    """Quick loader for all 3 Risk Analyst agents"""
    loader = AgentLoader()
    return [
        loader.load_agent("risk_conservative", "risk_analysts.yaml", 
                         "agents.conservative", use_openrouter, portfolio_summary),
        loader.load_agent("risk_moderate", "risk_analysts.yaml", 
                         "agents.moderate", use_openrouter, portfolio_summary),
        loader.load_agent("risk_aggressive", "risk_analysts.yaml", 
                         "agents.aggressive", use_openrouter, portfolio_summary)
    ]


def load_trading_strategists(use_openrouter: bool = False) -> List[Agent]:
    """Quick loader for all 3 Trading Strategist agents"""
    loader = AgentLoader()
    return [
        loader.load_agent("strategy_technical", "trading_strategists.yaml", 
                         "agents.technical", use_openrouter),
        loader.load_agent("strategy_fundamental", "trading_strategists.yaml", 
                         "agents.fundamental", use_openrouter),
        loader.load_agent("strategy_momentum", "trading_strategists.yaml", 
                         "agents.momentum", use_openrouter)
    ]


def load_portfolio_manager(use_openrouter: bool = True,
                           portfolio_summary: Optional[Dict] = None) -> Agent:
    """Quick loader for Portfolio Manager agent"""
    loader = AgentLoader()
    return loader.load_agent("portfolio_manager", use_openrouter=use_openrouter,
                            portfolio_summary=portfolio_summary)


def load_daily_reporter(use_openrouter: bool = True,
                       portfolio_summary: Optional[Dict] = None) -> Agent:
    """Quick loader for Daily Reporter agent"""
    loader = AgentLoader()
    return loader.load_agent("daily_reporter", use_openrouter=use_openrouter,
                            portfolio_summary=portfolio_summary)


def load_advanced_reporter(use_openrouter: bool = True) -> Agent:
    """
    Quick loader for Advanced Analytics Reporter agent (FASE 2)
    
    This agent generates comprehensive HTML reports with:
    - Advanced metrics (Sharpe, Sortino, Beta, Alpha, Max Drawdown)
    - Interactive Plotly charts (6 visualizations)
    - AI-powered insights using DeepSeek
    - Dark mode toggle
    - Professional HTML output
    
    Args:
        use_openrouter: Whether to use OpenRouter (recommended for DeepSeek)
    
    Returns:
        Configured Advanced Reporter agent
    """
    loader = AgentLoader()
    return loader.load_agent("advanced_reporter", use_openrouter=use_openrouter)


def load_complete_team(use_openrouter: bool = True,
                      portfolio_summary: Optional[Dict] = None) -> Team:
    """Quick loader for complete trading team"""
    loader = AgentLoader()
    return loader.load_team(use_openrouter=use_openrouter,
                           portfolio_summary=portfolio_summary)
